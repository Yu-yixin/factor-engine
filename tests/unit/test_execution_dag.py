from __future__ import annotations

from types import SimpleNamespace

from factor_engine.ast_nodes import BinaryOpNode, CallNode, NumberNode, VariableNode
from factor_engine.execution_dag import (
    count_materializable_node_occurrences,
    increment_planned_consumer,
    initialize_dag_execution_context,
    merge_node_hit_counts,
    rewrite_expr_with_materialized_nodes,
)


def test_increment_and_merge_node_counts_are_stable():
    planned: dict[tuple, int] = {}
    increment_planned_consumer(planned, ("expr", "a"))
    increment_planned_consumer(planned, ("expr", "a"))
    increment_planned_consumer(planned, None)

    hits = {"node-a": 1}
    merge_node_hit_counts(hits, {"node-a": 2, "node-b": 1})

    assert planned == {("expr", "a"): 2}
    assert hits == {"node-a": 3, "node-b": 1}


def test_rewrite_expr_with_materialized_nodes_replaces_reusable_child():
    expr = BinaryOpNode(VariableNode("close"), "+", NumberNode(1.0))
    node = SimpleNamespace(node_id="node-close", identity=("var", "close"), materialize=True)

    rewritten, hits = rewrite_expr_with_materialized_nodes(
        expr,
        materialized_column_by_identity={("var", "close"): "__dag_node_1"},
        dag_nodes_by_identity={("var", "close"): node},
        identity_for_expr=lambda item: ("var", item.name) if isinstance(item, VariableNode) else ("expr", repr(item)),
    )

    assert rewritten == BinaryOpNode(VariableNode("__dag_node_1"), "+", NumberNode(1.0))
    assert hits == {"node-close": 1}


def test_count_materializable_node_occurrences_honors_lifecycle_class():
    expr = CallNode("argmax", [VariableNode("close"), NumberNode(2.0)])
    node = SimpleNamespace(
        node_id="node-argmax",
        identity=("call", "argmax"),
        materialize=True,
    )

    count = count_materializable_node_occurrences(
        expr,
        dag_nodes_by_identity={("call", "argmax"): node},
        identity_for_expr=lambda item: ("call", "argmax") if isinstance(item, CallNode) else ("other", repr(item)),
        node_lifecycle_class_for_identity=lambda _identity: "native_heavy",
        node_lifecycle_class="native_heavy",
    )

    assert count == 1


def test_initialize_dag_execution_context_registers_materialized_policy():
    node = SimpleNamespace(
        node_id="node-a",
        identity=("call", "ts_mean"),
        output_names=("alpha",),
        materialize=True,
        occurrence_count=3,
        consumers=("node-b",),
        materialization_kind="shared_intermediate",
        materialization_reason="shared_reuse",
        materialization_eligibility="materialize_for_reuse",
        recomputation_expansion_if_inline=2,
        recomputation_guardrail_pass=True,
    )
    dag = SimpleNamespace(
        nodes=(node,),
        lifecycle_plan_by_node_id=lambda: {"node-a": object()},
    )

    context = initialize_dag_execution_context(dag)

    assert context.dag_nodes_by_output == {"alpha": "node-a"}
    assert context.dag_identity_by_node_id == {"node-a": ("call", "ts_mean")}
    assert context.lifecycle_plans_by_node_id.keys() == {"node-a"}
    assert "node-a" in context.result_store.stats
