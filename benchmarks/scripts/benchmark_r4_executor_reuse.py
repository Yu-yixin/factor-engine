from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from factor_engine.engine import FactorEngine  # noqa: E402
from factor_engine.lifecycle import (  # noqa: E402
    normalize_helper_lifecycle_mode,
    normalize_lifecycle_mode,
)


def parse_counts(raw: str) -> list[int]:
    return [int(part.strip()) for part in raw.split(",") if part.strip()]


def parse_workloads(raw: str) -> list[str]:
    names = [part.strip() for part in raw.split(",") if part.strip()]
    unknown = sorted(set(names) - set(WORKLOADS))
    if unknown:
        raise ValueError(
            f"unknown workload(s): {', '.join(unknown)}. Available: {', '.join(WORKLOADS)}"
        )
    return names


def repeated_terms(term: str, count: int) -> str:
    return " + ".join([term] * count)


def build_repeated_heavy(count: int) -> list[tuple[str, str]]:
    return [("repeated_heavy", repeated_terms("ts_rank(close, 10)", count))]


def build_cheap_repeat(count: int) -> list[tuple[str, str]]:
    return [("cheap_repeat", repeated_terms("(close + open)", count))]


def build_multi_consumer_dag(count: int) -> list[tuple[str, str]]:
    return [
        (f"consumer_{index + 1:02d}", f"ts_rank(close, 10) + {index + 1}")
        for index in range(count)
    ]


def build_native_heavy(count: int) -> list[tuple[str, str]]:
    return [("native_heavy", repeated_terms("argmax(close, 10)", count))]


def build_native_heavy_probe(count: int) -> list[tuple[str, str]]:
    return [("native_heavy_probe", repeated_terms("argmax(close, 10)", count))]


def build_native_heavy_nested(_count: int) -> list[tuple[str, str]]:
    return [
        (
            "native_heavy_nested",
            "argmax(ts_mean(close, 10), 10) + argmax(ts_mean(close, 10), 10)",
        )
    ]


def build_native_heavy_multi_read(count: int) -> list[tuple[str, str]]:
    return [("native_heavy_multi_read", repeated_terms("argmax(close, 10)", count))]


def build_multi_shared_nodes(count: int) -> list[tuple[str, str]]:
    terms = [
        repeated_terms("ts_rank(close, 10)", 2),
        repeated_terms("ts_rank(open, 10)", 2),
        repeated_terms("ts_rank(volume, 10)", 2),
    ]
    return [("multi_shared_nodes", " + ".join(terms[: max(1, min(count, len(terms)))]))]


def build_nested_dag(_count: int) -> list[tuple[str, str]]:
    return [
        (
            "nested_dag",
            "ts_rank(ts_mean(close, 10), 10) + ts_rank(ts_mean(close, 10), 10)",
        )
    ]


def build_nested_probe_a(_count: int) -> list[tuple[str, str]]:
    return [
        (
            "nested_probe_a",
            "ts_rank(ts_rank(close, 10), 10) + ts_rank(ts_rank(close, 10), 10)",
        )
    ]


def build_nested_probe_b(_count: int) -> list[tuple[str, str]]:
    return [
        (
            "nested_probe_b",
            "ts_rank(ts_mean(close, 10), 10) + ts_rank(ts_mean(close, 10), 10)",
        )
    ]


def build_nested_probe_c(_count: int) -> list[tuple[str, str]]:
    return [
        (
            "nested_probe_c",
            "ts_rank(ts_mean(close, 10), 10) + ts_std(ts_mean(close, 10), 10)",
        )
    ]


def build_partial_reuse(_count: int) -> list[tuple[str, str]]:
    return [
        ("partial_a", "ts_mean(close, 10) + 1"),
        ("partial_b", "ts_rank(ts_mean(close, 10), 10)"),
    ]


