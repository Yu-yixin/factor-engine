from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from factor_engine.engine import FactorEngine  # noqa: E402


METRICS = [
    "peak_rss_mb",
    "peak_frame_col_count",
    "peak_live_stage_count_estimate",
    "alive_stage_at_batch_end_count",
    "dropped_stage_count",
    "total_time_sec",
]


def discover_default_data_path() -> Path:
    candidates = sorted((PROJECT_ROOT / "data").glob("*.parquet"))
    if not candidates:
        raise SystemExit("No parquet file found under data/. Pass one explicitly with --data.")
    return candidates[0]


def build_expressions(df: pl.DataFrame) -> list[tuple[str, str]]:
    expressions = [
        ("argmax_fill_20", "argmax(fill_null(close, open), 20)"),
        ("argmin_fill_20", "argmin(fill_null(close, open), 20)"),
        ("ranked_mean_20", "rank(demean(ts_mean(fill_null(close, open), 20)), pct=true)"),
        (
            "argmax_ranked_mean_20",
            "argmax(rank(ts_mean(fill_null(close, open), 20), pct=true), 20)",
        ),
    ]
    if "volume" in df.columns:
        expressions.append(("corr_rank_volume_20", "corr(rank(close), rank(volume), 20)"))
    return expressions


def load_frame(path: Path, *, rows: int | None) -> pl.DataFrame:
    scan = pl.scan_parquet(str(path))
    if rows is not None:
        scan = scan.limit(rows)
    return scan.collect()


def load_summary(path: Path) -> dict[str, object]:
    return json.loads((path / "latest_run.json").read_text(encoding="utf-8"))


def frames_equal(left: pl.DataFrame, right: pl.DataFrame) -> bool:
    if left.columns != right.columns or left.shape != right.shape:
        return False
    try:
        return bool(left.equals(right, null_equal=True))
    except TypeError:
        return bool(left.equals(right))


def run_profiled(
    *,
    label: str,
    lifecycle: bool,
    df: pl.DataFrame,
    expressions: list[tuple[str, str]],
    output_dir: Path,
    time_col: str,
    code_col: str,
    dataset_name: str,
) -> tuple[pl.DataFrame, dict[str, object]]:
    shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    started_at = time.perf_counter()
    result = FactorEngine(time_col=time_col, code_col=code_col).evaluate_many(
        expressions,
        df,
        profiling=True,
        profile_output_dir=output_dir,
        benchmark_name=f"real_smoke_{label}",
        dataset_name=dataset_name,
        lifecycle=lifecycle,
    )
    summary = load_summary(output_dir)
    summary["driver_elapsed_sec"] = time.perf_counter() - started_at
    (output_dir / "driver_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return result, summary


def render_comparison(
    *,
    dataset: Path,
    rows: int,
    groups: int,
    expression_count: int,
    results_equal: bool,
    baseline: dict[str, object],
    lifecycle: dict[str, object],
) -> str:
    lines = [
        "# Real Data Stage Lifecycle Smoke",
        "",
        f"- dataset: `{dataset}`",
        f"- rows: `{rows}`",
        f"- groups: `{groups}`",
        f"- expressions: `{expression_count}`",
        f"- results_equal: `{results_equal}`",
        "",
        "| metric | V1 profiling only | V2 lifecycle | delta V2-V1 |",
        "| --- | ---: | ---: | ---: |",
    ]
    for metric in METRICS:
        left = baseline.get(metric, 0)
        right = lifecycle.get(metric, 0)
        if isinstance(left, float) or isinstance(right, float):
            delta = float(right) - float(left)
            lines.append(f"| {metric} | {float(left):.6f} | {float(right):.6f} | {delta:.6f} |")
        else:
            delta = int(right) - int(left)
            lines.append(f"| {metric} | {left} | {right} | {delta} |")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run V1/V2 stage lifecycle profiling on a real minute parquet sample."
    )
    parser.add_argument("--data", type=Path, default=None, help="Parquet path. Defaults to first data/*.parquet.")
    parser.add_argument("--rows", type=int, default=500_000, help="Rows to scan; use 0 for full file.")
    parser.add_argument("--time-col", default="time")
    parser.add_argument("--code-col", default="ths_code")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "benchmarks" / "latest" / "stage_lifecycle_real_smoke",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_path = args.data or discover_default_data_path()
    row_limit = None if args.rows == 0 else args.rows
    df = load_frame(data_path, rows=row_limit)
    required = {args.time_col, args.code_col, "close", "open"}
    missing = sorted(required.difference(df.columns))
    if missing:
        raise SystemExit(f"Missing required columns {missing}; available columns: {df.columns}")

    expressions = build_expressions(df)
    output_root = args.output
    output_root.mkdir(parents=True, exist_ok=True)

    baseline_result, baseline_summary = run_profiled(
        label="v1",
        lifecycle=False,
        df=df,
        expressions=expressions,
        output_dir=output_root / "v1",
        time_col=args.time_col,
        code_col=args.code_col,
        dataset_name=data_path.name,
    )
    lifecycle_result, lifecycle_summary = run_profiled(
        label="v2",
        lifecycle=True,
        df=df,
        expressions=expressions,
        output_dir=output_root / "v2",
        time_col=args.time_col,
        code_col=args.code_col,
        dataset_name=data_path.name,
    )

    results_equal = frames_equal(lifecycle_result, baseline_result)
    comparison = {
        "dataset": str(data_path),
        "rows": df.height,
        "groups": df.get_column(args.code_col).n_unique(),
        "expression_count": len(expressions),
        "results_equal": results_equal,
        "v1": baseline_summary,
        "v2": lifecycle_summary,
    }
    (output_root / "latest_real_smoke_comparison.json").write_text(
        json.dumps(comparison, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    report = render_comparison(
        dataset=data_path,
        rows=df.height,
        groups=df.get_column(args.code_col).n_unique(),
        expression_count=len(expressions),
        results_equal=results_equal,
        baseline=baseline_summary,
        lifecycle=lifecycle_summary,
    )
    (output_root / "real_smoke_report.md").write_text(report, encoding="utf-8")
    print(report)
    if not results_equal:
        raise SystemExit("V1/V2 outputs differ; inspect benchmark artifacts before trusting metrics.")


if __name__ == "__main__":
    main()
