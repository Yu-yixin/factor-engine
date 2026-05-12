from __future__ import annotations

import argparse
import itertools
import os
import statistics
from pathlib import Path
from typing import Any

from performance_truth_common import (
    FIELD_NOT_AVAILABLE,
    LATEST_ROOT,
    build_synthetic_frame,
    correctness_smoke_passed,
    evaluate_profiled,
    fmt,
    infer_backend,
    route_groups,
    sum_batch_field,
    write_artifact,
)
from factor_engine.native_positional import native_available, native_requested


OPERATORS = [
    "ts_mean",
    "ts_std",
    "ts_sum",
    "ts_min",
    "ts_max",
    "ts_rank",
    "corr",
    "cov",
    "skew",
    "kurt",
    "argmax",
    "argmin",
]


def expression_for(operator: str, window: int, index: int = 0) -> str:
    left = "close" if index % 2 == 0 else "open"
    right = "volume" if index % 2 == 0 else "open"
    if operator in {"corr", "cov"}:
        return f"{operator}({left}, {right}, {window})"
    return f"{operator}({left}, {window})"


def build_expressions(operator: str, window: int, mode: str, expression_count: int) -> list[tuple[str, str]]:
    if mode == "single":
        return [(f"{operator}_{window}", expression_for(operator, window))]
    if mode == "repeated":
        return [
            (f"{operator}_{window}_{index + 1:02d}", expression_for(operator, window, index))
            for index in range(expression_count)
        ]
    if mode == "mixed":
        operators = OPERATORS
        return [
            (
                f"mixed_{index + 1:02d}_{operators[index % len(operators)]}_{window}",
                expression_for(operators[index % len(operators)], window, index),
            )
            for index in range(expression_count)
        ]
    raise ValueError(f"Unsupported expression-count mode: {mode}")


def parse_csv(raw: str, cast: Any) -> list[Any]:
    return [cast(part.strip()) for part in raw.split(",") if part.strip()]


def _stats(times: list[float]) -> dict[str, float]:
    mean = statistics.fmean(times)
    stdev = statistics.stdev(times) if len(times) > 1 else 0.0
    return {
        "min_time_ms": min(times),
        "median_time_ms": statistics.median(times),
        "max_time_ms": max(times),
        "mean_time_ms": mean,
        "stdev_time_ms": stdev,
        "coefficient_of_variation": stdev / mean if mean else 0.0,
    }


def _positional_backend_details(operator: str, phases: list[dict[str, Any]]) -> dict[str, Any]:
    if operator not in {"argmax", "argmin"}:
        return {
            "native_path_used": FIELD_NOT_AVAILABLE,
            "python_fallback_used": FIELD_NOT_AVAILABLE,
            "env_flags_required": FIELD_NOT_AVAILABLE,
            "benchmark_path_tested": FIELD_NOT_AVAILABLE,
        }
    native_used = any(bool(item.get("native_kernel_used")) for item in phases)
    fallback_used = any(bool(item.get("python_kernel_used")) for item in phases)
    if native_used:
        tested = "native"
    elif fallback_used:
        tested = "fallback"
    else:
        tested = "unknown"
    return {
        "native_path_used": native_used,
        "python_fallback_used": fallback_used,
        "native_available": native_available(),
        "native_requested": native_requested(),
        "env_flags_required": (
            "FACTOR_ENGINE_POSITIONAL_KERNEL=native or auto; optional "
            "FACTOR_ENGINE_POSITIONAL_PARALLEL=0/1"
        ),
        "benchmark_path_tested": tested,
        "factor_engine_positional_kernel": os.environ.get(
            "FACTOR_ENGINE_POSITIONAL_KERNEL",
            "",
        ),
        "factor_engine_positional_parallel": os.environ.get(
            "FACTOR_ENGINE_POSITIONAL_PARALLEL",
            "",
        ),
    }


def run_case_once(
    *,
    operator: str,
    window: int,
    row_count: int,
    code_count: int,
    null_rate: float,
    mode: str,
    expression_count: int,
    output_root: Path,
    run_index: int = 0,
) -> dict[str, Any]:
    df = build_synthetic_frame(row_count=row_count, code_count=code_count, null_rate=null_rate)
    expressions = build_expressions(operator, window, mode, expression_count)
    case_name = f"{operator}_w{window}_n{str(null_rate).replace('.', 'p')}_{mode}_{len(expressions)}"
    profile_dir = output_root / case_name / f"run_{run_index:02d}"
    result, summary, batches, phases, elapsed_ms = evaluate_profiled(
        expressions=expressions,
        df=df,
        profile_dir=profile_dir,
        benchmark_name=f"performance_truth_rolling_{case_name}",
    )
    output_names = [name for name, _expr in expressions]
    return {
        "case": case_name,
        "operator": operator if mode != "mixed" else "mixed",
        "window": window,
        "row_count": row_count,
        "code_count": code_count,
        "null_rate": null_rate,
        "expression_count": len(expressions),
        "expression_count_mode": mode,
        "total_time_ms": float(summary.get("total_time_sec", elapsed_ms / 1000)) * 1000,
        "prepare_sort_time_ms": sum_batch_field(batches, "prepare_sort_time_ms"),
        "ordered_eval_time_ms": sum_batch_field(batches, "compiled_output_eval_time_ms"),
        "restore_time_ms": sum_batch_field(batches, "restore_time_ms"),
        "output_attach_time_ms": sum_batch_field(batches, "append_time_ms"),
        "peak_rss_mb": summary.get("peak_rss_mb", FIELD_NOT_AVAILABLE),
        "peak_frame_col_count": summary.get("peak_frame_col_count", FIELD_NOT_AVAILABLE),
        "peak_stage_col_count": summary.get("peak_stage_col_count", FIELD_NOT_AVAILABLE),
        "peak_output_col_count": summary.get("peak_output_col_count", FIELD_NOT_AVAILABLE),
        "backend_path": infer_backend(operator, phases, summary),
        "output_shape": [result.height, result.width],
        "correctness_smoke_passed": correctness_smoke_passed(result, df, output_names),
        "route_groups": route_groups(expressions, df),
        "profile_dir": str(profile_dir),
        "notes": "" if mode != "mixed" else "mixed rolling batch",
        **_positional_backend_details(operator, phases),
    }