WORKLOADS = {
    "repeated_heavy": build_repeated_heavy,
    "cheap_repeat": build_cheap_repeat,
    "multi_consumer_dag": build_multi_consumer_dag,
    "native_heavy": build_native_heavy,
    "native_heavy_probe": build_native_heavy_probe,
    "native_heavy_nested": build_native_heavy_nested,
    "native_heavy_multi_read": build_native_heavy_multi_read,
    "multi_shared_nodes": build_multi_shared_nodes,
    "nested_dag": build_nested_dag,
    "nested_probe_a": build_nested_probe_a,
    "nested_probe_b": build_nested_probe_b,
    "nested_probe_c": build_nested_probe_c,
    "partial_reuse": build_partial_reuse,
}


def load_dataframe(args: argparse.Namespace) -> pl.DataFrame:
    scan = pl.scan_parquet(str(args.data))
    if args.rows > 0:
        scan = scan.limit(args.rows)
    return scan.collect()


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def resolve_code_col(args: argparse.Namespace, df: pl.DataFrame) -> str:
    if args.code_col in df.columns:
        return args.code_col
    if args.code_col == "code" and "ths_code" in df.columns:
        return "ths_code"
    raise ValueError(
        f"code column '{args.code_col}' not found. Available columns: {', '.join(df.columns)}"
    )


def estimated_unshared_compute_calls(
    expressions: list[tuple[str, str]],
    df: pl.DataFrame,
    *,
    time_col: str,
    code_col: str,
) -> int:
    inspection = FactorEngine(time_col=time_col, code_col=code_col).inspect_dag(expressions, df)
    return sum(
        int(item["occurrence_count"])
        for item in inspection["deduplicated_nodes"]
        if item["share_decision"] == "materialize"
    )


