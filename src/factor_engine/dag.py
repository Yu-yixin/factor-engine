from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
import time
from typing import Literal

from factor_engine.ast_nodes import (
    BinaryOpNode,
    BooleanNode,
    CallNode,
    Expr,
    ListNode,
    NumberNode,
    UnaryOpNode,
    VariableNode,
)
from factor_engine.registry import get_function_spec


NodeCostClass = Literal["cheap", "medium", "expensive"]
MaterializationKind = Literal["final", "shared_intermediate", "ephemeral"]
MaterializationReason = Literal[
    "none",
    "shared_reuse",
    "path_normalization",
    "shared_reuse_and_path_normalization",
]
MaterializationEligibility = Literal[
    "inline_required",
    "materialize_for_reuse",
    "materialize_for_path_normalization",
    "materialize_for_both",
]


@dataclass(frozen=True)
class ExpandedCseAudit:
    selected_family: str = ""
    baseline_identity_rule: str = ""
    expanded_identity_rule: str = ""
    matched_groups: int = 0
    reused_groups: int = 0
    merged_nodes: tuple[str, ...] = ()
    estimated_helper_bytes_saved: int = 0
    affected_subgraph_signatures: tuple[str, ...] = ()
    baseline_miss_reason: str = ""
    safe_merge_rationale: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "selected_family": self.selected_family,
            "baseline_identity_rule": self.baseline_identity_rule,
            "expanded_identity_rule": self.expanded_identity_rule,
            "matched_groups": self.matched_groups,
            "reused_groups": self.reused_groups,
            "merged_nodes": self.merged_nodes,
            "estimated_helper_bytes_saved": self.estimated_helper_bytes_saved,
            "affected_subgraph_signatures": self.affected_subgraph_signatures,
            "baseline_miss_reason": self.baseline_miss_reason,
            "safe_merge_rationale": self.safe_merge_rationale,
        }


@dataclass(frozen=True)
class FusionAudit:
    selected_family: str = ""
    baseline_rule: str = ""
    fused_rule: str = ""
    matched_chains: int = 0
    fused_chains: tuple[tuple[str, ...], ...] = ()
    nodes_reduced: int = 0
    estimated_intermediate_eliminated: int = 0
    affected_subgraph_signatures: tuple[str, ...] = ()
    safe_fusion_rationale: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "selected_family": self.selected_family,
            "baseline_rule": self.baseline_rule,
            "fused_rule": self.fused_rule,
            "matched_chains": self.matched_chains,
            "fused_chains": self.fused_chains,
            "nodes_reduced": self.nodes_reduced,
            "estimated_intermediate_eliminated": self.estimated_intermediate_eliminated,
            "affected_subgraph_signatures": self.affected_subgraph_signatures,
            "safe_fusion_rationale": self.safe_fusion_rationale,
        }


@dataclass(frozen=True)
class DagNode:
    node_id: str
    identity: tuple
    node_type: str
    label: str
    dependencies: tuple[str, ...]
    consumers: tuple[str, ...]
    output_names: tuple[str, ...]
    occurrence_count: int
    cost_class: NodeCostClass
    is_expensive: bool
    is_shared: bool
    materialization_kind: MaterializationKind
    materialization_reason: MaterializationReason
    materialization_eligibility: MaterializationEligibility
    materialize: bool
    default_materialize: bool
    recomputation_expansion_if_inline: int
    recomputation_guardrail_pass: bool
    share_decision: str
    share_reason: str
    canonical_repr: str
    expr: Expr


