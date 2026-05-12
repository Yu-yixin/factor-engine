from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from performance_truth_common import (
    FIELD_NOT_AVAILABLE,
    LATEST_ROOT,
    build_synthetic_frame,
    correctness_smoke_passed,
    evaluate_profiled,
    fmt,
    route_groups,
    sum_batch_field,
    write_artifact,
)


ATTACH_MODES = ["materialize", "finalize_select", "last_use_select"]


def rolling_expr(index: int) -> str:
    variants = [
        "ts_mean(close, 20)",
        "ts_std(close, 20)",
        "ts_sum(volume, 20)",
        "ts_min(open, 20)",
        "ts_max(close, 20)",
        "ts_rank(close, 20)",
        "corr(close, volume, 20)",
        "cov(open, volume, 20)",
        "skew(close, 20)",
        "kurt(close, 20)",
        "argmax(close, 20)",
        "argmin(open, 20)",
    ]
    return variants[index % len(variants)]


def case_expressions(case: str) -> list[tuple[str, str]]:
    if case == "narrow":
        return [(f"narrow_{index + 1:02d}", rolling_expr(index)) for index in range(5)]
    if case == "medium":
        return [(f"medium_{index + 1:02d}", rolling_expr(index)) for index in range(25)]
    if case == "wide":
        return [(f"wide_{index + 1:03d}", rolling_expr(index)) for index in range(100)]
    if case == "deep_chained":
        return [
            ("rank_mean_20", "rank(ts_mean(close, 20))"),
            ("zscore_mean_20", "zscore(ts_mean(close, 20))"),
            ("demean_mean_20", "demean(ts_mean(close, 20))"),
            ("ts_rank_mean_20", "ts_rank(ts_mean(close, 20), 20)"),
        ]
    raise ValueError(f"Unsupported case: {case}")


def parse_csv(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def run_case(
    *,
    case: str,
    attach_mode: str,
    row_count: int,
    code_count: int,
    null_rate: float,
    output_root: Path,
) -> dict[str, Any]:
    df = build_synthetic_frame(row_count=row_count, code_count=code_count, null_rate=null_rate)
    expressions = case_expressions(case)
    case_name = f"{case}_{attach_mode}"
    profile_dir = output_root / case_name
    result, summary, batches, _phases, elapsed_ms = evaluate_profiled(
        expressions=expressions,
        df=df,
        profile_dir=profile_dir,
        benchmark_name=f"performance_truth_finalize_{case_name}",
        output_attach_mode=attach_mode,
    )
    output_names = [name for name, _expr in expressions]
    return {
        "case": case,
        "attach_mode": attach_mode,
        "row_count": row_count,
        "code_count": code_count,
        "null_rate": null_rate,
        "expression_count": len(expressions),
        "total_time_ms": float(summary.get("total_time_sec", elapsed_ms / 1000)) * 1000,
        "ordered_eval_time_ms": sum_batch_field(batches, "compiled_output_eval_time_ms"),
        "restore_time_ms": sum_batch_field(batches, "restore_time_ms"),
        "finalize_select_time_ms": sum_batch_field(batches, "finalize_time_ms"),
        "output_attach_time_ms": sum_batch_field(batches, "append_time_ms"),
        "prepare_sort_time_ms": sum_batch_field(batches, "prepare_sort_time_ms"),
        "peak_frame_col_count": summary.get("peak_frame_col_count", FIELD_NOT_AVAILABLE),
        "peak_stage_col_count": summary.get("peak_stage_col_count", FIELD_NOT_AVAILABLE),
        "peak_output_col_count": summary.get("peak_output_col_count", FIELD_NOT_AVAILABLE),
        "peak_rss_mb": summary.get("peak_rss_mb", FIELD_NOT_AVAILABLE),
        "shared_node_count": summary.get("shared_node_count", FIELD_NOT_AVAILABLE),
        "native_heavy_node_count": summary.get("native_heavy_node_count", FIELD_NOT_AVAILABLE),
        "output_shape": [result.height, result.width],
        "correctness_smoke_passed": correctness_smoke_passed(result, df, output_names),
        "route_groups": route_groups(expressions, df),
        "profile_dir": str(profile_dir),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark ordered finalization and restore cost.")
    parser.add_argument("--row-count", type=int, default=12_000)
    parser.add_argument("--code-count", type=int, default=120)
    parser.add_argument("--null-rate", type=float, default=0.01)
    parser.add_argument("--cases", default="narrow,medium,wide,deep_chained")
    parser.add_argument("--attach-modes", default=",".join(ATTACH_MODES))
    parser.add_argument("--quick", action="store_true", help="Run a small documented scale.")
    parser.add_argument("--output", type=Path, default=LATEST_ROOT / "ordered_finalize_restore")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cases = parse_csv(args.cases)
    attach_modes = parse_csv(args.attach_modes)
    row_count = min(args.row_count, 4_800) if args.quick else args.row_count
    code_count = min(args.code_count, 80) if args.quick else args.code_count
    if args.quick:
        cases = [case for case in cases if case != "wide"]

    args.output.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for case in cases:
        for attach_mode in attach_modes:
            row = run_case(
                case=case,
                attach_mode=attach_mode,
                row_count=row_count,
                code_count=code_count,
                null_rate=args.null_rate,
                output_root=args.output,
            )
            rows.append(row)
            print(
                f"{case}/{attach_mode}: total={fmt(row['total_time_ms'])} ms "
                f"restore={fmt(row['restore_time_ms'])} ms peak_cols={fmt(row['peak_frame_col_count'], 0)}"
            )

    artifact = write_artifact("ordered_finalize_restore.json", rows)
    print(f"Saved ordered finalize/restore benchmark artifact to {artifact}")


if __name__ == "__main__":
    main()
