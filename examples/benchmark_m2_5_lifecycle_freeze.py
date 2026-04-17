from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import polars as pl
from polars.testing import assert_frame_equal

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from factor_engine.engine import FactorEngine  # noqa: E402


STANDARD_NESTED_MISS_REASONS = {
    "not_nested",
    "unsupported_shape",
    "has_blocker",
    "output_pinned",
    "native_pinned",
    "non_helper_consumer",
    "children_not_ended",
    "safe_step_mismatch",
    "not_in_frame",
    "live_consumer_detected",
    "already_dropped",
    "mode_disabled",
}


@dataclass(frozen=True)
class LifecycleModeSpec:
    name: str
    lifecycle_mode: str
    helper_lifecycle_mode: str


MODES = (
    LifecycleModeSpec("off", "off", "off"),
    LifecycleModeSpec("first_wave", "first_wave", "first_wave"),
    LifecycleModeSpec("second_wave_nested", "first_wave", "second_wave_nested"),
)


def repeated_terms(term: str, count: int) -> str:
    return " + ".join([term] * count)


def value_workloads() -> dict[str, list[tuple[str, str]]]:
    return {
        "repeated_heavy": [("repeated_heavy", repeated_terms("ts_rank(close, 10)", 2))],
        "multi_shared_nodes": [
            (
                "multi_shared_nodes",
                "ts_rank(close, 10) + ts_rank(close, 10) + "
                "ts_rank(open, 10) + ts_rank(open, 10)",
            )
        ],
        "partial_reuse": [
            ("partial_a", "ts_mean(close, 10) + 1"),
            ("partial_b", "ts_rank(ts_mean(close, 10), 10)"),
        ],
        "pure_nested_chain": [
            (
                "pure_nested_chain",
                "ts_rank(ts_mean(close, 10), 10) + ts_rank(ts_mean(close, 10), 10)",
            )
        ],
    }


def rejection_cases() -> dict[str, list[tuple[str, str]]]:
    return {
        "shared_inner": [
            (
                "shared_inner",
                "ts_rank(ts_mean(close, 10), 10) + ts_std(ts_mean(close, 10), 10)",
            )
        ],
        "non_helper_downstream": [
            ("direct", "ts_mean(close, 10) + 1"),
            ("nested", "ts_rank(ts_mean(close, 10), 10)"),
        ],
        "output_pinned": [
            ("pinned", "ts_mean(close, 10)"),
            (
                "nested",
                "ts_rank(ts_mean(close, 10), 10) + ts_rank(ts_mean(close, 10), 10)",
            ),
        ],
        "native_heavy": [("native_heavy", "argmax(close, 10) + argmax(close, 10)")],
        "multi_child": [
            (
                "multi_child",
                "ts_rank(ts_mean(close, 10), 10) + ts_rank(ts_mean(close, 10), 10) + "
                "ts_std(ts_mean(close, 10), 10) + ts_std(ts_mean(close, 10), 10)",
            )
        ],
    }


def load_dataframe(args: argparse.Namespace) -> pl.DataFrame:
    scan = pl.scan_parquet(str(args.data))
    if args.rows > 0:
        scan = scan.limit(args.rows)
    return scan.collect()


def resolve_code_col(args: argparse.Namespace, df: pl.DataFrame) -> str:
    if args.code_col in df.columns:
        return args.code_col
    if args.code_col == "code" and "ths_code" in df.columns:
        return "ths_code"
    raise ValueError(
        f"code column '{args.code_col}' not found. Available columns: {', '.join(df.columns)}"
    )


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def run_profile(
    *,
    df: pl.DataFrame,
    expressions: list[tuple[str, str]],
    profile_dir: Path,
    benchmark_name: str,
    mode: LifecycleModeSpec,
    data_name: str,
    time_col: str,
    code_col: str,
) -> tuple[pl.DataFrame, dict[str, Any], list[dict[str, Any]]]:
    profile_dir.mkdir(parents=True, exist_ok=True)
    result = FactorEngine(time_col=time_col, code_col=code_col).evaluate_many(
        expressions,
        df,
        profiling=True,
        dag_cse=True,
        lifecycle_mode=mode.lifecycle_mode,
        helper_lifecycle_mode=mode.helper_lifecycle_mode,
        profile_output_dir=profile_dir,
        benchmark_name=benchmark_name,
        dataset_name=data_name,
    )
    return (
        result,
        read_json(profile_dir / "latest_run.json"),
        read_jsonl(profile_dir / "latest_node_execution_details.jsonl"),
    )


def pct_reduction(before: float, after: float) -> float:
    if before <= 0:
        return 0.0
    return max(0.0, (before - after) / before * 100.0)


def pct_delta(before: float, after: float) -> float:
    if before <= 0:
        return 0.0
    return (after - before) / before * 100.0


def nested_miss_reasons(node_details: list[dict[str, Any]]) -> list[str]:
    reasons = []
    for detail in node_details:
        reason = detail.get("nested_helper_miss_reason", "")
        if reason:
            reasons.append(str(reason))
    return sorted(set(reasons))


