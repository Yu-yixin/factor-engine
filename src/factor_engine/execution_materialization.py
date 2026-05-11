from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MaterializationGuardrailSummary:
    candidate_count: int
    allowed_count: int
    blocked_count: int
    expansion_estimate: int
    expansion_actual_delta: int
    estimated_unshared_compute_calls: int


def materialized_consumer_count(node: Any) -> int:
    return max(node.occurrence_count, len(node.consumers) + len(node.output_names))


def recomputation_guardrail_candidates(dag_nodes) -> list[Any]:
    return [
        node
        for node in dag_nodes
        if node.default_materialize and node.recomputation_expansion_if_inline > 0
    ]


def build_materialization_guardrail_summary(dag_nodes) -> MaterializationGuardrailSummary:
    nodes = tuple(dag_nodes)
    guardrail_candidates = recomputation_guardrail_candidates(nodes)
    return MaterializationGuardrailSummary(
        candidate_count=len(guardrail_candidates),
        allowed_count=sum(1 for node in guardrail_candidates if node.recomputation_guardrail_pass),
        blocked_count=sum(1 for node in guardrail_candidates if not node.recomputation_guardrail_pass),
        expansion_estimate=sum(
            node.recomputation_expansion_if_inline
            for node in guardrail_candidates
            if node.recomputation_guardrail_pass
        ),
        expansion_actual_delta=sum(
            node.recomputation_expansion_if_inline
            for node in guardrail_candidates
            if not node.materialize
        ),
        estimated_unshared_compute_calls=sum(
            node.occurrence_count for node in nodes if node.materialize
        ),
    )


def apply_dag_materialization_runtime_summary(runtime: Any, batch_dag: Any) -> None:
    runtime.ast_node_count = batch_dag.ast_node_count
    runtime.dag_node_count = batch_dag.dag_node_count
    runtime.deduplicated_node_count = batch_dag.deduplicated_node_count
    runtime.shared_node_count = batch_dag.shared_node_count
    runtime.materialized_node_count = batch_dag.materialized_node_count
    runtime.expensive_node_count = batch_dag.expensive_node_count

    summary = build_materialization_guardrail_summary(batch_dag.nodes)
    runtime.estimated_unshared_compute_calls = summary.estimated_unshared_compute_calls
    runtime.recomputation_guardrail_candidate_count = summary.candidate_count
    runtime.recomputation_guardrail_allowed_count = summary.allowed_count
    runtime.recomputation_guardrail_blocked_count = summary.blocked_count
    runtime.recomputation_expansion_estimate = summary.expansion_estimate
    runtime.recomputation_expansion_actual_delta = summary.expansion_actual_delta