@dataclass(frozen=True)
class NodeLifecyclePlan:
    node_id: str
    materialization_reason: MaterializationReason
    producer_step: int | None
    consumer_steps: tuple[int, ...]
    last_use_step: int | None
    ref_count_initial: int
    drop_candidate: bool
    drop_blocker_reason: str
    restore_assemble_step: int | None = None
    append_step: int | None = None
    finalize_step: int | None = None
    batch_end_step: int | None = None
    structural_release_lag_steps: int | None = None
    retained_past_last_read: bool = False
    finalize_retention_lag_steps: int | None = None
    potential_live_bytes_step_savings: int = 0
    node_depth: int = 0
    parent_node_id: str | None = None
    dependency_chain: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExpressionDag:
    nodes: tuple[DagNode, ...]
    output_node_ids: tuple[str, ...]
    ast_node_count: int
    dag_node_count: int
    deduplicated_node_count: int
    shared_node_count: int
    materialized_node_count: int
    expensive_node_count: int
    lifecycle_plans: tuple[NodeLifecyclePlan, ...] = ()
    expanded_cse_audit: ExpandedCseAudit = ExpandedCseAudit()
    fusion_audit: FusionAudit = FusionAudit()

    def node_by_id(self) -> dict[str, DagNode]:
        return {node.node_id: node for node in self.nodes}

    def lifecycle_plan_by_node_id(self) -> dict[str, NodeLifecyclePlan]:
        return {plan.node_id: plan for plan in self.lifecycle_plans}

    def to_inspection(self) -> dict[str, object]:
        return {
            "ast_node_count": self.ast_node_count,
            "dag_node_count": self.dag_node_count,
            "deduplicated_node_count": self.deduplicated_node_count,
            "shared_node_count": self.shared_node_count,
            "materialized_node_count": self.materialized_node_count,
            "expensive_node_count": self.expensive_node_count,
            "output_node_ids": self.output_node_ids,
            "lifecycle_plans": [
                {
                    "node_id": plan.node_id,
                    "materialization_reason": plan.materialization_reason,
                    "producer_step": plan.producer_step,
                    "consumer_steps": plan.consumer_steps,
                    "last_use_step": plan.last_use_step,
                    "ref_count_initial": plan.ref_count_initial,
                    "drop_candidate": plan.drop_candidate,
                    "drop_blocker_reason": plan.drop_blocker_reason,
                    "restore_assemble_step": plan.restore_assemble_step,
                    "append_step": plan.append_step,
                    "finalize_step": plan.finalize_step,
                    "batch_end_step": plan.batch_end_step,
                    "structural_release_lag_steps": plan.structural_release_lag_steps,
                    "retained_past_last_read": plan.retained_past_last_read,
                    "finalize_retention_lag_steps": plan.finalize_retention_lag_steps,
                    "potential_live_bytes_step_savings": (
                        plan.potential_live_bytes_step_savings
                    ),
                    "node_depth": plan.node_depth,
                    "parent_node_id": plan.parent_node_id,
                    "dependency_chain": plan.dependency_chain,
                }
                for plan in self.lifecycle_plans
            ],
            "expanded_cse_audit": self.expanded_cse_audit.to_dict(),
            "fusion_audit": self.fusion_audit.to_dict(),
            "deduplicated_nodes": [
                {
                    "node_id": node.node_id,
                    "label": node.label,
                    "occurrence_count": node.occurrence_count,
                    "identity": node.identity,
                    "consumers": node.consumers,
                    "outputs": node.output_names,
                    "cost_class": node.cost_class,
                    "share_decision": node.share_decision,
                    "share_reason": node.share_reason,
                    "materialization_kind": node.materialization_kind,
                    "materialization_reason": node.materialization_reason,
                    "materialization_eligibility": node.materialization_eligibility,
                    "recomputation_expansion_if_inline": (
                        node.recomputation_expansion_if_inline
                    ),
                    "recomputation_guardrail_pass": node.recomputation_guardrail_pass,
                    "lifecycle": self._lifecycle_inspection_for_node(node.node_id),
                }
                for node in self.nodes
                if node.occurrence_count > 1
            ],
            "nodes": [
                {
                    "node_id": node.node_id,
                    "label": node.label,
                    "identity": node.identity,
                    "dependencies": node.dependencies,
                    "consumers": node.consumers,
                    "outputs": node.output_names,
                    "occurrence_count": node.occurrence_count,
                    "cost_class": node.cost_class,
                    "is_shared": node.is_shared,
                    "materialize": node.materialize,
                    "materialization_kind": node.materialization_kind,
                    "materialization_reason": node.materialization_reason,
                    "materialization_eligibility": node.materialization_eligibility,
                    "recomputation_expansion_if_inline": (
                        node.recomputation_expansion_if_inline
                    ),
                    "recomputation_guardrail_pass": node.recomputation_guardrail_pass,
                    "share_decision": node.share_decision,
                    "share_reason": node.share_reason,
                    "lifecycle": self._lifecycle_inspection_for_node(node.node_id),
                }
                for node in self.nodes
            ],
        }

    def _lifecycle_inspection_for_node(self, node_id: str) -> dict[str, object] | None:
        plan = self.lifecycle_plan_by_node_id().get(node_id)
        if plan is None:
            return None
        return {
            "producer_step": plan.producer_step,
            "consumer_steps": plan.consumer_steps,
            "last_use_step": plan.last_use_step,
            "ref_count_initial": plan.ref_count_initial,
            "drop_candidate": plan.drop_candidate,
            "drop_blocker_reason": plan.drop_blocker_reason,
            "restore_assemble_step": plan.restore_assemble_step,
            "append_step": plan.append_step,
            "finalize_step": plan.finalize_step,
            "batch_end_step": plan.batch_end_step,
            "structural_release_lag_steps": plan.structural_release_lag_steps,
            "retained_past_last_read": plan.retained_past_last_read,
            "finalize_retention_lag_steps": plan.finalize_retention_lag_steps,
            "potential_live_bytes_step_savings": plan.potential_live_bytes_step_savings,
            "node_depth": plan.node_depth,
            "parent_node_id": plan.parent_node_id,
            "dependency_chain": plan.dependency_chain,
        }


@dataclass
class NodeResultStoreEntry:
    node_id: str
    identity: tuple
    materialization_kind: MaterializationKind
    materialization_reason: MaterializationReason = "none"
    materialization_eligibility: MaterializationEligibility = "inline_required"
    output_name: str | None = None
    column_name: str | None = None
    is_final_output: bool = False


@dataclass
class NodeExecutionStats:
    node_id: str
    identity: tuple
    materialization_kind: MaterializationKind
    materialization_reason: MaterializationReason
    materialization_eligibility: MaterializationEligibility
    consumer_count: int
    reuse_consumer_count: int = 0
    compute_count: int = 0
    node_store_read_count: int = 0
    compute_time_ms: float = 0.0
    store_write_time_ms: float = 0.0
    store_hit_time_ms: float = 0.0
    materialized_at_step: int | None = None
    first_read_step: int | None = None
    last_read_step: int | None = None
    theoretical_release_step: int | None = None
    retained_until_end: bool = True
    bytes_estimate: int = 0
    ref_count_initial: int = 0
    ref_count_remaining: int = 0
    active_drop_eligible: bool = False
    drop_expected_step: int | None = None
    dropped_at_step: int | None = None
    drop_delay_steps: int | None = None
    drop_reason: str = ""
    drop_missed: bool = False
    drop_miss_reason: str = ""
    helper_column_name: str | None = None
    helper_column_created_step: int | None = None
    helper_last_use_step: int | None = None
    helper_retained_until_end: bool = True
    helper_structural_lag_steps: int = 0
    helper_bytes_estimate: int = 0
    helper_potential_bytes_step_savings: int = 0
    helper_lifecycle_state: str = ""
    helper_drop_blocker_reason: str = ""
    helper_depth: int = 0
    parent_helper_column_name: str | None = None
    child_helper_columns: tuple[str, ...] = ()
    helper_logical_last_use_step: int | None = None
    helper_structural_dependency_end_step: int | None = None
    helper_drop_candidate: bool = False
    helper_drop_candidate_kind: str = ""
    helper_logical_death_step: int | None = None
    helper_drop_safe_step: int | None = None
    helper_drop_revalidated: bool = False
    helper_dropped_at_step: int | None = None
    helper_drop_delay_steps: int | None = None
    helper_drop_reason: str = ""
    helper_drop_missed: bool = False
    helper_drop_miss_reason: str = ""
    nested_helper_candidate: bool = False
    nested_helper_trace_events: tuple[str, ...] = ()
    nested_helper_miss_reason: str = ""
    recomputation_expansion_if_inline: int = 0
    recomputation_guardrail_pass: bool = False

    @property
    def hit_count(self) -> int:
        return self.node_store_read_count