def summarize_profile(
    profile_dir: Path,
    *,
    workload: str,
    consumer_count: int,
    dag_cse: bool,
    estimated_baseline_compute_calls: int,
) -> dict[str, object]:
    run = read_json(profile_dir / "latest_run.json")
    node_details = read_jsonl(profile_dir / "latest_node_execution_details.jsonl")
    return {
        "workload": workload,
        "consumer_count": consumer_count,
        "dag_cse": dag_cse,
        "estimated_baseline_compute_calls": estimated_baseline_compute_calls,
        "expression_count": run["expression_count"],
        "row_count": run["row_count"],
        "total_time_sec": run["total_time_sec"],
        "peak_rss_mb": run["peak_rss_mb"],
        "ast_node_count": run.get("ast_node_count", 0),
        "dag_node_count": run.get("dag_node_count", 0),
        "deduplicated_node_count": run.get("deduplicated_node_count", 0),
        "shared_node_count": run.get("shared_node_count", 0),
        "materialized_node_count": run.get("materialized_node_count", 0),
        "result_store_peak_entry_count": run.get("result_store_peak_entry_count", 0),
        "total_compute_calls": run.get("total_compute_calls", 0),
        "node_store_compute_calls": run.get("node_store_compute_calls", 0),
        "compiled_output_heavy_occurrence_count": run.get(
            "compiled_output_heavy_occurrence_count",
            0,
        ),
        "total_store_hits": run.get("total_store_hits", 0),
        "node_store_read_count": run.get("node_store_read_count", 0),
        "reuse_consumer_count": run.get("reuse_consumer_count", 0),
        "shared_node_hit_rate": run.get("shared_node_hit_rate", 0.0),
        "node_store_compute_time_ms": run.get(
            "node_store_compute_time_ms",
            run.get("compute_time_ms", 0.0),
        ),
        "compiled_output_eval_time_ms": run.get("compiled_output_eval_time_ms", 0.0),
        "restore_assemble_time_ms": run.get(
            "restore_assemble_time_ms",
            run.get("restore_time_ms", 0.0),
        ),
        "store_write_time_ms": run.get("store_write_time_ms", 0.0),
        "store_hit_time_ms": run.get("store_hit_time_ms", 0.0),
        "append_time_ms": run.get("append_time_ms", 0.0),
        "finalize_time_ms": run.get("finalize_time_ms", 0.0),
        "lifecycle_candidate_count": run.get("lifecycle_candidate_count", 0),
        "lifecycle_releasable_node_count": run.get("lifecycle_releasable_node_count", 0),
        "lifecycle_peak_live_node_count": run.get("lifecycle_peak_live_node_count", 0),
        "lifecycle_peak_live_bytes_est": run.get("lifecycle_peak_live_bytes_est", 0),
        "avg_release_lag_steps": run.get("avg_release_lag_steps", 0.0),
        "max_release_lag_steps": run.get("max_release_lag_steps", 0),
        "batch_end_step": run.get("batch_end_step", 0),
        "avg_structural_release_lag_steps": run.get(
            "avg_structural_release_lag_steps",
            run.get("avg_release_lag_steps", 0.0),
        ),
        "max_structural_release_lag_steps": run.get(
            "max_structural_release_lag_steps",
            run.get("max_release_lag_steps", 0),
        ),
        "avg_finalize_retention_lag_steps": run.get("avg_finalize_retention_lag_steps", 0.0),
        "max_finalize_retention_lag_steps": run.get("max_finalize_retention_lag_steps", 0),
        "potential_live_bytes_step_savings": run.get(
            "potential_live_bytes_step_savings",
            0,
        ),
        "l2_first_wave_candidate_count": run.get("l2_first_wave_candidate_count", 0),
        "dropped_node_count": run.get("dropped_node_count", 0),
        "drop_hit_count": run.get("drop_hit_count", 0),
        "drop_miss_count": run.get("drop_miss_count", 0),
        "peak_live_bytes_est_before_drop": run.get(
            "peak_live_bytes_est_before_drop",
            run.get("lifecycle_peak_live_bytes_est", 0),
        ),
        "peak_live_bytes_est_after_drop": run.get("peak_live_bytes_est_after_drop", 0),
        "drop_delay_steps_avg": run.get("drop_delay_steps_avg", 0.0),
        "drop_delay_steps_max": run.get("drop_delay_steps_max", 0),
        "lifecycle_mode": run.get("lifecycle_mode", "off"),
        "helper_lifecycle_mode": run.get("helper_lifecycle_mode", "off"),
        "lifecycle_effective": run.get("lifecycle_effective", False),
        "multi_node_overlap_peak": run.get("multi_node_overlap_peak", 0),
        "multi_node_peak_live_bytes_before": run.get("multi_node_peak_live_bytes_before", 0),
        "multi_node_peak_live_bytes_after": run.get("multi_node_peak_live_bytes_after", 0),
        "per_node_drop_order": run.get("per_node_drop_order", []),
        "nested_drop_order_valid": run.get("nested_drop_order_valid", True),
        "partial_reuse_safety_flag": run.get("partial_reuse_safety_flag", True),
        "native_heavy_node_count": run.get("native_heavy_node_count", 0),
        "native_heavy_forbidden_count": run.get("native_heavy_forbidden_count", 0),
        "native_heavy_observable_only_count": run.get(
            "native_heavy_observable_only_count",
            0,
        ),
        "native_heavy_candidate_future_count": run.get(
            "native_heavy_candidate_future_count",
            0,
        ),
        "native_compute_time_ms": run.get("native_compute_time_ms", 0.0),
        "native_path_normalization_time_ms": run.get(
            "native_path_normalization_time_ms",
            0.0,
        ),
        "native_storage_residency_bytes": run.get("native_storage_residency_bytes", 0),
        "native_node_store_read_count": run.get("native_node_store_read_count", 0),
        "native_logical_consumer_count": run.get("native_logical_consumer_count", 0),
        "native_effective_use_count": run.get("native_effective_use_count", 0),
        "native_fallback_eval_count": run.get("native_fallback_eval_count", 0),
        "native_rewrite_applied_count": run.get("native_rewrite_applied_count", 0),
        "native_helper_usage_patterns": run.get("native_helper_usage_patterns", []),
        "helper_column_count": run.get("helper_column_count", 0),
        "helper_releasable_count": run.get("helper_releasable_count", 0),
        "helper_blocked_count": run.get("helper_blocked_count", 0),
        "helper_peak_live_bytes": run.get("helper_peak_live_bytes", 0),
        "helper_potential_savings": run.get("helper_potential_savings", 0),
        "helper_blocker_reasons": run.get("helper_blocker_reasons", []),
        "helper_dropped_count": run.get("helper_dropped_count", 0),
        "helper_drop_miss_count": run.get("helper_drop_miss_count", 0),
        "helper_peak_live_bytes_before_drop": run.get(
            "helper_peak_live_bytes_before_drop",
            run.get("helper_peak_live_bytes", 0),
        ),
        "helper_peak_live_bytes_after_drop": run.get("helper_peak_live_bytes_after_drop", 0),
        "helper_frame_width_before_drop": run.get("helper_frame_width_before_drop", 0),
        "helper_frame_width_after_drop": run.get("helper_frame_width_after_drop", 0),
        "helper_drop_delay_steps_avg": run.get("helper_drop_delay_steps_avg", 0.0),
        "helper_lifecycle_effective": run.get("helper_lifecycle_effective", False),
        "nested_helper_dropped_count": run.get("nested_helper_dropped_count", 0),
        "nested_helper_drop_missed_count": run.get("nested_helper_drop_missed_count", 0),
        "nested_helper_peak_live_bytes_before_drop": run.get(
            "nested_helper_peak_live_bytes_before_drop",
            0,
        ),
        "nested_helper_peak_live_bytes_after_drop": run.get(
            "nested_helper_peak_live_bytes_after_drop",
            0,
        ),
        "nested_helper_frame_width_before_drop": run.get(
            "nested_helper_frame_width_before_drop",
            0,
        ),
        "nested_helper_frame_width_after_drop": run.get(
            "nested_helper_frame_width_after_drop",
            0,
        ),
        "nested_helper_lifecycle_effective": run.get(
            "nested_helper_lifecycle_effective",
            False,
        ),
        "node_detail_count": len(node_details),
    }


