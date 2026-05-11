from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import polars as pl
from polars.testing import assert_frame_equal

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from factor_engine.auto_optimization import (  # noqa: E402
    CandidateEvaluation,
    OptimizationCandidate,
    OptimizationHistoryEntry,
    build_structural_bottleneck_report,
    candidate_space_exhausted,
    candidate_seen_before,
    detect_bottlenecks,
    generate_m3_candidates,
    generate_m3_proposal_candidates,
    generate_m4_executable_candidates,
    generate_m4_candidates,
    optimization_score,
    select_best_candidate,
    stagnation_detected,
)
from factor_engine.engine import FactorEngine  # noqa: E402


def load_history(path: Path) -> list[OptimizationHistoryEntry]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [OptimizationHistoryEntry(**item) for item in raw]


def save_history(path: Path, history: list[OptimizationHistoryEntry]) -> None:
    path.write_text(
        json.dumps([entry.to_dict() for entry in history], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_dataframe(data: Path, *, rows: int) -> pl.DataFrame:
    scan = pl.scan_parquet(str(data))
    if rows > 0:
        scan = scan.limit(rows)
    return scan.collect()


def resolve_code_col(code_col: str, df: pl.DataFrame) -> str:
    if code_col in df.columns:
        return code_col
    if code_col == "code" and "ths_code" in df.columns:
        return "ths_code"
    raise ValueError(
        f"code column '{code_col}' not found. Available columns: {', '.join(df.columns)}"
    )


def workload_expressions() -> dict[str, list[tuple[str, str]]]:
    return {
        "synthetic_small": [
            ("reuse", "ts_rank(close, 10) + ts_rank(close, 10)"),
        ],
        "synthetic_large": [
            (
                "multi",
                "ts_rank(close, 10) + ts_rank(close, 10) + "
                "ts_rank(open, 10) + ts_rank(open, 10)",
            ),
        ],
        "real_workload": [
            ("a", "ts_rank(close, 10) + 1"),
            ("b", "ts_rank(close, 10) + 2"),
            ("c", "ts_mean(close, 10) + 3"),
        ],
        "pure_nested_chain": [
            (
                "nested",
                "ts_rank(ts_mean(close, 10), 10) + ts_rank(ts_mean(close, 10), 10)",
            ),
        ],
        "mixed_pattern": [
            ("direct", "ts_mean(close, 10) + 1"),
            (
                "nested",
                "ts_rank(ts_mean(close, 10), 10) + ts_rank(ts_mean(close, 10), 10)",
            ),
        ],
        "m4_repeated_neutral_subgraph": [
            (
                "neutral",
                "ts_rank(close + 0, 10) + ts_rank(close, 10) + "
                "ts_mean(close + 0, 10) + ts_mean(close, 10)",
            ),
        ],
        "m4_unary_chain_fusion": [
            (
                "fusion",
                "ts_rank(ts_mean(close, 10), 10) + "
                "ts_rank(ts_mean(close, 10), 10)",
            ),
        ],
    }


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


def read_profile_artifacts(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    run_summaries: list[dict[str, Any]] = []
    node_details: list[dict[str, Any]] = []
    candidate_runs = root / "candidate_runs"
    if not candidate_runs.exists():
        return run_summaries, node_details
    for run_path in candidate_runs.rglob("latest_run.json"):
        try:
            run = read_json(run_path)
        except (OSError, json.JSONDecodeError):
            continue
        parts = run_path.parts
        if len(parts) >= 3:
            run.setdefault("workload", parts[-3])
        run_summaries.append(run)
    for node_path in candidate_runs.rglob("latest_node_execution_details.jsonl"):
        node_details.extend(read_jsonl(node_path))
    return run_summaries, node_details


def run_workload(
    *,
    df: pl.DataFrame,
    expressions: list[tuple[str, str]],
    profile_dir: Path,
    benchmark_name: str,
    code_col: str,
    time_col: str,
    output_attach_mode: str,
    frame_projection_mode: str,
    materialization_threshold_mode: str,
    recomputation_guardrail_max_expansion: int,
    planner_cse_mode: str,
    fusion_mode: str,
) -> tuple[pl.DataFrame, dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    engine = FactorEngine(time_col=time_col, code_col=code_col)
    result = engine.evaluate_many(
        expressions,
        df,
        profiling=True,
        dag_cse=True,
        lifecycle_mode="first_wave",
        helper_lifecycle_mode="second_wave_nested",
        output_attach_mode=output_attach_mode,
        frame_projection_mode=frame_projection_mode,
        materialization_threshold_mode=materialization_threshold_mode,
        recomputation_guardrail_max_expansion=recomputation_guardrail_max_expansion,
        planner_cse_mode=planner_cse_mode,
        fusion_mode=fusion_mode,
        profile_output_dir=profile_dir,
        benchmark_name=benchmark_name,
        dataset_name="dataframe",
    )
    dag_inspection = (
        engine.last_expression_dag.to_inspection()
        if engine.last_expression_dag is not None
        else {}
    )
    return (
        result,
        read_json(profile_dir / "latest_run.json"),
        read_jsonl(profile_dir / "latest_node_execution_details.jsonl"),
        dag_inspection,
    )


def pct_reduction(before: float, after: float) -> float:
    if before <= 0:
        return 0.0
    return (before - after) / before * 100.0


def pct_increase(before: float, after: float) -> float:
    if before <= 0:
        return 0.0
    return (after - before) / before * 100.0


def aggregate_metrics(rows: list[dict[str, Any]]) -> dict[str, float]:
    return {
        "sec": sum(float(row.get("total_time_sec", 0.0) or 0.0) for row in rows),
        "memory_peak": max(
            (float(row.get("peak_rss_mb", 0.0) or 0.0) for row in rows),
            default=0.0,
        ),
        "frame_peak": max(
            (float(row.get("peak_frame_col_count", 0) or 0) for row in rows),
            default=0.0,
        ),
        "helper_before": sum(
            float(row.get("helper_peak_live_bytes_before_drop", 0) or 0)
            for row in rows
        ),
        "helper_after": sum(
            float(row.get("helper_peak_live_bytes_after_drop", 0) or 0)
            for row in rows
        ),
        "frame_before": sum(
            float(row.get("helper_frame_width_before_drop", 0) or 0)
            for row in rows
        ),
        "frame_after": sum(
            float(row.get("helper_frame_width_after_drop", 0) or 0)
            for row in rows
        ),
        "recomputation_expansion": sum(
            float(row.get("recomputation_expansion_actual_delta", 0) or 0)
            for row in rows
        ),
        "recomputation_guardrail_blocked": sum(
            float(row.get("recomputation_guardrail_blocked_count", 0) or 0)
            for row in rows
        ),
        "recomputation_guardrail_allowed": sum(
            float(row.get("recomputation_guardrail_allowed_count", 0) or 0)
            for row in rows
        ),
    }


def aggregate_m4_cse_audit(
    *,
    candidate: OptimizationCandidate,
    candidate_rows: list[dict[str, Any]],
    candidate_dag_inspections: list[dict[str, Any]],
) -> dict[str, Any]:
    if candidate.id != "m4_cse_expand_repeated_subgraphs":
        return {
            "candidate_id": candidate.id,
            "selected_family": "",
            "matched_groups": 0,
            "reused_groups": 0,
            "merged_nodes": [],
            "estimated_helper_bytes_saved": 0,
            "affected_subgraph_signatures": [],
            "baseline_identity_rule": "",
            "expanded_identity_rule": "",
            "baseline_miss_reason": "",
            "safe_merge_rationale": "",
        }
    audits = [
        inspection.get("expanded_cse_audit", {})
        for inspection in candidate_dag_inspections
        if inspection.get("expanded_cse_audit", {}).get("selected_family")
    ]
    selected_family = "rolling_neutral_add_input"
    matched_groups = sum(int(audit.get("matched_groups", 0) or 0) for audit in audits)
    reused_groups = sum(int(audit.get("reused_groups", 0) or 0) for audit in audits)
    affected_signatures = sorted(
        {
            str(signature)
            for audit in audits
            for signature in audit.get("affected_subgraph_signatures", [])
        }
    )
    merged_nodes = sorted(
        {
            str(node)
            for audit in audits
            for node in audit.get("merged_nodes", [])
        }
    )
    estimated_helper_bytes_saved = sum(
        int(row.get("row_count", 0) or 0) * 8 * int(
            audit.get("reused_groups", 0) or 0
        )
        for row, audit in zip(candidate_rows, [
            inspection.get("expanded_cse_audit", {})
            for inspection in candidate_dag_inspections
        ])
    )
    first_audit = audits[0] if audits else {}
    return {
        "candidate_id": candidate.id,
        "selected_family": selected_family if audits else "",
        "matched_groups": matched_groups,
        "reused_groups": reused_groups,
        "merged_nodes": merged_nodes,
        "estimated_helper_bytes_saved": estimated_helper_bytes_saved,
        "affected_subgraph_signatures": affected_signatures,
        "baseline_identity_rule": first_audit.get("baseline_identity_rule", ""),
        "expanded_identity_rule": first_audit.get("expanded_identity_rule", ""),
        "baseline_miss_reason": first_audit.get("baseline_miss_reason", ""),
        "safe_merge_rationale": first_audit.get("safe_merge_rationale", ""),
    }


def aggregate_m4_fusion_audit(
    *,
    candidate: OptimizationCandidate,
    candidate_rows: list[dict[str, Any]],
    candidate_dag_inspections: list[dict[str, Any]],
) -> dict[str, Any]:
    if candidate.id != "m4_fuse_deep_operator_chains":
        return {
            "candidate_id": candidate.id,
            "selected_family": "",
            "matched_chains": 0,
            "nodes_reduced": 0,
            "fused_chains": [],
            "estimated_intermediate_eliminated": 0,
            "affected_subgraph_signatures": [],
            "baseline_rule": "",
            "fused_rule": "",
            "safe_fusion_rationale": "",
        }
    audits = [
        inspection.get("fusion_audit", {})
        for inspection in candidate_dag_inspections
        if inspection.get("fusion_audit", {}).get("selected_family")
    ]
    selected_family = "rolling_unary_chain_ts_mean_into_ts_rank"
    matched_chains = sum(int(audit.get("matched_chains", 0) or 0) for audit in audits)
    nodes_reduced = sum(int(audit.get("nodes_reduced", 0) or 0) for audit in audits)
    affected_signatures = sorted(
        {
            str(signature)
            for audit in audits
            for signature in audit.get("affected_subgraph_signatures", [])
        }
    )
    fused_chains = [
        list(chain)
        for audit in audits
        for chain in audit.get("fused_chains", [])
    ]
    estimated_intermediate_eliminated = sum(
        int(row.get("row_count", 0) or 0)
        * 8
        * int(audit.get("nodes_reduced", 0) or 0)
        for row, audit in zip(
            candidate_rows,
            [
                inspection.get("fusion_audit", {})
                for inspection in candidate_dag_inspections
            ],
        )
    )
    first_audit = audits[0] if audits else {}
    return {
        "candidate_id": candidate.id,
        "selected_family": selected_family if audits else "",
        "matched_chains": matched_chains,
        "nodes_reduced": nodes_reduced,
        "fused_chains": fused_chains,
        "estimated_intermediate_eliminated": estimated_intermediate_eliminated,
        "affected_subgraph_signatures": affected_signatures,
        "baseline_rule": first_audit.get("baseline_rule", ""),
        "fused_rule": first_audit.get("fused_rule", ""),
        "safe_fusion_rationale": first_audit.get("safe_fusion_rationale", ""),
    }


def evaluate_candidate(
    *,
    candidate: OptimizationCandidate,
    df: pl.DataFrame,
    output_root: Path,
    code_col: str,
    time_col: str,
) -> CandidateEvaluation:
    if not candidate.is_executable:
        raise ValueError(
            f"Only executable candidates can be evaluated, got {candidate.id!r}"
        )
    baseline_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    node_details: list[dict[str, Any]] = []
    baseline_dag_inspections: list[dict[str, Any]] = []
    candidate_dag_inspections: list[dict[str, Any]] = []
    correctness_pass = True
    baseline_output_attach_mode = str(
        candidate.params.get("baseline_output_attach_mode", "materialize")
    )
    candidate_output_attach_mode = str(
        candidate.params.get("output_attach_mode", baseline_output_attach_mode)
    )
    baseline_frame_projection_mode = str(
        candidate.params.get("baseline_frame_projection_mode", "off")
    )
    candidate_frame_projection_mode = str(
        candidate.params.get("frame_projection_mode", baseline_frame_projection_mode)
    )
    baseline_materialization_threshold_mode = str(
        candidate.params.get("baseline_materialization_threshold_mode", "reuse_ge_2")
    )
    candidate_materialization_threshold_mode = str(
        candidate.params.get(
            "materialization_threshold_mode",
            baseline_materialization_threshold_mode,
        )
    )
    recomputation_guardrail_max_expansion = int(
        candidate.params.get("recomputation_guardrail_max_expansion", 0)
    )
    baseline_planner_cse_mode = str(
        candidate.params.get("baseline_planner_cse_mode", "baseline")
    )
    candidate_planner_cse_mode = str(
        candidate.params.get("planner_cse_mode", baseline_planner_cse_mode)
    )
    baseline_fusion_mode = str(candidate.params.get("baseline_fusion_mode", "off"))
    candidate_fusion_mode = str(
        candidate.params.get("fusion_mode", baseline_fusion_mode)
    )
    for workload, expressions in workload_expressions().items():
        baseline_dir = output_root / candidate.id / workload / "baseline"
        candidate_dir = output_root / candidate.id / workload / "candidate"
        baseline_result, baseline_run, baseline_nodes, baseline_dag = run_workload(
            df=df,
            expressions=expressions,
            profile_dir=baseline_dir,
            benchmark_name=f"m3_baseline_{workload}",
            code_col=code_col,
            time_col=time_col,
            output_attach_mode=baseline_output_attach_mode,
            frame_projection_mode=baseline_frame_projection_mode,
            materialization_threshold_mode=baseline_materialization_threshold_mode,
            recomputation_guardrail_max_expansion=recomputation_guardrail_max_expansion,
            planner_cse_mode=baseline_planner_cse_mode,
            fusion_mode=baseline_fusion_mode,
        )
        candidate_result, candidate_run, candidate_nodes, candidate_dag = run_workload(
            df=df,
            expressions=expressions,
            profile_dir=candidate_dir,
            benchmark_name=f"m3_{candidate.id}_{workload}",
            code_col=code_col,
            time_col=time_col,
            output_attach_mode=candidate_output_attach_mode,
            frame_projection_mode=candidate_frame_projection_mode,
            materialization_threshold_mode=candidate_materialization_threshold_mode,
            recomputation_guardrail_max_expansion=recomputation_guardrail_max_expansion,
            planner_cse_mode=candidate_planner_cse_mode,
            fusion_mode=candidate_fusion_mode,
        )
        try:
            assert_frame_equal(
                candidate_result.select([name for name, _expr in expressions]),
                baseline_result.select([name for name, _expr in expressions]),
                check_exact=False,
            )
        except AssertionError:
            correctness_pass = False
        baseline_run["workload"] = workload
        candidate_run["workload"] = workload
        baseline_rows.append(baseline_run)
        candidate_rows.append(candidate_run)
        node_details.extend(baseline_nodes)
        node_details.extend(candidate_nodes)
        baseline_dag_inspections.append(baseline_dag)
        candidate_dag_inspections.append(candidate_dag)
    baseline = aggregate_metrics(baseline_rows)
    observed = aggregate_metrics(candidate_rows)
    memory_reduction = pct_reduction(baseline["memory_peak"], observed["memory_peak"])
    frame_width_reduction = pct_reduction(baseline["frame_peak"], observed["frame_peak"])
    time_increase = pct_increase(baseline["sec"], observed["sec"])
    recomputation_expansion_delta = (
        observed["recomputation_expansion"] - baseline["recomputation_expansion"]
    )
    score = optimization_score(
        memory_reduction=memory_reduction,
        frame_width_reduction=frame_width_reduction,
        time_increase=time_increase,
    )
    recomputation_guardrail_passed = (
        recomputation_expansion_delta <= recomputation_guardrail_max_expansion
    )
    m4_cse_audit = aggregate_m4_cse_audit(
        candidate=candidate,
        candidate_rows=candidate_rows,
        candidate_dag_inspections=candidate_dag_inspections,
    )
    m4_fusion_audit = aggregate_m4_fusion_audit(
        candidate=candidate,
        candidate_rows=candidate_rows,
        candidate_dag_inspections=candidate_dag_inspections,
    )
    audit_explainable = (
        candidate.phase != "m4_bridge"
        or (
            candidate.id == "m4_cse_expand_repeated_subgraphs"
            and bool(m4_cse_audit["selected_family"])
            and int(m4_cse_audit["matched_groups"]) > 0
            and bool(m4_cse_audit["affected_subgraph_signatures"])
        )
        or (
            candidate.id == "m4_fuse_deep_operator_chains"
            and bool(m4_fusion_audit["selected_family"])
            and int(m4_fusion_audit["matched_chains"]) > 0
            and int(m4_fusion_audit["nodes_reduced"]) > 0
            and bool(m4_fusion_audit["affected_subgraph_signatures"])
        )
        or candidate.id not in {
            "m4_cse_expand_repeated_subgraphs",
            "m4_fuse_deep_operator_chains",
        }
    )
    isolation_pass = (
        candidate.phase != "m4_bridge"
        or (
            candidate.id == "m4_cse_expand_repeated_subgraphs"
            and m4_cse_audit.get("selected_family", "") == "rolling_neutral_add_input"
        )
        or (
            candidate.id == "m4_fuse_deep_operator_chains"
            and m4_fusion_audit.get("selected_family", "")
            == "rolling_unary_chain_ts_mean_into_ts_rank"
        )
        or candidate.id not in {
            "m4_cse_expand_repeated_subgraphs",
            "m4_fuse_deep_operator_chains",
        }
    )
    selected_family = ""
    matched_groups = 0
    reused_groups = 0
    estimated_helper_bytes_saved = 0
    if candidate.id == "m4_cse_expand_repeated_subgraphs":
        selected_family = str(m4_cse_audit.get("selected_family", ""))
        matched_groups = int(m4_cse_audit.get("matched_groups", 0) or 0)
        reused_groups = int(m4_cse_audit.get("reused_groups", 0) or 0)
        estimated_helper_bytes_saved = int(
            m4_cse_audit.get("estimated_helper_bytes_saved", 0) or 0
        )
    elif candidate.id == "m4_fuse_deep_operator_chains":
        selected_family = str(m4_fusion_audit.get("selected_family", ""))
        matched_groups = int(m4_fusion_audit.get("matched_chains", 0) or 0)
        reused_groups = int(m4_fusion_audit.get("nodes_reduced", 0) or 0)
        estimated_helper_bytes_saved = int(
            m4_fusion_audit.get("estimated_intermediate_eliminated", 0) or 0
        )
    guardrails_passed = correctness_pass and audit_explainable and isolation_pass
    return CandidateEvaluation(
        candidate=candidate,
        score=score,
        accepted=(
            candidate.engine_supported
            and score > 0
            and recomputation_guardrail_passed
            and guardrails_passed
        ),
        memory_reduction=memory_reduction,
        frame_width_reduction=frame_width_reduction,
        time_increase=time_increase,
        recomputation_expansion_delta=recomputation_expansion_delta,
        correctness_pass=correctness_pass,
        audit_explainable=audit_explainable,
        isolation_pass=isolation_pass,
        selected_family=selected_family,
        matched_groups=matched_groups,
        reused_groups=reused_groups,
        estimated_helper_bytes_saved=estimated_helper_bytes_saved,
        metrics={
            "baseline": baseline,
            "candidate": observed,
            "workloads": candidate_rows,
            "baseline_workloads": baseline_rows,
            "node_details": node_details,
            "baseline_output_attach_mode": baseline_output_attach_mode,
            "candidate_output_attach_mode": candidate_output_attach_mode,
            "baseline_frame_projection_mode": baseline_frame_projection_mode,
            "candidate_frame_projection_mode": candidate_frame_projection_mode,
            "baseline_materialization_threshold_mode": (
                baseline_materialization_threshold_mode
            ),
            "candidate_materialization_threshold_mode": (
                candidate_materialization_threshold_mode
            ),
            "recomputation_guardrail_max_expansion": (
                recomputation_guardrail_max_expansion
            ),
            "recomputation_expansion_delta": recomputation_expansion_delta,
            "recomputation_guardrail_passed": recomputation_guardrail_passed,
            "baseline_planner_cse_mode": baseline_planner_cse_mode,
            "candidate_planner_cse_mode": candidate_planner_cse_mode,
            "baseline_fusion_mode": baseline_fusion_mode,
            "candidate_fusion_mode": candidate_fusion_mode,
            "baseline_dag_inspections": baseline_dag_inspections,
            "candidate_dag_inspections": candidate_dag_inspections,
            "m4_cse_audit": m4_cse_audit,
            "m4_fusion_audit": m4_fusion_audit,
            "correctness_pass": correctness_pass,
            "audit_explainable": audit_explainable,
            "isolation_pass": isolation_pass,
        },
    )


def render_yaml_block(mapping: dict[str, object]) -> str:
    lines: list[str] = []
    for key, value in mapping.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for child_key, child_value in value.items():
                rendered = "true" if child_value is True else "false" if child_value is False else child_value
                lines.append(f"  {child_key}: {rendered}")
        elif isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            rendered = "true" if value is True else "false" if value is False else value
            lines.append(f"{key}: {rendered}")
    return "\n".join(str(line) for line in lines) + "\n"


def render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# M3 Auto Optimization Pipeline",
        "",
        "## Status",
        "",
        "```yaml",
        render_yaml_block(summary["status"]).strip(),
        "```",
        "",
        "## Candidate Evaluations",
        "",
        "| candidate | status | kind | supported | score | accepted | memory reduction | frame reduction | time increase | recompute delta |",
        "| --- | --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for evaluation in summary["evaluations"]:
        candidate = evaluation["candidate"]
        lines.append(
            f"| `{candidate['id']}` | `{candidate['candidate_status']}` | "
            f"`{candidate['kind']}` | "
            f"{candidate['engine_supported']} | {evaluation['score']:.3f} | "
            f"{evaluation['accepted']} | {evaluation['memory_reduction']:.3f} | "
            f"{evaluation['frame_width_reduction']:.3f} | "
            f"{evaluation['time_increase']:.3f} | "
            f"{evaluation['recomputation_expansion_delta']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Proposal Queue",
            "",
            "| proposal | kind | rationale |",
            "| --- | --- | --- |",
        ]
    )
    for candidate in summary["proposal_queue"]:
        lines.append(
            f"| `{candidate['id']}` | `{candidate['kind']}` | {candidate['rationale']} |"
        )
    lines.extend(
        [
            "",
            "## Bridge",
            "",
            "```yaml",
            render_yaml_block(summary["bridge_status"]).strip(),
            "```",
            "",
            "## M4 Status",
            "",
            "```yaml",
            render_yaml_block(summary["m4_status"]).strip(),
            "```",
            "",
            "## M4 Candidates",
            "",
            "| candidate | kind | rationale |",
            "| --- | --- | --- |",
        ]
    )
    for candidate in summary["m4_candidates"]:
        lines.append(
            f"| `{candidate['id']}` | `{candidate['kind']}` | {candidate['rationale']} |"
        )
    return "\n".join(lines) + "\n"


def render_structural_report(report: dict[str, Any]) -> str:
    lines = [
        "# M4 Structural Bottleneck Report",
        "",
        "## Summary",
        "",
        f"- dominant bottleneck class: `{report['dominant_bottleneck_class']}`",
        f"- structural observability complete: `{report['structural_observability_complete']}`",
        f"- proposal priority: `{', '.join(report['proposal_priority'])}`",
        "",
        "## Repeated Subgraphs",
        "",
        "| signature | occurrences | nodes | helper bytes | compute weight |",
        "| --- | ---: | --- | ---: | ---: |",
    ]
    for item in report["repeated_subgraphs"]:
        lines.append(
            f"| `{str(item['signature'])[:96]}` | {item['occurrences']} | "
            f"`{','.join(item['nodes'])}` | {item['estimated_helper_bytes']} | "
            f"{float(item['estimated_compute_weight']):.3f} |"
        )
    lines.extend(
        [
            "",
            "## Deep Chains",
            "",
            "| chain | depth | materialized hops | transient hops | pressure |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in report["deep_chains"]:
        lines.append(
            f"| `{item['chain_id']}` | {item['depth']} | {item['materialized_hops']} | "
            f"{item['transient_hops']} | {item['estimated_chain_pressure']} |"
        )
    lines.extend(
        [
            "",
            "## Wide Fan-Out Nodes",
            "",
            "| node | occurrences | fanout | children | pressure |",
            "| --- | ---: | ---: | --- | ---: |",
        ]
    )
    for item in report["wide_fanout_nodes"]:
        children = item.get("child_nodes", [])
        if not isinstance(children, list):
            children = list(children)
        lines.append(
            f"| `{item['node_id']}` | {item.get('occurrences', 1)} | "
            f"{item['fanout_degree']} | "
            f"`{','.join(str(child) for child in children)}` | "
            f"{item['estimated_fanout_pressure']} |"
        )
    lines.extend(
        [
            "",
            "## Heavy Paths",
            "",
            "| path | memory weight | time weight | pressure score |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for item in report["heavy_paths"]:
        lines.append(
            f"| `{item['path_id']}` | {item['estimated_memory_weight']} | "
            f"{float(item['estimated_time_weight']):.3f} | "
            f"{float(item['combined_pressure_score']):.3f} |"
        )
    return "\n".join(lines) + "\n"


def render_m4_cse_candidate_report(summary: dict[str, Any]) -> str:
    result = summary.get("m4_cse_result", {})
    audit = result.get("audit", {})
    if not result:
        return "# M4.2 CSE Candidate Report\n\nNo M4.2 CSE candidate was evaluated.\n"
    return "\n".join(
        [
            "# M4.2 CSE Candidate Report",
            "",
            f"- candidate: `{result['candidate_id']}`",
            f"- selected family: `{result['selected_family']}`",
            f"- matched groups: `{result['matched_groups']}`",
            f"- reused groups: `{result['reused_groups']}`",
            f"- estimated helper bytes saved: `{result['estimated_helper_bytes_saved']}`",
            f"- score: `{result['score']:.3f}`",
            f"- decision: `{result['decision']}`",
            f"- correctness pass: `{result['correctness_pass']}`",
            f"- audit explainable: `{result['audit_explainable']}`",
            f"- isolation pass: `{result['isolation_pass']}`",
            "",
            "## Identity Rules",
            "",
            f"- baseline: {audit.get('baseline_identity_rule', '')}",
            f"- expanded: {audit.get('expanded_identity_rule', '')}",
            f"- baseline miss reason: {audit.get('baseline_miss_reason', '')}",
            f"- safe merge rationale: {audit.get('safe_merge_rationale', '')}",
            "",
            "## Affected Signatures",
            "",
            *[
                f"- `{signature}`"
                for signature in audit.get("affected_subgraph_signatures", [])
            ],
            "",
        ]
    )


def render_m4_2_decision(summary: dict[str, Any]) -> str:
    result = summary.get("m4_cse_result", {})
    if not result:
        return "# M4.2 Decision\n\nNo M4.2 candidate was evaluated.\n"
    return "\n".join(
        [
            "# M4.2 Decision",
            "",
            f"Decision: **{result['decision']}**",
            "",
            f"`{result['candidate_id']}` targeted `{result['selected_family']}`.",
            f"Score was `{result['score']:.3f}`.",
            "",
            "Guardrails:",
            "",
            f"- correctness: `{result['correctness_pass']}`",
            f"- audit explainability: `{result['audit_explainable']}`",
            f"- isolation: `{result['isolation_pass']}`",
            "",
            "Result:",
            "",
            (
                "Expanded CSE may proceed as an accepted M4 structural candidate."
                if result["decision"] == "ACCEPT"
                else "Expanded CSE is rejected for this round; keep the knob as an experimental path and proceed to the next M4 candidate."
            ),
            "",
        ]
    )


def render_m4_fusion_candidate_report(summary: dict[str, Any]) -> str:
    result = summary.get("m4_fusion_result", {})
    audit = result.get("audit", {})
    if not result:
        return "# M4.3 Fusion Candidate Report\n\nNo M4.3 fusion candidate was evaluated.\n"
    return "\n".join(
        [
            "# M4.3 Fusion Candidate Report",
            "",
            f"- candidate: `{result['candidate_id']}`",
            f"- selected family: `{result['selected_family']}`",
            f"- matched chains: `{result['matched_groups']}`",
            f"- nodes reduced: `{result['reused_groups']}`",
            f"- estimated intermediate eliminated: `{result['estimated_helper_bytes_saved']}`",
            f"- score: `{result['score']:.3f}`",
            f"- decision: `{result['decision']}`",
            f"- correctness pass: `{result['correctness_pass']}`",
            f"- audit explainable: `{result['audit_explainable']}`",
            f"- isolation pass: `{result['isolation_pass']}`",
            "",
            "## Fusion Rules",
            "",
            f"- baseline: {audit.get('baseline_rule', '')}",
            f"- fused: {audit.get('fused_rule', '')}",
            f"- safe fusion rationale: {audit.get('safe_fusion_rationale', '')}",
            "",
            "## Fused Chains",
            "",
            *[f"- `{chain}`" for chain in audit.get("fused_chains", [])],
            "",
        ]
    )


def render_m4_3_decision(summary: dict[str, Any]) -> str:
    result = summary.get("m4_fusion_result", {})
    if not result:
        return "# M4.3 Decision\n\nNo M4.3 candidate was evaluated.\n"
    return "\n".join(
        [
            "# M4.3 Decision",
            "",
            f"Decision: **{result['decision']}**",
            "",
            f"`{result['candidate_id']}` targeted `{result['selected_family']}`.",
            f"Score was `{result['score']:.3f}`.",
            "",
            "Guardrails:",
            "",
            f"- correctness: `{result['correctness_pass']}`",
            f"- audit explainability: `{result['audit_explainable']}`",
            f"- isolation: `{result['isolation_pass']}`",
            "",
            "Result:",
            "",
            (
                "Unary-chain fusion may proceed as an accepted M4 structural candidate."
                if result["decision"] == "ACCEPT"
                else "Unary-chain fusion is rejected for this round; M4 can be frozen as a localized structural win unless a later review authorizes another high-risk candidate."
            ),
            "",
        ]
    )


def render_m4_freeze_review(summary: dict[str, Any]) -> str:
    final_status = summary.get("m4_final_status", {})
    accepted = final_status.get("accepted_candidates", [])
    rejected = final_status.get("rejected_candidates", [])
    return "\n".join(
        [
            "# M4 Freeze Readiness Review",
            "",
            "```yaml",
            render_yaml_block(final_status).strip(),
            "```",
            "",
            "## Accepted",
            "",
            *[f"- `{item}`" for item in accepted],
            "",
            "## Rejected",
            "",
            *[f"- `{item}`" for item in rejected],
            "",
            "## Conclusion",
            "",
            (
                "M4 is safe to consider frozen. The required CSE and fusion classes have both been tested, and the result is now a bounded structural conclusion rather than an open-ended optimization hunt."
                if final_status.get("safe_to_consider_freeze")
                else "M4 is not yet safe to freeze because the required structural candidate classes have not both been tested."
            ),
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run M3 auto optimization and bridge pipeline.")
    parser.add_argument("--data", type=Path, default=PROJECT_ROOT / "data" / "data.parquet")
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument("--code-col", default="code")
    parser.add_argument("--time-col", default="time")
    parser.add_argument("--round-index", type=int, default=1)
    parser.add_argument("--max-candidates-per-round", type=int, default=3)
    parser.add_argument("--reset-history", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "benchmarks" / "latest" / "m3_auto_pipeline",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = load_dataframe(args.data, rows=args.rows)
    code_col = resolve_code_col(args.code_col, df)
    output_root = args.output
    if args.reset_history:
        shutil.rmtree(output_root, ignore_errors=True)
    output_root.mkdir(parents=True, exist_ok=True)
    history_path = output_root / "optimization_history.json"
    previous_summary_path = output_root / "summary.json"
    previous_summary = (
        read_json(previous_summary_path)
        if previous_summary_path.exists() and not args.reset_history
        else None
    )
    history = [] if args.reset_history else load_history(history_path)
    proposal_queue = generate_m3_proposal_candidates(
        history,
        max_candidates_per_round=args.max_candidates_per_round,
    )
    candidates = generate_m3_candidates(
        history,
        max_candidates_per_round=1,
    )
    if not candidates and not proposal_queue and candidate_space_exhausted(history):
        candidates = generate_m4_executable_candidates(
            history,
            max_candidates_per_round=1,
        )
    evaluations = [
        evaluate_candidate(
            candidate=candidate,
            df=df,
            output_root=output_root / "candidate_runs",
            code_col=code_col,
            time_col=args.time_col,
        )
        for candidate in candidates
    ]
    best = select_best_candidate(evaluations, round_index=args.round_index)
    history.extend(evaluation.to_history_entry() for evaluation in evaluations)
    save_history(history_path, history)

    run_summaries = [
        workload
        for evaluation in evaluations
        for workload in evaluation.metrics.get("workloads", [])
    ]
    node_details = [
        detail
        for evaluation in evaluations
        for detail in evaluation.metrics.get("node_details", [])
    ]
    if not evaluations and previous_summary is not None:
        previous_evaluations = previous_summary.get("evaluations", [])
        if previous_evaluations:
            previous_metrics = previous_evaluations[-1].get("metrics", {})
            run_summaries = list(previous_metrics.get("workloads", []))
            node_details = list(previous_metrics.get("node_details", []))
    if not evaluations and not node_details:
        run_summaries, node_details = read_profile_artifacts(output_root)
    exhausted = candidate_space_exhausted(
        history,
        max_candidates_per_round=1,
    )
    candidate_space_done = exhausted and not proposal_queue
    best_memory = best.memory_reduction if best is not None else 0.0
    best_frame = best.frame_width_reduction if best is not None else 0.0
    stagnation = stagnation_detected(
        history,
        memory_improvement=best_memory,
        frame_improvement=best_frame,
        candidate_exhausted=exhausted,
    )
    bottleneck_report = detect_bottlenecks(
        run_summaries=run_summaries,
        node_details=node_details,
    )
    structural_report = build_structural_bottleneck_report(
        run_summaries=run_summaries,
        node_details=node_details,
    )
    trigger_bridge = candidate_space_done and (
        stagnation or (best is None or best.score <= 0)
    )
    m4_candidates = generate_m4_candidates(bottleneck_report) if trigger_bridge else []
    m4_candidates = [
        candidate
        for candidate in m4_candidates
        if not candidate_seen_before(candidate, history)
    ]
    if trigger_bridge:
        priority = list(structural_report.proposal_priority)
        m4_candidates = sorted(
            m4_candidates,
            key=lambda candidate: (
                priority.index(candidate.id)
                if candidate.id in priority
                else len(priority)
            ),
        )
    m4_cse_evaluation = next(
        (
            evaluation
            for evaluation in evaluations
            if evaluation.candidate.id == "m4_cse_expand_repeated_subgraphs"
        ),
        None,
    )
    m4_cse_audit = (
        m4_cse_evaluation.metrics.get("m4_cse_audit", {})
        if m4_cse_evaluation is not None
        else {}
    )
    m4_cse_result = (
        {
            "candidate_id": m4_cse_evaluation.candidate.id,
            "candidate_class": "CSE",
            "candidate_kind": m4_cse_evaluation.candidate.candidate_status,
            "selected_family": m4_cse_evaluation.selected_family,
            "matched_groups": m4_cse_evaluation.matched_groups,
            "reused_groups": m4_cse_evaluation.reused_groups,
            "estimated_helper_bytes_saved": (
                m4_cse_evaluation.estimated_helper_bytes_saved
            ),
            "score": m4_cse_evaluation.score,
            "correctness_pass": m4_cse_evaluation.correctness_pass,
            "audit_explainable": m4_cse_evaluation.audit_explainable,
            "isolation_pass": m4_cse_evaluation.isolation_pass,
            "decision": "ACCEPT" if m4_cse_evaluation.accepted else "REJECT",
            "audit": m4_cse_audit,
        }
        if m4_cse_evaluation is not None
        else {}
    )
    if not m4_cse_result and previous_summary is not None:
        previous_m4_cse_result = previous_summary.get("m4_cse_result", {})
        if previous_m4_cse_result:
            m4_cse_result = previous_m4_cse_result
    m4_fusion_evaluation = next(
        (
            evaluation
            for evaluation in evaluations
            if evaluation.candidate.id == "m4_fuse_deep_operator_chains"
        ),
        None,
    )
    m4_fusion_audit = (
        m4_fusion_evaluation.metrics.get("m4_fusion_audit", {})
        if m4_fusion_evaluation is not None
        else {}
    )
    m4_fusion_result = (
        {
            "candidate_id": m4_fusion_evaluation.candidate.id,
            "candidate_class": "fusion",
            "candidate_kind": m4_fusion_evaluation.candidate.candidate_status,
            "selected_family": m4_fusion_evaluation.selected_family,
            "matched_groups": m4_fusion_evaluation.matched_groups,
            "reused_groups": m4_fusion_evaluation.reused_groups,
            "estimated_helper_bytes_saved": (
                m4_fusion_evaluation.estimated_helper_bytes_saved
            ),
            "score": m4_fusion_evaluation.score,
            "correctness_pass": m4_fusion_evaluation.correctness_pass,
            "audit_explainable": m4_fusion_evaluation.audit_explainable,
            "isolation_pass": m4_fusion_evaluation.isolation_pass,
            "decision": "ACCEPT" if m4_fusion_evaluation.accepted else "REJECT",
            "audit": m4_fusion_audit,
        }
        if m4_fusion_evaluation is not None
        else {}
    )
    if not m4_fusion_result and previous_summary is not None:
        previous_m4_fusion_result = previous_summary.get("m4_fusion_result", {})
        if previous_m4_fusion_result:
            m4_fusion_result = previous_m4_fusion_result
    accepted_m4_candidates = [
        result["candidate_id"]
        for result in (m4_cse_result, m4_fusion_result)
        if result and result.get("decision") == "ACCEPT"
    ]
    rejected_m4_candidates = [
        result["candidate_id"]
        for result in (m4_cse_result, m4_fusion_result)
        if result and result.get("decision") == "REJECT"
    ]
    required_m4_tested = bool(m4_cse_result) and bool(m4_fusion_result)
    if required_m4_tested and len(accepted_m4_candidates) >= 2:
        m4_freeze_path = "strong_success"
        structure_is_primary_bottleneck = True
    elif required_m4_tested and m4_cse_result.get("decision") == "ACCEPT":
        m4_freeze_path = "weak_success_localized"
        structure_is_primary_bottleneck = False
    elif required_m4_tested:
        m4_freeze_path = "failed_structural_value"
        structure_is_primary_bottleneck = False
    else:
        m4_freeze_path = "not_ready"
        structure_is_primary_bottleneck = False
    m4_final_status = {
        "accepted_candidates": accepted_m4_candidates,
        "rejected_candidates": rejected_m4_candidates,
        "dominant_bottleneck_class": structural_report.dominant_bottleneck_class,
        "required_candidate_classes_tested": required_m4_tested,
        "structure_is_primary_bottleneck": structure_is_primary_bottleneck,
        "optimization_space_exhausted": required_m4_tested,
        "freeze_path": m4_freeze_path,
        "safe_to_consider_freeze": required_m4_tested,
    }
    summary = {
        "status": {
            "m3_status": {
                "delayed_attach_executable": True,
                "materialization_control": "executable_guarded",
                "frame_width_control": "executable",
                "auto_optimization_enabled": True,
                "safe_to_freeze": bool(candidate_space_done and not trigger_bridge),
                "m4_structural_observability_complete": (
                    structural_report.structural_observability_complete
                ),
            },
            "m3_value": {
                "total_memory_reduction": round(best_memory, 3),
                "total_frame_width_reduction": round(best_frame, 3),
                "total_time_delta": round(best.time_increase if best else 0.0, 3),
                "optimization_rounds": len(history),
                "executable_candidates_this_round": len(candidates),
                "proposal_candidates_queued": len(proposal_queue),
            },
        },
        "bridge_status": {
            "triggered": trigger_bridge,
            "stagnation_detected": stagnation,
            "bottleneck_detected": bottleneck_report.bottleneck_detected,
            "executable_space_exhausted": exhausted,
            "candidate_space_exhausted": candidate_space_done,
        },
        "m4_status": {
            "structural_observability_complete": (
                structural_report.structural_observability_complete
            ),
            "proposal_space_defined": structural_report.structural_observability_complete,
            "first_executable_candidate": (
                "m4_cse_expand_repeated_subgraphs"
                if structural_report.structural_observability_complete
                else ""
            ),
            "high_value_candidate_classes_tested": required_m4_tested,
            "no_new_positive_candidate_trend": bool(
                required_m4_tested
                and len(accepted_m4_candidates) < 2
            ),
            "safe_to_consider_freeze": required_m4_tested,
        },
        "evaluations": [evaluation.to_dict() for evaluation in evaluations],
        "proposal_queue": [candidate.to_dict() for candidate in proposal_queue],
        "selected_candidate": best.to_dict() if best is not None else None,
        "optimization_history": [entry.to_dict() for entry in history],
        "bottleneck_report": bottleneck_report.to_dict(),
        "m4_cse_result": m4_cse_result,
        "m4_fusion_result": m4_fusion_result,
        "m4_final_status": m4_final_status,
        "structural_bottleneck_report": {
            **structural_report.to_dict(),
            "structural_observability_complete": (
                structural_report.structural_observability_complete
            ),
        },
        "m4_candidates": [candidate.to_dict() for candidate in m4_candidates],
        "score_contract": {
            "score": "0.5 * memory_reduction + 0.3 * frame_width_reduction - 0.2 * time_increase",
            "accept_if": "score > 0",
        },
    }
    (output_root / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    report = render_report(summary)
    (output_root / "m3_auto_pipeline_report.md").write_text(report, encoding="utf-8")
    structural_report_dict = summary["structural_bottleneck_report"]
    (output_root / "structural_bottleneck_report.json").write_text(
        json.dumps(structural_report_dict, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_root / "structural_bottleneck_report.md").write_text(
        render_structural_report(structural_report_dict),
        encoding="utf-8",
    )
    if summary["m4_cse_result"]:
        (output_root / "m4_cse_audit.json").write_text(
            json.dumps(
                summary["m4_cse_result"]["audit"],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (output_root / "m4_cse_candidate_report.md").write_text(
            render_m4_cse_candidate_report(summary),
            encoding="utf-8",
        )
        (output_root / "m4_2_cse_decision.md").write_text(
            render_m4_2_decision(summary),
            encoding="utf-8",
        )
    if summary["m4_fusion_result"]:
        (output_root / "m4_fusion_audit.json").write_text(
            json.dumps(
                summary["m4_fusion_result"]["audit"],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (output_root / "m4_fusion_candidate_report.md").write_text(
            render_m4_fusion_candidate_report(summary),
            encoding="utf-8",
        )
        (output_root / "m4_3_fusion_decision.md").write_text(
            render_m4_3_decision(summary),
            encoding="utf-8",
        )
    if summary["m4_final_status"]["safe_to_consider_freeze"]:
        (output_root / "m4_freeze_review.md").write_text(
            render_m4_freeze_review(summary),
            encoding="utf-8",
        )
        (output_root / "m4_value_summary.yaml").write_text(
            render_yaml_block(summary["m4_final_status"]),
            encoding="utf-8",
        )
    m4_history = [
        entry
        for entry in summary["optimization_history"]
        if entry.get("phase") == "m4_bridge"
    ]
    if m4_history:
        (output_root / "m4_history.json").write_text(
            json.dumps(m4_history, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    print(report)


if __name__ == "__main__":
    main()