def run_value_confirmation(
    *,
    df: pl.DataFrame,
    output_root: Path,
    data_name: str,
    time_col: str,
    code_col: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    failures: list[str] = []
    for workload, expressions in value_workloads().items():
        baseline_result: pl.DataFrame | None = None
        for mode in MODES:
            profile_dir = output_root / "value_confirmation" / workload / mode.name
            result, run, node_details = run_profile(
                df=df,
                expressions=expressions,
                profile_dir=profile_dir,
                benchmark_name=f"m2_5_{workload}_{mode.name}",
                mode=mode,
                data_name=data_name,
                time_col=time_col,
                code_col=code_col,
            )
            if baseline_result is None:
                baseline_result = result
            else:
                try:
                    assert_frame_equal(result, baseline_result)
                except AssertionError as exc:
                    failures.append(f"{workload}:{mode.name}:result_mismatch:{exc}")
            rows.append(
                {
                    "workload": workload,
                    "mode": mode.name,
                    "sec": run.get("total_time_sec", 0.0),
                    "peak_live_bytes": run.get("peak_live_bytes_est_after_drop", 0),
                    "helper_bytes": run.get("helper_peak_live_bytes_after_drop", 0),
                    "helper_before_bytes": run.get("helper_peak_live_bytes_before_drop", 0),
                    "frame_width": run.get("helper_frame_width_after_drop", 0),
                    "nested_helper_dropped_count": run.get("nested_helper_dropped_count", 0),
                    "helper_dropped_count": run.get("helper_dropped_count", 0),
                    "helper_drop_miss_count": run.get("helper_drop_miss_count", 0),
                    "nested_helper_drop_missed_count": run.get(
                        "nested_helper_drop_missed_count",
                        0,
                    ),
                    "nested_miss_reasons": nested_miss_reasons(node_details),
                    "profile_dir": str(profile_dir),
                }
            )
    return rows, failures


def run_rejection_audit(
    *,
    df: pl.DataFrame,
    output_root: Path,
    data_name: str,
    time_col: str,
    code_col: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    mode = LifecycleModeSpec("second_wave_nested", "first_wave", "second_wave_nested")
    rows: list[dict[str, Any]] = []
    failures: list[str] = []
    for case_name, expressions in rejection_cases().items():
        profile_dir = output_root / "rejection_audit" / case_name
        result, run, node_details = run_profile(
            df=df,
            expressions=expressions,
            profile_dir=profile_dir,
            benchmark_name=f"m2_5_reject_{case_name}",
            mode=mode,
            data_name=data_name,
            time_col=time_col,
            code_col=code_col,
        )
        baseline = FactorEngine(time_col=time_col, code_col=code_col).evaluate_many(
            expressions,
            df,
            dag_cse=True,
            lifecycle_mode="off",
            helper_lifecycle_mode="off",
        )
        try:
            assert_frame_equal(result, baseline)
        except AssertionError as exc:
            failures.append(f"{case_name}:result_mismatch:{exc}")
        reasons = nested_miss_reasons(node_details)
        dropped = int(run.get("nested_helper_dropped_count", 0))
        missed = int(run.get("nested_helper_drop_missed_count", 0))
        standardized = bool(reasons) and all(reason in STANDARD_NESTED_MISS_REASONS for reason in reasons)
        passed = dropped == 0 and missed >= 1 and standardized
        if not passed:
            failures.append(
                f"{case_name}:expected_drop0_miss_reason got dropped={dropped} "
                f"missed={missed} reasons={reasons}"
            )
        rows.append(
            {
                "case": case_name,
                "expected": "miss",
                "passed": passed,
                "nested_helper_dropped_count": dropped,
                "nested_helper_drop_missed_count": missed,
                "standardized_reasons": reasons,
                "sec": run.get("total_time_sec", 0.0),
                "profile_dir": str(profile_dir),
            }
        )
    return rows, failures


def pick(rows: list[dict[str, Any]], workload: str, mode: str) -> dict[str, Any]:
    return next(row for row in rows if row["workload"] == workload and row["mode"] == mode)


def decide(value_rows: list[dict[str, Any]], rejection_failures: list[str], value_failures: list[str]) -> dict[str, Any]:
    nested_first = pick(value_rows, "pure_nested_chain", "first_wave")
    nested_second = pick(value_rows, "pure_nested_chain", "second_wave_nested")
    first_helper_before = float(nested_first.get("helper_bytes", 0))
    second_helper_after = float(nested_second.get("helper_bytes", 0))
    peak_memory_reduction = pct_reduction(first_helper_before, second_helper_after)
    performance_delta = pct_delta(
        float(nested_first.get("sec", 0.0)),
        float(nested_second.get("sec", 0.0)),
    )
    effective = int(nested_second.get("nested_helper_dropped_count", 0)) > 0
    if peak_memory_reduction >= 5.0:
        second_wave_decision = "KEEP"
    elif peak_memory_reduction >= 2.0 and performance_delta <= 5.0:
        second_wave_decision = "KEEP"
    else:
        second_wave_decision = "LOW_PRIORITY"
    first_wave_stable = not value_failures
    regression_detected = bool(value_failures or rejection_failures)
    rejection_audit_complete = not rejection_failures
    return {
        "lifecycle_status": {
            "first_wave_stable": first_wave_stable,
            "second_wave_nested_v1": True,
            "rejection_audit_complete": rejection_audit_complete,
            "regression_detected": regression_detected,
            "safe_to_freeze": (
                first_wave_stable and rejection_audit_complete and not regression_detected
            ),
        },
        "lifecycle_value": {
            "peak_memory_reduction": round(peak_memory_reduction, 3),
            "performance_delta": round(performance_delta, 3),
            "effective": effective,
            "second_wave_decision": second_wave_decision,
        },
    }


def m3_score(
    *,
    memory_reduction: float,
    frame_width_reduction: float,
    time_increase: float,
    w1: float = 0.5,
    w2: float = 0.3,
    w3: float = 0.2,
) -> float:
    return w1 * memory_reduction + w2 * frame_width_reduction - w3 * time_increase


def render_yaml(decision: dict[str, Any]) -> str:
    lines: list[str] = []
    for section, values in decision.items():
        lines.append(f"{section}:")
        for key, value in values.items():
            if isinstance(value, bool):
                rendered = "true" if value else "false"
            else:
                rendered = str(value)
            lines.append(f"  {key}: {rendered}")
    return "\n".join(lines) + "\n"


def render_report(
    *,
    value_rows: list[dict[str, Any]],
    rejection_rows: list[dict[str, Any]],
    decision: dict[str, Any],
    rows: int,
    data_name: str,
) -> str:
    lines = [
        "# M2.5 Lifecycle Freeze Validation",
        "",
        f"- data: `{data_name}`",
        f"- rows: `{rows}`",
        "",
        "## Lifecycle Status",
        "",
        "```yaml",
        render_yaml(decision).strip(),
        "```",
        "",
        "## Value Confirmation",
        "",
        "| workload | mode | sec | peak live bytes | helper bytes | frame width | nested dropped | helper dropped | helper misses | nested misses |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in value_rows:
        lines.append(
            f"| {row['workload']} | {row['mode']} | {float(row['sec']):.6f} | "
            f"{row['peak_live_bytes']} | {row['helper_bytes']} | {row['frame_width']} | "
            f"{row['nested_helper_dropped_count']} | {row['helper_dropped_count']} | "
            f"{row['helper_drop_miss_count']} | {row['nested_helper_drop_missed_count']} |"
        )
    lines.extend(
        [
            "",
            "## Rejection Audit",
            "",
            "| case | expected | passed | dropped | missed | reasons |",
            "| --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in rejection_rows:
        lines.append(
            f"| {row['case']} | {row['expected']} | {row['passed']} | "
            f"{row['nested_helper_dropped_count']} | "
            f"{row['nested_helper_drop_missed_count']} | "
            f"`{','.join(row['standardized_reasons'])}` |"
        )
    lines.extend(
        [
            "",
            "## M3.v1 Scoring Contract",
            "",
            "```text",
            "score = 0.5 * memory_reduction + 0.3 * frame_width_reduction - 0.2 * time_increase",
            "ACCEPT iff score > 0",
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run M2.5 lifecycle freeze validation.")
    parser.add_argument("--data", type=Path, default=PROJECT_ROOT / "data" / "data.parquet")
    parser.add_argument("--rows", type=int, default=0, help="0 means full input.")
    parser.add_argument("--code-col", default="code")
    parser.add_argument("--time-col", default="time")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "benchmarks" / "m2_5_lifecycle_freeze",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = load_dataframe(args)
    code_col = resolve_code_col(args, df)
    output_root = args.output
    shutil.rmtree(output_root, ignore_errors=True)
    output_root.mkdir(parents=True, exist_ok=True)

    value_rows, value_failures = run_value_confirmation(
        df=df,
        output_root=output_root,
        data_name=args.data.name,
        time_col=args.time_col,
        code_col=code_col,
    )
    rejection_rows, rejection_failures = run_rejection_audit(
        df=df,
        output_root=output_root,
        data_name=args.data.name,
        time_col=args.time_col,
        code_col=code_col,
    )
    decision = decide(value_rows, rejection_failures, value_failures)
    summary = {
        "rows": df.height,
        "data": args.data.name,
        "value_confirmation": value_rows,
        "rejection_audit": rejection_rows,
        "failures": value_failures + rejection_failures,
        "decision": decision,
        "m3_v1_score_contract": {
            "weights": {"memory_reduction": 0.5, "frame_width_reduction": 0.3, "time_increase": 0.2},
            "accept_if": "score > 0",
        },
    }
    (output_root / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_root / "decision.yaml").write_text(render_yaml(decision), encoding="utf-8")
    report = render_report(
        value_rows=value_rows,
        rejection_rows=rejection_rows,
        decision=decision,
        rows=df.height,
        data_name=args.data.name,
    )
    (output_root / "m2_5_lifecycle_freeze_report.md").write_text(report, encoding="utf-8")
    print(report)
    if summary["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