def run_case(
    *,
    operator: str,
    window: int,
    row_count: int,
    code_count: int,
    null_rate: float,
    mode: str,
    expression_count: int,
    output_root: Path,
    runs: int,
    warmup_runs: int,
) -> dict[str, Any]:
    warmup_samples: list[dict[str, Any]] = []
    for warmup_index in range(warmup_runs):
        warmup_samples.append(
            run_case_once(
                operator=operator,
                window=window,
                row_count=row_count,
                code_count=code_count,
                null_rate=null_rate,
                mode=mode,
                expression_count=expression_count,
                output_root=output_root / "_warmup",
                run_index=warmup_index + 1,
            )
        )

    samples = [
        run_case_once(
            operator=operator,
            window=window,
            row_count=row_count,
            code_count=code_count,
            null_rate=null_rate,
            mode=mode,
            expression_count=expression_count,
            output_root=output_root,
            run_index=run_index + 1,
        )
        for run_index in range(runs)
    ]
    times = [float(sample["total_time_ms"]) for sample in samples]
    row = dict(samples[len(samples) // 2])
    row.update(_stats(times))
    row["total_time_ms"] = row["median_time_ms"]
    row["run_time_ms"] = times
    row["runs"] = runs
    row["warmup_runs"] = warmup_runs
    row["warmup_time_ms"] = [float(sample["total_time_ms"]) for sample in warmup_samples]
    row["profile_dir"] = str(output_root / row["case"])
    return row


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark per-operator rolling/window cost.")
    parser.add_argument("--row-count", default="12_000")
    parser.add_argument("--code-count", default="120")
    parser.add_argument("--windows", default="5,20,60,120")
    parser.add_argument("--null-rates", default="0.0,0.01,0.10")
    parser.add_argument("--operators", default=",".join(OPERATORS))
    parser.add_argument("--modes", default="single,repeated,mixed")
    parser.add_argument("--expression-count", type=int, default=8)
    parser.add_argument("--repeat-count", type=int, default=None)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--warmup-runs", type=int, default=0)
    parser.add_argument("--output-report", type=Path, default=None)
    parser.add_argument("--quick", action="store_true", help="Run a small documented scale.")
    parser.add_argument("--output", type=Path, default=LATEST_ROOT / "rolling_operators")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    row_counts = parse_csv(args.row_count, lambda value: int(value.replace("_", "")))
    code_counts = parse_csv(args.code_count, lambda value: int(value.replace("_", "")))
    windows = parse_csv(args.windows, int)
    null_rates = parse_csv(args.null_rates, float)
    operators = parse_csv(args.operators, str)
    modes = parse_csv(args.modes, str)
    expression_count = args.repeat_count if args.repeat_count is not None else args.expression_count
    if args.quick:
        row_counts = [min(row_counts[0], 4_800)]
        code_counts = [min(code_counts[0], 80)]
        windows = windows[:2]
        null_rates = null_rates[:2]
        modes = modes[:2]

    rows: list[dict[str, Any]] = []
    args.output.mkdir(parents=True, exist_ok=True)
    for row_count, code_count, operator, window, null_rate, mode in itertools.product(
        row_counts,
        code_counts,
        operators,
        windows,
        null_rates,
        modes,
    ):
        row = run_case(
            operator=operator,
            window=window,
            row_count=row_count,
            code_count=code_count,
            null_rate=null_rate,
            mode=mode,
            expression_count=expression_count,
            output_root=args.output,
            runs=args.runs,
            warmup_runs=args.warmup_runs,
        )
        rows.append(row)
        print(
            f"{row['case']} rows={row_count} codes={code_count}: "
            f"median={fmt(row['median_time_ms'])} ms cv={fmt(row['coefficient_of_variation'])} "
            f"rss={fmt(row['peak_rss_mb'], 2)} MB backend={row['backend_path']}"
        )

    ranked_rows = sorted(rows, key=lambda item: float(item["median_time_ms"]), reverse=True)
    for rank, row in enumerate(ranked_rows, start=1):
        row["rank_by_median"] = rank

    artifact_name = "scaleup_rolling_operators.json" if args.output_report is not None else "rolling_operators.json"
    artifact = write_artifact(
        artifact_name,
        rows,
        update_baseline=args.output_report is None,
    )
    print(f"Saved rolling benchmark artifact to {artifact}")
    if args.output_report is not None:
        from performance_truth_common import render_scaleup_report

        report_path = render_scaleup_report(rows, args.output_report)
        print(f"Saved scale-up report to {report_path}")


if __name__ == "__main__":
    main()
