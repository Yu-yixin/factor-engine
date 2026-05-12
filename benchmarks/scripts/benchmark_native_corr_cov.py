from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import statistics
import sys
import time

import polars as pl

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from factor_engine.native_corr_cov import (  # noqa: E402
    evaluate_native_corr_cov_kernel,
    native_corr_cov_available,
)


def _make_frame(rows: int, codes: int, null_rate: float) -> pl.DataFrame:
    code_values = [f"C{i % codes:04d}" for i in range(rows)]
    time_values = [i // codes for i in range(rows)]
    x = []
    y = []
    null_every = int(1 / null_rate) if null_rate > 0 else 0
    for i in range(rows):
        x_value = math.sin(i * 0.013) + (i % 17) * 0.1
        y_value = math.cos(i * 0.017) + (i % 23) * 0.07
        if null_every and i % null_every == 0:
            x_value = None
        if null_every and (i + 7) % null_every == 0:
            y_value = None
        x.append(x_value)
        y.append(y_value)
    return pl.DataFrame({"time": time_values, "code": code_values, "x": x, "y": y}).sort(
        ["code", "time"]
    )


def _time_call(fn, repeats: int) -> list[float]:
    timings = []
    for _ in range(repeats):
        started = time.perf_counter()
        fn()
        timings.append((time.perf_counter() - started) * 1000)
    return timings


def _polars_case(df: pl.DataFrame, mode: str, window: int):
    expr = (
        pl.rolling_corr(pl.col("x"), pl.col("y"), window_size=window, min_samples=2)
        if mode == "corr"
        else pl.rolling_cov(pl.col("x"), pl.col("y"), window_size=window, min_samples=2)
    )
    return df.with_columns(expr.over("code").alias("result"))


def _native_case(df: pl.DataFrame, mode: str, window: int):
    return evaluate_native_corr_cov_kernel(df["x"], df["y"], df["code"], window, mode=mode)


def _summarize(values: list[float]) -> dict[str, float]:
    median = statistics.median(values)
    mean = statistics.fmean(values)
    stdev = statistics.pstdev(values) if len(values) > 1 else 0.0
    return {
        "median_ms": median,
        "mean_ms": mean,
        "cv": stdev / mean if mean else 0.0,
    }


def run(repeats: int, reduced: bool) -> dict:
    matrix = [
        (24_000, 40, 5, 0.0, "corr"),
        (24_000, 40, 20, 0.01, "cov"),
        (24_000, 250, 60, 0.10, "corr"),
    ]
    full_matrix_marked_not_run = True
    if not reduced:
        matrix.extend(
            [
                (120_000, 250, 20, 0.01, "corr"),
                (120_000, 250, 120, 0.10, "cov"),
            ]
        )
        full_matrix_marked_not_run = True

    native_available = native_corr_cov_available()
    os.environ["FACTOR_ENGINE_NATIVE_CORR_COV"] = "1"
    cases = []
    for rows, codes, window, null_rate, mode in matrix:
        df = _make_frame(rows, codes, null_rate)
        polars_timings = _time_call(lambda: _polars_case(df, mode, window), repeats)
        native_result = _native_case(df, mode, window) if native_available else None
        if native_result is None:
            native_timings = []
            native_used = False
            speedup = None
        else:
            native_timings = _time_call(lambda: _native_case(df, mode, window), repeats)
            native_used = True
            speedup = statistics.median(polars_timings) / statistics.median(native_timings)

        cases.append(
            {
                "rows": rows,
                "codes": codes,
                "window": window,
                "null_rate": null_rate,
                "mode": mode,
                "polars": _summarize(polars_timings),
                "native": _summarize(native_timings) if native_timings else None,
                "native_used": native_used,
                "speedup": speedup,
                "status": "RUN" if native_used else "NOT_RUN",
                "fallback_reason": "" if native_used else "native extension unavailable or kernel failed",
            }
        )

    run_cases = [case for case in cases if case["native_used"]]
    if not run_cases:
        decision = "REJECT"
        reason = "No native run completed; prototype remains opt-in and unaccepted."
    else:
        median_speedup = statistics.median(case["speedup"] for case in run_cases)
        worst_cv = max(case["native"]["cv"] for case in run_cases)
        decision = "ACCEPT" if median_speedup >= 1.25 and worst_cv <= 0.15 else "REJECT"
        reason = f"median_speedup={median_speedup:.3f}, worst_native_cv={worst_cv:.3f}"

    return {
        "benchmark": "native_corr_cov_ab",
        "repeats": repeats,
        "decision": decision,
        "decision_reason": reason,
        "full_matrix": "NOT_RUN" if full_matrix_marked_not_run else "RUN",
        "cases": cases,
    }


def write_report(result: dict) -> None:
    artifacts = REPO_ROOT / "benchmarks" / "artifacts" / "native_corr_cov_ab.json"
    report = REPO_ROOT / "benchmarks" / "reports" / "native_corr_cov_ab.md"
    artifacts.write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = [
        "# Native corr/cov A/B Report",
        "",
        f"Decision: `{result['decision']}`",
        "",
        f"Reason: {result['decision_reason']}",
        "",
        f"Full requested matrix: `{result['full_matrix']}`. Reduced scale is documented here when used.",
        "",
        "| rows | codes | window | null_rate | mode | native_used | polars median ms | native median ms | speedup | status |",
        "| ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for case in result["cases"]:
        native = case["native"] or {}
        speedup = "" if case["speedup"] is None else f"{case['speedup']:.3f}"
        lines.append(
            "| {rows} | {codes} | {window} | {null_rate} | {mode} | {native_used} | "
            "{polars:.3f} | {native_ms} | {speedup} | {status} |".format(
                rows=case["rows"],
                codes=case["codes"],
                window=case["window"],
                null_rate=case["null_rate"],
                mode=case["mode"],
                native_used=case["native_used"],
                polars=case["polars"]["median_ms"],
                native_ms="" if not native else f"{native['median_ms']:.3f}",
                speedup=speedup,
                status=case["status"],
            )
        )
    lines.extend(
        [
            "",
            "Acceptance rule: correctness must pass, median speedup must be at least 1.25x, CV must be at most 0.15, peak RSS must not materially regress, and fallback must be safe.",
            "",
            "This report uses total wall time for each callable path. Kernel-only time is not treated as sufficient evidence.",
        ]
    )
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    result = run(repeats=args.repeats, reduced=not args.full)
    write_report(result)
    print(json.dumps({"decision": result["decision"], "report": "benchmarks/reports/native_corr_cov_ab.md"}))


if __name__ == "__main__":
    main()