def render_report(
    summaries: list[dict[str, object]],
    *,
    rows: int,
    data_name: str,
    lifecycle: bool,
    lifecycle_mode: str,
    helper_lifecycle_mode: str,
) -> str:
    lines = [
        "# R4 Executor-Native Reuse Benchmark",
        "",
        f"- data: `{data_name}`",
        f"- rows: `{rows}`",
        f"- lifecycle: `{lifecycle}`",
        f"- lifecycle mode: `{lifecycle_mode}`",
        f"- helper lifecycle mode: `{helper_lifecycle_mode}`",
        "",
        "| workload | consumers | cse | lifecycle mode | helper mode | lifecycle effective | helper effective | sec | est no-reuse computes | attributed computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | native nodes | native eligibility | native compute ms | native path ms | native storage bytes | native reads | native logical consumers | native effective uses | native fallback evals | native rewrites | native helper patterns | helper cols | helper releasable | helper blocked | helper bytes | helper before bytes | helper after bytes | helper dropped | helper misses | helper frame before | helper frame after | helper delay avg | helper bytes-step | helper blockers | lifecycle candidates | releasable | peak live nodes | before bytes | after bytes | dropped | misses | drop delay avg | overlap peak | drop order | nested order | partial safe | batch end step | structural lag | finalize lag | bytes-step savings | L2 first-wave | hit rate | materialized | store peak | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms | peak rss mb |",
        "| --- | ---: | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in summaries:
        lines.append(
            f"| {item['workload']} | {item['consumer_count']} | {item['dag_cse']} | "
            f"{item['lifecycle_mode']} | {item['helper_lifecycle_mode']} | "
            f"{item['lifecycle_effective']} | {item['helper_lifecycle_effective']} | "
            f"{float(item['total_time_sec']):.6f} | "
            f"{item['estimated_baseline_compute_calls']} | {item['total_compute_calls']} | "
            f"{item['node_store_compute_calls']} | "
            f"{item['compiled_output_heavy_occurrence_count']} | "
            f"{item['node_store_read_count']} | {item['reuse_consumer_count']} | "
            f"{item['native_heavy_node_count']} | "
            f"F:{item['native_heavy_forbidden_count']}/"
            f"O:{item['native_heavy_observable_only_count']}/"
            f"C:{item['native_heavy_candidate_future_count']} | "
            f"{float(item['native_compute_time_ms']):.3f} | "
            f"{float(item['native_path_normalization_time_ms']):.3f} | "
            f"{item['native_storage_residency_bytes']} | "
            f"{item['native_node_store_read_count']} | "
            f"{item['native_logical_consumer_count']} | "
            f"{item['native_effective_use_count']} | "
            f"{item['native_fallback_eval_count']} | "
            f"{item['native_rewrite_applied_count']} | "
            f"`{','.join(item['native_helper_usage_patterns'])}` | "
            f"{item['helper_column_count']} | "
            f"{item['helper_releasable_count']} | "
            f"{item['helper_blocked_count']} | "
            f"{item['helper_peak_live_bytes']} | "
            f"{item['helper_peak_live_bytes_before_drop']} | "
            f"{item['helper_peak_live_bytes_after_drop']} | "
            f"{item['helper_dropped_count']} | "
            f"{item['helper_drop_miss_count']} | "
            f"{item['helper_frame_width_before_drop']} | "
            f"{item['helper_frame_width_after_drop']} | "
            f"{float(item['helper_drop_delay_steps_avg']):.3f} | "
            f"{item['helper_potential_savings']} | "
            f"`{','.join(item['helper_blocker_reasons'])}` | "
            f"{item['lifecycle_candidate_count']} | "
            f"{item['lifecycle_releasable_node_count']} | "
            f"{item['lifecycle_peak_live_node_count']} | "
            f"{item['peak_live_bytes_est_before_drop']} | "
            f"{item['peak_live_bytes_est_after_drop']} | "
            f"{item['dropped_node_count']} | "
            f"{item['drop_miss_count']} | "
            f"{float(item['drop_delay_steps_avg']):.3f} | "
            f"{item['multi_node_overlap_peak']} | "
            f"`{','.join(item['per_node_drop_order'])}` | "
            f"{item['nested_drop_order_valid']} | "
            f"{item['partial_reuse_safety_flag']} | "
            f"{item['batch_end_step']} | "
            f"{float(item['avg_structural_release_lag_steps']):.3f} | "
            f"{float(item['avg_finalize_retention_lag_steps']):.3f} | "
            f"{item['potential_live_bytes_step_savings']} | "
            f"{item['l2_first_wave_candidate_count']} | "
            f"{float(item['shared_node_hit_rate']):.3f} | "
            f"{item['materialized_node_count']} | {item['result_store_peak_entry_count']} | "
            f"{float(item['node_store_compute_time_ms']):.3f} | "
            f"{float(item['compiled_output_eval_time_ms']):.3f} | "
            f"{float(item['restore_assemble_time_ms']):.3f} | "
            f"{float(item['append_time_ms']):.3f} | "
            f"{float(item['finalize_time_ms']):.3f} | "
            f"{float(item['peak_rss_mb']):.2f} |"
        )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run R4 executor-native reuse benchmarks with DAG/CSE off/on."
    )
    parser.add_argument("--data", type=Path, default=PROJECT_ROOT / "data" / "data.parquet")
    parser.add_argument("--rows", type=int, default=0, help="0 means full input.")
    parser.add_argument("--consumer-counts", default="1,2,4,8")
    parser.add_argument(
        "--workloads",
        default="repeated_heavy,cheap_repeat,multi_consumer_dag,native_heavy",
        help=f"Comma-separated workload names. Available: {', '.join(WORKLOADS)}",
    )
    parser.add_argument("--code-col", default="code")
    parser.add_argument("--time-col", default="time")
    parser.add_argument("--lifecycle", action="store_true")
    parser.add_argument("--lifecycle-mode", choices=["off", "first_wave"], default=None)
    parser.add_argument(
        "--helper-lifecycle-mode",
        choices=["off", "first_wave", "second_wave_nested"],
        default=None,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "benchmarks" / "latest" / "r4_executor_reuse",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    lifecycle_mode = normalize_lifecycle_mode(
        lifecycle=args.lifecycle,
        lifecycle_mode=args.lifecycle_mode,
    )
    helper_lifecycle_mode = normalize_helper_lifecycle_mode(
        helper_lifecycle_mode=args.helper_lifecycle_mode,
    )
    df = load_dataframe(args)
    code_col = resolve_code_col(args, df)
    output_root = args.output
    shutil.rmtree(output_root, ignore_errors=True)
    output_root.mkdir(parents=True, exist_ok=True)

    summaries: list[dict[str, object]] = []
    selected_workloads = parse_workloads(args.workloads)
    selected_counts = parse_counts(args.consumer_counts)
    total_runs = len(selected_workloads) * len(selected_counts) * 2
    run_index = 0
    for workload_name in selected_workloads:
        builder = WORKLOADS[workload_name]
        for count in parse_counts(args.consumer_counts):
            expressions = builder(count)
            estimated_baseline = estimated_unshared_compute_calls(
                expressions,
                df,
                time_col=args.time_col,
                code_col=code_col,
            )
            for dag_cse in (False, True):
                run_index += 1
                mode = "cse_on" if dag_cse else "cse_off"
                profile_dir = output_root / workload_name / f"consumers_{count}" / mode
                print(
                    f"[{run_index}/{total_runs}] running {workload_name} "
                    f"consumers={count} {mode}",
                    flush=True,
                )
                FactorEngine(time_col=args.time_col, code_col=code_col).evaluate_many(
                    expressions,
                    df,
                    profiling=True,
                    dag_cse=dag_cse,
                    lifecycle_mode=lifecycle_mode,
                    helper_lifecycle_mode=helper_lifecycle_mode,
                    profile_output_dir=profile_dir,
                    benchmark_name=f"r4_{workload_name}_{count}_{mode}",
                    dataset_name=args.data.name,
                )
                summaries.append(
                    summarize_profile(
                        profile_dir,
                        workload=workload_name,
                        consumer_count=count,
                        dag_cse=dag_cse,
                        estimated_baseline_compute_calls=estimated_baseline,
                    )
                )
                partial_report = render_report(
                    summaries,
                    rows=df.height,
                    data_name=args.data.name,
                    lifecycle=lifecycle_mode != "off",
                    lifecycle_mode=lifecycle_mode,
                    helper_lifecycle_mode=helper_lifecycle_mode,
                )
                (output_root / "r4_executor_reuse_partial_report.md").write_text(
                    partial_report,
                    encoding="utf-8",
                )
                (output_root / "summary.partial.json").write_text(
                    json.dumps(summaries, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

    report = render_report(
        summaries,
        rows=df.height,
        data_name=args.data.name,
        lifecycle=lifecycle_mode != "off",
        lifecycle_mode=lifecycle_mode,
        helper_lifecycle_mode=helper_lifecycle_mode,
    )
    (output_root / "r4_executor_reuse_report.md").write_text(report, encoding="utf-8")
    (output_root / "summary.json").write_text(
        json.dumps(summaries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(report)


if __name__ == "__main__":
    main()