class NodeResultStore:
    def __init__(self) -> None:
        self.entries: OrderedDict[str, NodeResultStoreEntry] = OrderedDict()
        self.stats: OrderedDict[str, NodeExecutionStats] = OrderedDict()
        self.peak_entry_count = 0

    def register_policy(
        self,
        *,
        node_id: str,
        identity: tuple,
        materialization_kind: MaterializationKind,
        consumer_count: int,
        materialization_reason: MaterializationReason = "none",
        materialization_eligibility: MaterializationEligibility = "inline_required",
        recomputation_expansion_if_inline: int = 0,
        recomputation_guardrail_pass: bool = False,
    ) -> None:
        stats = self.stats.setdefault(
            node_id,
            NodeExecutionStats(
                node_id=node_id,
                identity=identity,
                materialization_kind=materialization_kind,
                materialization_reason=materialization_reason,
                materialization_eligibility=materialization_eligibility,
                consumer_count=consumer_count,
            ),
        )
        stats.recomputation_expansion_if_inline = recomputation_expansion_if_inline
        stats.recomputation_guardrail_pass = recomputation_guardrail_pass

    def put(self, entry: NodeResultStoreEntry) -> None:
        self.entries[entry.node_id] = entry
        self.peak_entry_count = max(self.peak_entry_count, len(self.entries))

    def put_materialized(
        self,
        entry: NodeResultStoreEntry,
        *,
        compute_time_ms: float,
        store_write_time_ms: float,
        materialized_at_step: int | None = None,
        theoretical_release_step: int | None = None,
        bytes_estimate: int = 0,
        ref_count_initial: int = 0,
        active_drop_eligible: bool = False,
    ) -> None:
        self.put(entry)
        stats = self.stats.setdefault(
            entry.node_id,
            NodeExecutionStats(
                node_id=entry.node_id,
                identity=entry.identity,
                materialization_kind=entry.materialization_kind,
                materialization_reason=entry.materialization_reason,
                materialization_eligibility=entry.materialization_eligibility,
                consumer_count=0,
            ),
        )
        stats.compute_count += 1
        stats.compute_time_ms += compute_time_ms
        stats.store_write_time_ms += store_write_time_ms
        stats.materialized_at_step = materialized_at_step
        stats.theoretical_release_step = theoretical_release_step
        stats.bytes_estimate = bytes_estimate
        stats.helper_column_name = entry.column_name
        stats.helper_column_created_step = materialized_at_step
        stats.helper_bytes_estimate = bytes_estimate
        stats.ref_count_initial = ref_count_initial
        stats.ref_count_remaining = ref_count_initial
        stats.active_drop_eligible = active_drop_eligible
        stats.drop_expected_step = theoretical_release_step

    def get(self, node_id: str) -> NodeResultStoreEntry | None:
        return self.entries.get(node_id)

    def get_materialized(self, node_id: str) -> NodeResultStoreEntry | None:
        started_at = time.perf_counter()
        entry = self.entries.get(node_id)
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        if entry is not None and entry.column_name is not None:
            stats = self.stats.get(node_id)
            if stats is not None:
                stats.node_store_read_count += 1
                stats.reuse_consumer_count += 1
                stats.store_hit_time_ms += elapsed_ms
            return entry
        return None

    def record_reads(
        self,
        node_id: str,
        *,
        read_count: int,
        consumer_count: int,
        read_step: int | None = None,
    ) -> None:
        if read_count <= 0 and consumer_count <= 0:
            return
        stats = self.stats.get(node_id)
        if stats is not None:
            stats.node_store_read_count += max(0, read_count)
            stats.reuse_consumer_count += max(0, consumer_count)
            if read_step is not None and (read_count > 0 or consumer_count > 0):
                if stats.first_read_step is None:
                    stats.first_read_step = read_step
                stats.last_read_step = read_step

    def record_planned_consumption(
        self,
        node_id: str,
        *,
        step: int | None,
        multiplicity: int,
        active_drop_enabled: bool,
    ) -> None:
        if multiplicity <= 0:
            return
        stats = self.stats.get(node_id)
        if stats is None:
            return
        stats.ref_count_remaining = max(0, stats.ref_count_remaining - multiplicity)
        if (
            active_drop_enabled
            and stats.active_drop_eligible
            and stats.ref_count_remaining == 0
            and step is not None
            and stats.drop_expected_step is not None
            and step >= stats.drop_expected_step
            and stats.dropped_at_step is None
        ):
            self.entries.pop(node_id, None)
            stats.dropped_at_step = step
            stats.drop_delay_steps = max(0, step - stats.drop_expected_step)
            stats.drop_reason = "ref_count_zero"
            stats.retained_until_end = False

    def mark_drop_misses(self) -> None:
        for stats in self.stats.values():
            if stats.active_drop_eligible and stats.dropped_at_step is None:
                stats.drop_missed = True
                if stats.ref_count_remaining > 0:
                    stats.drop_miss_reason = "ref_count_remaining"
                elif stats.drop_expected_step is None:
                    stats.drop_miss_reason = "missing_drop_expected_step"
                else:
                    stats.drop_miss_reason = "drop_not_triggered"

    def record_hits(self, node_id: str, count: int) -> None:
        self.record_reads(node_id, read_count=count, consumer_count=0)

    def total_compute_calls(self) -> int:
        return sum(item.compute_count for item in self.stats.values())

    def total_store_hits(self) -> int:
        return self.total_node_store_reads()

    def total_node_store_reads(self) -> int:
        return sum(item.node_store_read_count for item in self.stats.values())

    def total_reuse_consumers(self) -> int:
        return sum(item.reuse_consumer_count for item in self.stats.values())

    def total_compute_time_ms(self) -> float:
        return sum(item.compute_time_ms for item in self.stats.values())

    def total_store_write_time_ms(self) -> float:
        return sum(item.store_write_time_ms for item in self.stats.values())

    def total_store_hit_time_ms(self) -> float:
        return sum(item.store_hit_time_ms for item in self.stats.values())

    def shared_hit_rate(self) -> float:
        hits = self.total_node_store_reads()
        computes = self.total_compute_calls()
        denominator = hits + computes
        return hits / denominator if denominator else 0.0

    def __len__(self) -> int:
        return len(self.entries)


