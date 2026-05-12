from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from performance_truth_common import (
    FIELD_NOT_AVAILABLE,
    LATEST_ROOT,
    build_synthetic_frame,
    correctness_smoke_passed,
    counted_prepared_sorts,
    evaluate_profiled,
    fmt,
    route_groups,
    sum_batch_field,
    write_artifact,
)


def mixed_expressions(case: str) -> list[tuple[str, str]]:
    base = [
        ("seg_mean_close_3", "seg_mean(close, 3)"),
        ("seg_sum_volume_3", "seg_sum(volume, 3)"),
        ("mean_close_20", "ts_mean(close, 20)"),
        ("rank_close_20", "ts_rank(close, 20)"),
        ("corr_close_volume_20", "corr(close, volume, 20)"),
        ("rank_mean_20", "rank(ts_mean(close, 20))"),
        ("demean_rank_20", "demean(ts_rank(open, 20))"),
        ("group_rank_corr_20", "group_rank(corr(close, volume, 20), industry)"),
    ]
    if case == "mixed_segmented_ordered_staged":
        return base
    if case == "segmented_only":
        return base[:2]
    if case == "ordered_staged_only":
        return base[2:]
    raise ValueError(f"Unsupported case: {case}")


def parse_csv(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def run_case(
    *,
    case: str,
    row_count: int,
    code_count: int,
    null_rate: float,
    output_root: Path,
) -> dict[str, Any]:
    df = build_synthetic_frame(row_count=row_count, code_count=code_count, null_rate=null_rate)
    expressions = mixed_expressions(case)
    profile_dir = output_root / case
    with counted_prepared_sorts() as sort_state:
        result, summary, batches, _phases, elapsed_ms = evaluate_profiled(
            expressions=expressions,
            df=df,
            profile_dir=profile_dir,
            benchmark_name=f"performance_truth_mixed_sorting_{case}",
        )
    output_names = [name for name, _expr in expressions]
    profile_sort_time = sum_batch_field(batches, "prepare_sort_time_ms")
    counted_sort_time = sort_state.get("time_ms", FIELD_NOT_AVAILABLE)
    sort_count = sort_state.get("count", FIELD_NOT_AVAILABLE)
    reuse = "unknown"
    if isinstance(sort_count, int):
        reuse = "reused" if sort_count <= 1 else "rebuilt"
    evidence = (
        f"monkeypatch build_prepared_frame count={sort_count}; "
        f"profile prepare_sort_time_ms={fmt(profile_sort_time)}"
    )
    conclusion = (
        "HYPOTHESIS: segmented and ordered routes build separate prepared frames"
        if reuse == "rebuilt"
        else "prepared frame appears reused or only one ordered route was exercised"
        if reuse == "reused"
        else "UNKNOWN"
    )
    return {
        "case": case,
        "row_count": row_count,
        "code_count": code_count,
        "null_rate": null_rate,
        "expression_count": len(expressions),
        "prepare_sort_count": sort_count,
        "prepare_sort_time_ms": profile_sort_time,
        "counted_prepare_sort_time_ms": counted_sort_time,
        "route_groups": route_groups(expressions, df),
        "total_time_ms": float(summary.get("total_time_sec", elapsed_ms / 1000)) * 1000,
        "peak_rss_mb": summary.get("peak_rss_mb", FIELD_NOT_AVAILABLE),
        "sorted_prepared_frame_reuse": reuse,
        "output_shape": [result.height, result.width],
        "correctness_smoke_passed": correctness_smoke_passed(result, df, output_names),
        "evidence": evidence,
        "conclusion": conclusion,
        "profile_dir": str(profile_dir),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure whether mixed segmented + ordered batches cause repeated sorting."
    )
    parser.add_argument("--row-count", type=int, default=12_000)
    parser.add_argument("--code-count", type=int, default=120)
    parser.add_argument("--null-rate", type=float, default=0.01)
    parser.add_argument(
        "--cases",
        default="mixed_segmented_ordered_staged,segmented_only,ordered_staged_only",
    )
    parser.add_argument("--quick", action="store_true", help="Run a small documented scale.")
    parser.add_argument("--output", type=Path, default=LATEST_ROOT / "mixed_segmented_ordered_sorting")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cases = parse_csv(args.cases)
    row_count = min(args.row_count, 4_800) if args.quick else args.row_count
    code_count = min(args.code_count, 80) if args.quick else args.code_count
    args.output.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for case in cases:
        row = run_case(
            case=case,
            row_count=row_count,
            code_count=code_count,
            null_rate=args.null_rate,
            output_root=args.output,
        )
        rows.append(row)
        print(
            f"{case}: sorts={fmt(row['prepare_sort_count'], 0)} "
            f"profile_sort={fmt(row['prepare_sort_time_ms'])} ms total={fmt(row['total_time_ms'])} ms "
            f"reuse={row['sorted_prepared_frame_reuse']}"
        )

    artifact = write_artifact("mixed_segmented_ordered_sorting.json", rows)
    print(f"Saved mixed sorting benchmark artifact to {artifact}")


if __name__ == "__main__":
    main()
