from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from factor_engine.engine import FactorEngine  # noqa: E402
from examples.benchmark_positional_phases import build_expressions as build_positional_expressions  # noqa: E402
from examples.benchmark_stage_lifecycle import build_workload as build_synthetic_workload  # noqa: E402


def build_output_retention_expressions(count: int) -> list[tuple[str, str]]:
    expressions: list[tuple[str, str]] = []
    for index in range(count):
        window = 4 + index % 7
        mode = "argmax" if index % 2 == 0 else "argmin"
        source = "fill_null(close, open)" if index % 3 == 0 else "close"
        expressions.append((f"out_{index + 1:02d}", f"{mode}({source}, {window})"))
    return expressions


def build_frame_pressure_expressions(count: int) -> list[tuple[str, str]]:
    expressions: list[tuple[str, str]] = []
    for index in range(count):
        window = 5 + index % 6
        if index % 4 == 0:
            expr = f"rank(demean(ts_mean(fill_null(close, open), {window})), pct=true)"
        elif index % 4 == 1:
            expr = f"zscore(demean(ts_mean(close, {window})))"
        elif index % 4 == 2:
            expr = f"corr(rank(close), rank(volume), {window})"
        else:
            expr = f"argmax(ts_mean(fill_null(close, open), {window}), {window})"
        expressions.append((f"frame_{index + 1:02d}", expr))
    return expressions


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def summarize_profile(profile_dir: Path, *, workload: str) -> dict[str, object]:
    run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
    batches = read_jsonl(profile_dir / "latest_batch_details.jsonl")
    native_buffers = read_jsonl(profile_dir / "latest_native_buffer_details.jsonl")
    return {
        "workload": workload,
        "expression_count": run["expression_count"],
        "row_count": run["row_count"],
        "total_time_sec": run["total_time_sec"],
        "peak_rss_mb": run["peak_rss_mb"],
        "peak_frame_col_count": run["peak_frame_col_count"],
        "peak_output_col_count": run["peak_output_col_count"],
        "peak_stage_col_count": run["peak_stage_col_count"],
        "alive_output_at_batch_end_count": run["alive_output_at_batch_end_count"],
        "late_alive_output_count": run["late_alive_output_count"],
        "native_output_buffer_count": run["native_output_buffer_count"],
        "peak_native_buffer_bytes_estimate": run["peak_native_buffer_bytes_estimate"],
        "native_buffer_release_lag": run["native_buffer_release_lag"],
        "total_recomputed_stage_count": run["total_recomputed_stage_count"],
        "ast_node_count": run.get("ast_node_count", 0),
        "dag_node_count": run.get("dag_node_count", 0),
        "deduplicated_node_count": run.get("deduplicated_node_count", 0),
        "shared_node_count": run.get("shared_node_count", 0),
        "materialized_node_count": run.get("materialized_node_count", 0),
        "result_store_peak_entry_count": run.get("result_store_peak_entry_count", 0),
        "finalize_time_ms": run.get("finalize_time_ms", 0.0),
        "parallel_enabled": run["parallel_enabled"],
        "parallel_worker_count": run["parallel_worker_count"],
        "batch_count": len(batches),
        "native_buffer_detail_count": len(native_buffers),
    }


def parse_counts(raw: str) -> list[int]:
    return [int(part.strip()) for part in raw.split(",") if part.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run M1 memory-attribution benchmarks for output, frame, and native buffer pressure."
    )
    parser.add_argument("--data", type=Path, default=None)
    parser.add_argument("--rows", type=int, default=0, help="0 means full input/synthetic default.")
    parser.add_argument("--expr-counts", default="8,16,20")
    parser.add_argument("--code-col", default="code")
    parser.add_argument("--time-col", default="time")
    parser.add_argument("--lifecycle", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "benchmarks" / "m1_memory_model",
    )
    return parser.parse_args()


def load_dataframe(args: argparse.Namespace) -> pl.DataFrame:
    if args.data is None:
        return build_synthetic_workload(code_count=32, time_count=80)

    scan = pl.scan_parquet(str(args.data))
    if args.rows > 0:
        scan = scan.limit(args.rows)
    return scan.collect()


def main() -> None:
    args = parse_args()
    df = load_dataframe(args)
    output_root = args.output
    shutil.rmtree(output_root, ignore_errors=True)
    output_root.mkdir(parents=True, exist_ok=True)

    workloads = {
        "output_retention": build_output_retention_expressions,
        "frame_pressure": build_frame_pressure_expressions,
        "native_buffer": build_positional_expressions,
    }

    summaries: list[dict[str, object]] = []
    for workload_name, builder in workloads.items():
        for count in parse_counts(args.expr_counts):
            profile_dir = output_root / workload_name / f"expr_{count}"
            expressions = builder(count)
            FactorEngine(time_col=args.time_col, code_col=args.code_col).evaluate_many(
                expressions,
                df,
                profiling=True,
                lifecycle=args.lifecycle,
                profile_output_dir=profile_dir,
                benchmark_name=f"m1_{workload_name}_{count}",
                dataset_name="synthetic" if args.data is None else args.data.name,
            )
            summaries.append(summarize_profile(profile_dir, workload=workload_name))

    lines = [
        "# M1 Memory Model Benchmark",
        "",
        f"- rows: `{df.height}`",
        f"- lifecycle: `{args.lifecycle}`",
        "",
        "| workload | exprs | total sec | peak rss mb | peak frame cols | peak output cols | peak stage cols | dag nodes | dedup nodes | shared nodes | materialized nodes | store peak | finalize ms | native buffers | native peak bytes | release lag | recomputed | parallel | workers |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for item in summaries:
        lines.append(
            f"| {item['workload']} | {item['expression_count']} | "
            f"{float(item['total_time_sec']):.6f} | {float(item['peak_rss_mb']):.2f} | "
            f"{item['peak_frame_col_count']} | {item['peak_output_col_count']} | "
            f"{item['peak_stage_col_count']} | {item['dag_node_count']} | "
            f"{item['deduplicated_node_count']} | {item['shared_node_count']} | "
            f"{item['materialized_node_count']} | {item['result_store_peak_entry_count']} | "
            f"{float(item['finalize_time_ms']):.3f} | {item['native_output_buffer_count']} | "
            f"{item['peak_native_buffer_bytes_estimate']} | "
            f"{item['native_buffer_release_lag']} | {item['total_recomputed_stage_count']} | "
            f"{item['parallel_enabled']} | {item['parallel_worker_count']} |"
        )

    report = "\n".join(lines) + "\n"
    (output_root / "m1_memory_model_report.md").write_text(report, encoding="utf-8")
    (output_root / "summary.json").write_text(
        json.dumps(summaries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(report)


if __name__ == "__main__":
    main()
