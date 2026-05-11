from __future__ import annotations

import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from factor_engine.engine import FactorEngine  # noqa: E402


SEED = 20260416


@dataclass(frozen=True)
class Workload:
    name: str
    expressions: list[tuple[str, str]]


def build_workload(*, code_count: int = 120, time_count: int = 180) -> pl.DataFrame:
    total_rows = code_count * time_count
    df = (
        pl.DataFrame({"row_id": range(total_rows)})
        .with_columns(
            [
                (pl.col("row_id") // time_count).alias("__code_idx"),
                (pl.col("row_id") % time_count).alias("__time_idx"),
            ]
        )
        .with_columns(
            [
                pl.concat_str([pl.lit("C"), pl.col("__code_idx").cast(pl.Utf8)]).alias("code"),
                pl.col("__time_idx").alias("time"),
                (100.0 + pl.col("__code_idx") * 0.03 + pl.col("__time_idx") * 0.05).alias("open"),
                (
                    100.0
                    + pl.col("__code_idx") * 0.03
                    + pl.col("__time_idx") * 0.05
                    + ((pl.col("__code_idx") * 11 + pl.col("__time_idx") * 7 + SEED) % 13) * 0.02
                ).alias("close"),
                (((pl.col("__code_idx") * 17 + pl.col("__time_idx") * 5 + SEED) % 5000) + 1000)
                .cast(pl.Float64)
                .alias("volume"),
            ]
        )
        .drop(["row_id", "__code_idx", "__time_idx"])
        .sample(fraction=1.0, shuffle=True, seed=SEED)
    )
    return df.select(["time", "code", "open", "close", "volume"])


WORKLOADS = [
    Workload(
        name="stage_accumulation",
        expressions=[
            ("argmax_fill_20", "argmax(fill_null(close, open), 20)"),
            ("argmin_fill_20", "argmin(fill_null(close, open), 20)"),
            ("ranked_mean", "rank(demean(ts_mean(fill_null(close, open), 20)), pct=true)"),
            ("scored_mean", "zscore(demean(ts_mean(fill_null(close, open), 20)))"),
            ("corr_ranked", "corr(rank(close), rank(volume), 20)"),
            ("cov_ranked", "cov(rank(close), rank(volume), 20)"),
        ],
    ),
    Workload(
        name="long_lived_stage",
        expressions=[
            ("ranked_a", "rank(demean(ts_mean(close, 20)), pct=true)"),
            ("ranked_b", "rank(demean(ts_mean(close, 20) + 1), pct=true)"),
            ("scored_a", "zscore(demean(ts_mean(close, 20)))"),
            ("argmax_ranked", "argmax(rank(ts_mean(close, 20), pct=true), 20)"),
        ],
    ),
]


def load_summary(path: Path) -> dict[str, object]:
    return json.loads((path / "latest_run.json").read_text(encoding="utf-8"))


def render_report(results: list[tuple[str, dict[str, object], dict[str, object]]]) -> str:
    lines = [
        "# Stage Lifecycle Benchmark",
        "",
        "This benchmark compares V1 profiling-only execution with V2 lifecycle sweep enabled.",
        "",
        "| workload | rows | expressions | V1 peak cols | V2 peak cols | V1 alive end | V2 alive end | V2 dropped | V1 peak rss mb | V2 peak rss mb |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, baseline, lifecycle in results:
        lines.append(
            f"| {name} | {baseline['row_count']} | {baseline['expression_count']} | "
            f"{baseline['peak_frame_col_count']} | {lifecycle['peak_frame_col_count']} | "
            f"{baseline['alive_stage_at_batch_end_count']} | "
            f"{lifecycle['alive_stage_at_batch_end_count']} | "
            f"{lifecycle['dropped_stage_count']} | "
            f"{float(baseline['peak_rss_mb']):.2f} | {float(lifecycle['peak_rss_mb']):.2f} |"
        )
    lines.extend(
        [
            "",
            "## Planned Lifecycle Metrics",
            "",
            "| workload | V2 planned reusable | V2 avoided recompute | V2 recomputed | V2 late alive |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for name, _baseline, lifecycle in results:
        lines.append(
            f"| {name} | {lifecycle.get('total_planned_reusable_stage_count', 0)} | "
            f"{lifecycle.get('total_avoided_recomputation_count', 0)} | "
            f"{lifecycle.get('total_recomputed_stage_count', 0)} | "
            f"{lifecycle.get('late_alive_stage_count', 0)} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    df = build_workload()
    output_root = PROJECT_ROOT / "benchmarks" / "latest" / "stage_lifecycle"
    shutil.rmtree(output_root, ignore_errors=True)
    output_root.mkdir(parents=True, exist_ok=True)

    results: list[tuple[str, dict[str, object], dict[str, object]]] = []
    for workload in WORKLOADS:
        baseline_dir = output_root / f"{workload.name}_v1"
        lifecycle_dir = output_root / f"{workload.name}_v2"
        FactorEngine().evaluate_many(
            workload.expressions,
            df,
            profiling=True,
            profile_output_dir=baseline_dir,
            benchmark_name=f"stage_lifecycle_{workload.name}_v1",
            dataset_name="synthetic_stage_lifecycle",
            lifecycle=False,
        )
        FactorEngine().evaluate_many(
            workload.expressions,
            df,
            profiling=True,
            profile_output_dir=lifecycle_dir,
            benchmark_name=f"stage_lifecycle_{workload.name}_v2",
            dataset_name="synthetic_stage_lifecycle",
            lifecycle=True,
        )
        results.append((workload.name, load_summary(baseline_dir), load_summary(lifecycle_dir)))

    report = render_report(results)
    report_path = PROJECT_ROOT / "benchmarks" / "reports" / "stage_lifecycle.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"Saved stage lifecycle benchmark report to {report_path}")


if __name__ == "__main__":
    main()