@dataclass
class _MutableNode:
    node_id: str
    identity: tuple
    node_type: str
    label: str
    dependencies: tuple[str, ...]
    occurrence_count: int = 0
    consumers: set[str] | None = None
    output_names: list[str] | None = None
    canonical_repr: str = ""
    expr: Expr | None = None


class ExpressionDagBuilder:
    def __init__(self, *, time_col: str = "time", code_col: str = "code") -> None:
        self.time_col = time_col
        self.code_col = code_col
        self._nodes_by_identity: OrderedDict[tuple, _MutableNode] = OrderedDict()
        self._node_ids_by_identity: dict[tuple, str] = {}
        self._ast_node_count = 0
        self._planner_cse_mode = "baseline"
        self._fusion_mode = "off"
        self._expanded_cse_matches: dict[tuple, set[str]] = {}
        self._fusion_suppressed_identities: set[tuple] = set()
        self._fusion_chains: list[tuple[str, str]] = []

    def build(
        self,
        expressions: list[tuple[str, Expr]],
        *,
        materialization_threshold_mode: str = "reuse_ge_2",
        recomputation_guardrail_max_expansion: int = 0,
        planner_cse_mode: str = "baseline",
        fusion_mode: str = "off",
    ) -> ExpressionDag:
        self._planner_cse_mode = planner_cse_mode
        self._fusion_mode = fusion_mode
        output_node_ids: list[str] = []
        for output_name, expr in expressions:
            node_id = self._visit(expr)
            output_node_ids.append(node_id)
            node = self._nodes_by_identity[self._identity_by_node_id(node_id)]
            if node.output_names is None:
                node.output_names = []
            node.output_names.append(output_name)

        self._fusion_suppressed_identities = self._select_unary_chain_fusion_identities()
        nodes = [
            self._freeze_node(
                node,
                materialization_threshold_mode=materialization_threshold_mode,
                recomputation_guardrail_max_expansion=recomputation_guardrail_max_expansion,
            )
            for node in self._nodes_by_identity.values()
        ]
        lifecycle_plans = self._build_lifecycle_plans(
            nodes=nodes,
            output_node_ids=tuple(output_node_ids),
        )
        expanded_cse_audit = self._build_expanded_cse_audit(nodes)
        fusion_audit = self._build_fusion_audit(nodes)
        return ExpressionDag(
            nodes=tuple(nodes),
            output_node_ids=tuple(output_node_ids),
            ast_node_count=self._ast_node_count,
            dag_node_count=len(nodes),
            deduplicated_node_count=sum(1 for node in nodes if node.occurrence_count > 1),
            shared_node_count=sum(1 for node in nodes if node.is_shared),
            materialized_node_count=sum(1 for node in nodes if node.materialize),
            expensive_node_count=sum(1 for node in nodes if node.is_expensive),
            lifecycle_plans=lifecycle_plans,
            expanded_cse_audit=expanded_cse_audit,
            fusion_audit=fusion_audit,
        )

    def _visit(self, expr: Expr) -> str:
        self._ast_node_count += 1
        dependencies: tuple[str, ...]
        if isinstance(expr, NumberNode):
            identity = ("number", self._canonical_number(expr.value))
            node_type = "number"
            label = repr(self._canonical_number(expr.value))
            dependencies = ()
        elif isinstance(expr, BooleanNode):
            identity = ("boolean", expr.value)
            node_type = "boolean"
            label = str(expr.value).lower()
            dependencies = ()
        elif isinstance(expr, ListNode):
            dependency_ids = tuple(self._visit(item) for item in expr.items)
            child_identities = tuple(self._nodes_by_identity[self._identity_by_node_id(dep)].identity for dep in dependency_ids)
            identity = ("list", child_identities)
            node_type = "list"
            label = "list"
            dependencies = dependency_ids
        elif isinstance(expr, VariableNode):
            identity = ("var", expr.name)
            node_type = "variable"
            label = expr.name
            dependencies = ()
        elif isinstance(expr, UnaryOpNode):
            dependency_ids = (self._visit(expr.operand),)
            child_identity = self._nodes_by_identity[self._identity_by_node_id(dependency_ids[0])].identity
            identity = ("unary", expr.operator, child_identity)
            node_type = "unary"
            label = expr.operator
            dependencies = dependency_ids
        elif isinstance(expr, BinaryOpNode):
            left_id = self._visit(expr.left)
            right_id = self._visit(expr.right)
            left_identity = self._nodes_by_identity[self._identity_by_node_id(left_id)].identity
            right_identity = self._nodes_by_identity[self._identity_by_node_id(right_id)].identity
            identity = ("binary", expr.operator, left_identity, right_identity)
            node_type = "binary"
            label = expr.operator
            dependencies = (left_id, right_id)
        elif isinstance(expr, CallNode):
            dependency_ids = tuple(self._visit(arg) for arg in expr.args)
            kw_dependency_ids = tuple(
                (key, self._visit(value))
                for key, value in sorted(expr.kwargs.items())
            )
            child_identities = tuple(
                self._nodes_by_identity[self._identity_by_node_id(dep)].identity
                for dep in dependency_ids
            )
            kw_identities = tuple(
                (key, self._nodes_by_identity[self._identity_by_node_id(dep)].identity)
                for key, dep in kw_dependency_ids
            )
            normalized_kwargs = self._normalized_kwargs(expr, kw_identities)
            spec = get_function_spec(expr.name)
            route_sensitive = (
                "function_context",
                spec.execution_kind if spec is not None else "unknown",
                spec.window_kind if spec is not None else "unknown",
                bool(spec.requires_time_col) if spec is not None else False,
                self.time_col if spec is not None and spec.requires_time_col else None,
                bool(spec.requires_code_col) if spec is not None else False,
                self.code_col if spec is not None and spec.requires_code_col else None,
            )
            identity = (
                "call",
                expr.name,
                route_sensitive,
                child_identities,
                normalized_kwargs,
            )
            expanded_identity = self._expanded_repeated_family_identity(
                expr=expr,
                baseline_identity=identity,
                route_sensitive=route_sensitive,
                child_identities=child_identities,
                normalized_kwargs=normalized_kwargs,
            )
            if expanded_identity != identity:
                self._expanded_cse_matches.setdefault(expanded_identity, set()).add(
                    repr(identity)
                )
                identity = expanded_identity
            node_type = "call"
            label = expr.name
            dependencies = (*dependency_ids, *(dep for _key, dep in kw_dependency_ids))
        else:
            raise TypeError(f"Unsupported AST node for DAG building: {type(expr).__name__}")

        existing_id = self._node_ids_by_identity.get(identity)
        if existing_id is not None:
            self._nodes_by_identity[identity].occurrence_count += 1
            for dep_id in dependencies:
                self._add_consumer(dep_id, existing_id)
            return existing_id

        node_id = f"n{len(self._nodes_by_identity) + 1}"
        node = _MutableNode(
            node_id=node_id,
            identity=identity,
            node_type=node_type,
            label=label,
            dependencies=dependencies,
            occurrence_count=1,
            consumers=set(),
            output_names=[],
            canonical_repr=repr(identity),
            expr=expr,
        )
        self._nodes_by_identity[identity] = node
        self._node_ids_by_identity[identity] = node_id
        for dep_id in dependencies:
            self._add_consumer(dep_id, node_id)
        return node_id

    @staticmethod
    def _canonical_number(value: float) -> int | float:
        return int(value) if int(value) == value else float(value)

    @staticmethod
    def _normalized_kwargs(
        expr: CallNode,
        kw_identities: tuple[tuple[str, tuple], ...],
    ) -> tuple[tuple[str, tuple], ...]:
        kwargs = dict(kw_identities)
        if expr.name in {"rank", "group_rank", "ts_rank"}:
            kwargs.setdefault("ascending", ("boolean", False))
            kwargs.setdefault("pct", ("boolean", False))
        return tuple(sorted(kwargs.items()))

    def _expanded_repeated_family_identity(
        self,
        *,
        expr: CallNode,
        baseline_identity: tuple,
        route_sensitive: tuple,
        child_identities: tuple[tuple, ...],
        normalized_kwargs: tuple[tuple[str, tuple], ...],
    ) -> tuple:
        if self._planner_cse_mode != "expanded_repeated_family":
            return baseline_identity
        if expr.name not in {"ts_rank", "ts_mean"}:
            return baseline_identity
        if len(child_identities) < 2:
            return baseline_identity
        if len(route_sensitive) < 3 or route_sensitive[2] != "rolling":
            return baseline_identity
        normalized_first = self._neutral_add_variable_identity(child_identities[0])
        if normalized_first is None:
            return baseline_identity
        return (
            "call",
            expr.name,
            route_sensitive,
            (normalized_first, *child_identities[1:]),
            normalized_kwargs,
        )

    @staticmethod
    def _neutral_add_variable_identity(identity: tuple) -> tuple | None:
        if len(identity) != 4 or identity[0] != "binary" or identity[1] != "+":
            return None
        left = identity[2]
        right = identity[3]
        if (
            isinstance(left, tuple)
            and isinstance(right, tuple)
            and left[0] == "var"
            and right == ("number", 0)
        ):
            return left
        if (
            isinstance(left, tuple)
            and isinstance(right, tuple)
            and right[0] == "var"
            and left == ("number", 0)
        ):
            return right
        return None

    def _select_unary_chain_fusion_identities(self) -> set[tuple]:
        if self._fusion_mode != "unary_chain_fusion":
            self._fusion_chains = []
            return set()

        nodes_by_id = {
            node.node_id: node
            for node in self._nodes_by_identity.values()
        }
        suppressed: set[tuple] = set()
        chains: list[tuple[str, str]] = []
        for outer in self._nodes_by_identity.values():
            if not self._is_fusion_outer_node(outer):
                continue
            if len(outer.dependencies) < 2:
                continue
            inner = nodes_by_id.get(outer.dependencies[0])
            if inner is None or not self._is_fusion_inner_node(inner):
                continue
            if inner.output_names:
                continue
            if (inner.consumers or set()) != {outer.node_id}:
                continue
            if inner.occurrence_count < 2 or outer.occurrence_count < 2:
                continue
            if not inner.dependencies:
                continue
            source = nodes_by_id.get(inner.dependencies[0])
            if source is None or source.node_type != "variable":
                continue
            suppressed.add(inner.identity)
            chains.append((inner.node_id, outer.node_id))

        self._fusion_chains = chains
        return suppressed

    @staticmethod
    def _is_fusion_inner_node(node: _MutableNode) -> bool:
        return node.node_type == "call" and node.label == "ts_mean"

    @staticmethod
    def _is_fusion_outer_node(node: _MutableNode) -> bool:
        return node.node_type == "call" and node.label == "ts_rank"

    def _identity_by_node_id(self, node_id: str) -> tuple:
        for identity, current_id in self._node_ids_by_identity.items():
            if current_id == node_id:
                return identity
        raise KeyError(node_id)

    def _add_consumer(self, node_id: str, consumer_node_id: str) -> None:
        node = self._nodes_by_identity[self._identity_by_node_id(node_id)]
        if node.consumers is None:
            node.consumers = set()
        node.consumers.add(consumer_node_id)

    def _freeze_node(
        self,
        node: _MutableNode,
        *,
        materialization_threshold_mode: str,
        recomputation_guardrail_max_expansion: int,
    ) -> DagNode:
        output_names = tuple(node.output_names or ())
        consumer_count = max(node.occurrence_count, len(node.consumers or set()) + len(output_names))
        cost_class = self._cost_class(node)
        is_expensive = cost_class == "expensive"
        is_shared = node.occurrence_count > 1 and consumer_count > 1
        default_materialize = is_shared and is_expensive
        if node.identity in self._fusion_suppressed_identities:
            default_materialize = False
        recomputation_expansion_if_inline = (
            max(0, node.occurrence_count - 1) if default_materialize else 0
        )
        recomputation_guardrail_pass = (
            recomputation_expansion_if_inline <= recomputation_guardrail_max_expansion
        )
        if materialization_threshold_mode == "reuse_ge_3_guarded":
            materialize = (
                default_materialize
                and (
                    node.occurrence_count >= 3
                    or not recomputation_guardrail_pass
                )
            )
        else:
            materialize = default_materialize
        materialization_reason = self._materialization_reason(
            is_shared=is_shared,
            is_expensive=is_expensive,
            materialize=materialize,
        )
        materialization_eligibility = self._materialization_eligibility(
            materialization_reason=materialization_reason,
            materialize=materialize,
        )
        materialization_kind: MaterializationKind
        if output_names:
            materialization_kind = "final"
        elif materialize:
            materialization_kind = "shared_intermediate"
        else:
            materialization_kind = "ephemeral"
        if node.identity in self._fusion_suppressed_identities:
            share_decision = "inline"
            share_reason = "fused_into_parent_unary_chain"
        else:
            share_decision, share_reason = self._share_decision(
                node,
                cost_class=cost_class,
                is_shared=is_shared,
                materialize=materialize,
            )
        if node.expr is None:
            raise TypeError("Internal error: DAG node is missing its source expression")
        return DagNode(
            node_id=node.node_id,
            identity=node.identity,
            node_type=node.node_type,
            label=node.label,
            dependencies=node.dependencies,
            consumers=tuple(sorted(node.consumers or set())),
            output_names=output_names,
            occurrence_count=node.occurrence_count,
            cost_class=cost_class,
            is_expensive=is_expensive,
            is_shared=is_shared,
            materialization_kind=materialization_kind,
            materialization_reason=materialization_reason,
            materialization_eligibility=materialization_eligibility,
            materialize=materialize,
            default_materialize=default_materialize,
            recomputation_expansion_if_inline=recomputation_expansion_if_inline,
            recomputation_guardrail_pass=recomputation_guardrail_pass,
            share_decision=share_decision,
            share_reason=share_reason,
            canonical_repr=node.canonical_repr,
            expr=node.expr,
        )

    def _cost_class(self, node: _MutableNode) -> NodeCostClass:
        if node.node_type != "call":
            return "cheap"
        if len(node.identity) < 3:
            return "cheap"
        route_sensitive = node.identity[2]
        if not isinstance(route_sensitive, tuple) or len(route_sensitive) < 4:
            return "cheap"
        execution_kind = route_sensitive[1]
        window_kind = route_sensitive[2]
        if window_kind in {"rolling", "positional", "segmented"} or execution_kind == "time_series":
            return "expensive"
        if execution_kind == "cross_sectional":
            return "medium"
        return "cheap"

    def _build_lifecycle_plans(
        self,
        *,
        nodes: list[DagNode],
        output_node_ids: tuple[str, ...],
    ) -> tuple[NodeLifecyclePlan, ...]:
        nodes_by_id = {node.node_id: node for node in nodes}
        node_steps = {node.node_id: index for index, node in enumerate(nodes, start=1)}
        output_steps = {
            output_node_id: len(nodes) + index
            for index, output_node_id in enumerate(output_node_ids, start=1)
        }
        last_consumer_step = max(output_steps.values(), default=len(nodes))
        restore_assemble_step = last_consumer_step + 1
        append_step = restore_assemble_step + 1
        finalize_step = append_step + 1
        batch_end_step = finalize_step + 1
        node_depth_by_id = {
            node.node_id: self._node_depth(node.node_id, nodes_by_id=nodes_by_id)
            for node in nodes
        }
        materialized_parent_by_node_id: dict[str, str] = {}
        for node in nodes:
            if not node.materialize:
                continue
            for dependency_id in node.dependencies:
                for child_id in self._reachable_until_materialized(
                    dependency_id,
                    nodes_by_id=nodes_by_id,
                ):
                    materialized_parent_by_node_id.setdefault(child_id, node.node_id)

        plans: list[NodeLifecyclePlan] = []
        for node in nodes:
            if not node.materialize:
                plans.append(
                    NodeLifecyclePlan(
                        node_id=node.node_id,
                        materialization_reason=node.materialization_reason,
                        producer_step=None,
                        consumer_steps=(),
                        last_use_step=None,
                        ref_count_initial=0,
                        drop_candidate=False,
                        drop_blocker_reason="not_materialized",
                        restore_assemble_step=restore_assemble_step,
                        append_step=append_step,
                        finalize_step=finalize_step,
                        batch_end_step=batch_end_step,
                        node_depth=node_depth_by_id[node.node_id],
                        parent_node_id=materialized_parent_by_node_id.get(node.node_id),
                        dependency_chain=self._dependency_chain(
                            node.node_id,
                            nodes_by_id=nodes_by_id,
                        ),
                    )
                )
                continue

            materialized_parent_steps = [
                node_steps[parent.node_id]
                for parent in nodes
                if parent.materialize and parent.node_id != node.node_id
                for _ in range(
                    self._materialized_parent_dependency_occurrence_count(
                        target_node_id=node.node_id,
                        parent_node_id=parent.node_id,
                        nodes_by_id=nodes_by_id,
                    )
                )
            ]
            output_consumer_steps = [
                output_steps[output_node_id]
                for output_node_id in output_node_ids
                for _ in range(
                    self._bounded_dependency_occurrence_count(
                        target_node_id=node.node_id,
                        root_node_id=output_node_id,
                        nodes_by_id=nodes_by_id,
                    )
                )
            ]
            consumer_steps = tuple(sorted([*materialized_parent_steps, *output_consumer_steps]))
            ref_count_initial = len(consumer_steps)
            last_use_step = max(consumer_steps) if consumer_steps else None
            final_output_retained = bool(node.output_names)
            drop_candidate = (
                ref_count_initial > 0
                and last_use_step is not None
                and not final_output_retained
            )
            if final_output_retained:
                drop_blocker_reason = "final_output_retention"
            elif drop_candidate:
                drop_blocker_reason = ""
            elif ref_count_initial == 0:
                drop_blocker_reason = "no_planned_consumers"
            else:
                drop_blocker_reason = "no_last_use_step"
            structural_release_lag_steps = (
                max(0, batch_end_step - last_use_step)
                if last_use_step is not None
                else None
            )
            finalize_retention_lag_steps = (
                max(0, finalize_step - last_use_step)
                if last_use_step is not None
                else None
            )
            plans.append(
                NodeLifecyclePlan(
                    node_id=node.node_id,
                    materialization_reason=node.materialization_reason,
                    producer_step=node_steps[node.node_id],
                    consumer_steps=consumer_steps,
                    last_use_step=last_use_step,
                    ref_count_initial=ref_count_initial,
                    drop_candidate=drop_candidate,
                    drop_blocker_reason=drop_blocker_reason,
                    restore_assemble_step=restore_assemble_step,
                    append_step=append_step,
                    finalize_step=finalize_step,
                    batch_end_step=batch_end_step,
                    structural_release_lag_steps=structural_release_lag_steps,
                    retained_past_last_read=(
                        last_use_step is not None and batch_end_step > last_use_step
                    ),
                    finalize_retention_lag_steps=finalize_retention_lag_steps,
                    node_depth=node_depth_by_id[node.node_id],
                    parent_node_id=materialized_parent_by_node_id.get(node.node_id),
                    dependency_chain=self._dependency_chain(
                        node.node_id,
                        nodes_by_id=nodes_by_id,
                    ),
                )
            )

        return tuple(plans)

    def _build_expanded_cse_audit(self, nodes: list[DagNode]) -> ExpandedCseAudit:
        if self._planner_cse_mode != "expanded_repeated_family":
            return ExpandedCseAudit()
        matched_nodes = [
            node
            for node in nodes
            if node.identity in self._expanded_cse_matches
        ]
        reused_nodes = [
            node
            for node in matched_nodes
            if node.is_shared and node.materialize
        ]
        return ExpandedCseAudit(
            selected_family="rolling_neutral_add_input",
            baseline_identity_rule=(
                "baseline keeps the full first-argument subtree in rolling call identity"
            ),
            expanded_identity_rule=(
                "for ts_rank/ts_mean only, first argument var+0 or 0+var canonicalizes to var"
            ),
            matched_groups=len(matched_nodes),
            reused_groups=len(reused_nodes),
            merged_nodes=tuple(node.node_id for node in reused_nodes),
            affected_subgraph_signatures=tuple(
                repr(node.identity) for node in matched_nodes
            ),
            baseline_miss_reason=(
                "neutral pointwise add creates a distinct child identity despite identical numeric value"
            ),
            safe_merge_rationale=(
                "x + 0 and 0 + x are value-preserving for the numeric rolling inputs in this selected family"
            ),
        )

    def _build_fusion_audit(self, nodes: list[DagNode]) -> FusionAudit:
        if self._fusion_mode != "unary_chain_fusion":
            return FusionAudit()
        nodes_by_id = {node.node_id: node for node in nodes}
        fused_chains = tuple(
            tuple(node_id for node_id in (inner_id, outer_id) if node_id in nodes_by_id)
            for inner_id, outer_id in self._fusion_chains
        )
        affected_signatures = tuple(
            repr(nodes_by_id[inner_id].identity)
            for inner_id, _outer_id in self._fusion_chains
            if inner_id in nodes_by_id
        )
        return FusionAudit(
            selected_family="rolling_unary_chain_ts_mean_into_ts_rank",
            baseline_rule=(
                "baseline materializes repeated expensive ts_mean and repeated "
                "expensive ts_rank nodes independently"
            ),
            fused_rule=(
                "for pure ts_rank(ts_mean(variable, w1), w2) repeated chains, "
                "the shared inner ts_mean stays transient while the outer "
                "ts_rank remains the materialized helper"
            ),
            matched_chains=len(fused_chains),
            fused_chains=fused_chains,
            nodes_reduced=len(self._fusion_suppressed_identities),
            affected_subgraph_signatures=affected_signatures,
            safe_fusion_rationale=(
                "the selected family is a single-parent unary rolling chain with "
                "no branching, no inner output retention, and no route or DSL "
                "semantic change"
            ),
        )

    def _bounded_dependency_occurrence_count(
        self,
        *,
        target_node_id: str,
        root_node_id: str,
        nodes_by_id: dict[str, DagNode],
    ) -> int:
        if root_node_id == target_node_id:
            return 1
        root = nodes_by_id[root_node_id]
        if root.materialize:
            return 0
        direct_count = sum(
            1 for dependency_id in root.dependencies if dependency_id == target_node_id
        )
        nested_count = sum(
            self._bounded_dependency_occurrence_count(
                target_node_id=target_node_id,
                root_node_id=dependency_id,
                nodes_by_id=nodes_by_id,
            )
            for dependency_id in root.dependencies
            if dependency_id != target_node_id and not nodes_by_id[dependency_id].materialize
        )
        return direct_count + nested_count

    def _materialized_parent_dependency_occurrence_count(
        self,
        *,
        target_node_id: str,
        parent_node_id: str,
        nodes_by_id: dict[str, DagNode],
    ) -> int:
        parent = nodes_by_id[parent_node_id]
        return sum(
            1
            if dependency_id == target_node_id
            else self._bounded_dependency_occurrence_count(
                target_node_id=target_node_id,
                root_node_id=dependency_id,
                nodes_by_id=nodes_by_id,
            )
            for dependency_id in parent.dependencies
            if dependency_id == target_node_id or not nodes_by_id[dependency_id].materialize
        )

    def _reachable_until_materialized(
        self,
        node_id: str,
        *,
        nodes_by_id: dict[str, DagNode],
    ) -> set[str]:
        node = nodes_by_id[node_id]
        if node.materialize:
            return {node_id}
        reachable = {node_id}
        for dependency_id in node.dependencies:
            reachable.update(
                self._reachable_until_materialized(
                    dependency_id,
                    nodes_by_id=nodes_by_id,
                )
            )
        return reachable

    def _node_depth(
        self,
        node_id: str,
        *,
        nodes_by_id: dict[str, DagNode],
    ) -> int:
        node = nodes_by_id[node_id]
        if not node.dependencies:
            return 0
        return 1 + max(
            self._node_depth(dependency_id, nodes_by_id=nodes_by_id)
            for dependency_id in node.dependencies
        )

    def _dependency_chain(
        self,
        node_id: str,
        *,
        nodes_by_id: dict[str, DagNode],
    ) -> tuple[str, ...]:
        node = nodes_by_id[node_id]
        if not node.dependencies:
            return (node_id,)
        deepest_dependency = max(
            node.dependencies,
            key=lambda dependency_id: self._node_depth(
                dependency_id,
                nodes_by_id=nodes_by_id,
            ),
        )
        return (
            *self._dependency_chain(deepest_dependency, nodes_by_id=nodes_by_id),
            node_id,
        )

    def _reachable_node_ids(
        self,
        node_id: str,
        *,
        nodes_by_id: dict[str, DagNode],
    ) -> set[str]:
        reachable = {node_id}
        node = nodes_by_id[node_id]
        for dependency_id in node.dependencies:
            reachable.update(
                self._reachable_node_ids(
                    dependency_id,
                    nodes_by_id=nodes_by_id,
                )
            )
        return reachable

    @staticmethod
    def _materialization_reason(
        *,
        is_shared: bool,
        is_expensive: bool,
        materialize: bool,
    ) -> MaterializationReason:
        if not materialize:
            return "none"
        if is_shared and is_expensive:
            # R4/P4 currently lifts repeated expensive ordered/window nodes both
            # for reuse and to keep heavy compiled work out of final assemble.
            return "shared_reuse_and_path_normalization"
        return "none"

    @staticmethod
    def _materialization_eligibility(
        *,
        materialization_reason: MaterializationReason,
        materialize: bool,
    ) -> MaterializationEligibility:
        if not materialize:
            return "inline_required"
        if materialization_reason == "shared_reuse":
            return "materialize_for_reuse"
        if materialization_reason == "path_normalization":
            return "materialize_for_path_normalization"
        if materialization_reason == "shared_reuse_and_path_normalization":
            return "materialize_for_both"
        return "inline_required"

    @staticmethod
    def _share_decision(
        node: _MutableNode,
        *,
        cost_class: NodeCostClass,
        is_shared: bool,
        materialize: bool,
    ) -> tuple[str, str]:
        if not is_shared:
            return "not_shared", "single_consumer_or_single_occurrence"
        if materialize:
            return "materialize", "repeated_expensive_node"
        return "inline", f"repeated_{cost_class}_node"
