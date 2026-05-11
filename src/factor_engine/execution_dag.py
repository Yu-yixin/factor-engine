from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

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
from factor_engine.dag import DagNode, ExpressionDagBuilder, NodeResultStore
from factor_engine.errors import ExecutionError
from factor_engine.execution_materialization import materialized_consumer_count


@dataclass
class DagExecutionContext:
    result_store: NodeResultStore
    dag_nodes_by_output: dict[str, str]
    dag_identity_by_node_id: dict[str, tuple]
    dag_nodes_by_identity: dict[tuple, DagNode]
    lifecycle_plans_by_node_id: dict[str, object]
    lifecycle_read_cursor_by_node_id: dict[str, int]
    materialized_column_by_identity: dict[tuple, str]


def increment_planned_consumer(planned: dict[tuple, int], cache_key: tuple | None) -> None:
    if cache_key is not None:
        planned[cache_key] = planned.get(cache_key, 0) + 1


def dag_identity_for_expr(
    expr: Expr,
    *,
    time_col: str,
    code_col: str,
    materialization_threshold_mode: str,
    recomputation_guardrail_max_expansion: int,
    planner_cse_mode: str,
    fusion_mode: str,
) -> tuple:
    dag = ExpressionDagBuilder(time_col=time_col, code_col=code_col).build(
        [("__value__", expr)],
        materialization_threshold_mode=materialization_threshold_mode,
        recomputation_guardrail_max_expansion=recomputation_guardrail_max_expansion,
        planner_cse_mode=planner_cse_mode,
        fusion_mode=fusion_mode,
    )
    nodes_by_id = dag.node_by_id()
    return nodes_by_id[dag.output_node_ids[0]].identity


def merge_node_hit_counts(target: dict[str, int], source: dict[str, int]) -> None:
    for node_id, count in source.items():
        target[node_id] = target.get(node_id, 0) + count


def rewrite_expr_with_materialized_nodes(
    expr: Expr,
    *,
    materialized_column_by_identity: dict[tuple, str],
    dag_nodes_by_identity: dict[tuple, DagNode],
    identity_for_expr: Callable[[Expr], tuple],
    skip_identity: tuple | None = None,
) -> tuple[Expr, dict[str, int]]:
    identity = identity_for_expr(expr)
    if identity != skip_identity and identity in materialized_column_by_identity:
        node = dag_nodes_by_identity[identity]
        return VariableNode(materialized_column_by_identity[identity]), {node.node_id: 1}

    if isinstance(expr, (NumberNode, BooleanNode, VariableNode)):
        return expr, {}

    if isinstance(expr, ListNode):
        items: list[Expr] = []
        hits: dict[str, int] = {}
        for item in expr.items:
            rewritten, child_hits = rewrite_expr_with_materialized_nodes(
                item,
                materialized_column_by_identity=materialized_column_by_identity,
                dag_nodes_by_identity=dag_nodes_by_identity,
                identity_for_expr=identity_for_expr,
                skip_identity=skip_identity,
            )
            items.append(rewritten)
            merge_node_hit_counts(hits, child_hits)
        return ListNode(items), hits

    if isinstance(expr, UnaryOpNode):
        operand, hits = rewrite_expr_with_materialized_nodes(
            expr.operand,
            materialized_column_by_identity=materialized_column_by_identity,
            dag_nodes_by_identity=dag_nodes_by_identity,
            identity_for_expr=identity_for_expr,
            skip_identity=skip_identity,
        )
        return UnaryOpNode(expr.operator, operand), hits

    if isinstance(expr, BinaryOpNode):
        left, hits = rewrite_expr_with_materialized_nodes(
            expr.left,
            materialized_column_by_identity=materialized_column_by_identity,
            dag_nodes_by_identity=dag_nodes_by_identity,
            identity_for_expr=identity_for_expr,
            skip_identity=skip_identity,
        )
        right, right_hits = rewrite_expr_with_materialized_nodes(
            expr.right,
            materialized_column_by_identity=materialized_column_by_identity,
            dag_nodes_by_identity=dag_nodes_by_identity,
            identity_for_expr=identity_for_expr,
            skip_identity=skip_identity,
        )
        merge_node_hit_counts(hits, right_hits)
        return BinaryOpNode(left, expr.operator, right), hits

    if isinstance(expr, CallNode):
        args: list[Expr] = []
        hits: dict[str, int] = {}
        for arg in expr.args:
            rewritten, child_hits = rewrite_expr_with_materialized_nodes(
                arg,
                materialized_column_by_identity=materialized_column_by_identity,
                dag_nodes_by_identity=dag_nodes_by_identity,
                identity_for_expr=identity_for_expr,
                skip_identity=skip_identity,
            )
            args.append(rewritten)
            merge_node_hit_counts(hits, child_hits)
        kwargs: dict[str, Expr] = {}
        for key, value in expr.kwargs.items():
            rewritten, child_hits = rewrite_expr_with_materialized_nodes(
                value,
                materialized_column_by_identity=materialized_column_by_identity,
                dag_nodes_by_identity=dag_nodes_by_identity,
                identity_for_expr=identity_for_expr,
                skip_identity=skip_identity,
            )
            kwargs[key] = rewritten
            merge_node_hit_counts(hits, child_hits)
        return CallNode(expr.name, args, kwargs), hits

    raise ExecutionError(f"Unsupported AST node for DAG rewrite: {type(expr).__name__}")


def count_materializable_node_occurrences(
    expr: Expr,
    *,
    dag_nodes_by_identity: dict[tuple, DagNode],
    identity_for_expr: Callable[[Expr], tuple],
    node_lifecycle_class_for_identity: Callable[[tuple], str],
    node_lifecycle_class: str | None = None,
) -> int:
    identity = identity_for_expr(expr)
    node = dag_nodes_by_identity.get(identity)
    if node is not None and node.materialize:
        if node_lifecycle_class is None:
            return 1
        return 1 if node_lifecycle_class_for_identity(node.identity) == node_lifecycle_class else 0

    if isinstance(expr, (NumberNode, BooleanNode, VariableNode)):
        return 0

    if isinstance(expr, ListNode):
        return sum(
            count_materializable_node_occurrences(
                item,
                dag_nodes_by_identity=dag_nodes_by_identity,
                identity_for_expr=identity_for_expr,
                node_lifecycle_class_for_identity=node_lifecycle_class_for_identity,
                node_lifecycle_class=node_lifecycle_class,
            )
            for item in expr.items
        )

    if isinstance(expr, UnaryOpNode):
        return count_materializable_node_occurrences(
            expr.operand,
            dag_nodes_by_identity=dag_nodes_by_identity,
            identity_for_expr=identity_for_expr,
            node_lifecycle_class_for_identity=node_lifecycle_class_for_identity,
            node_lifecycle_class=node_lifecycle_class,
        )

    if isinstance(expr, BinaryOpNode):
        return (
            count_materializable_node_occurrences(
                expr.left,
                dag_nodes_by_identity=dag_nodes_by_identity,
                identity_for_expr=identity_for_expr,
                node_lifecycle_class_for_identity=node_lifecycle_class_for_identity,
                node_lifecycle_class=node_lifecycle_class,
            )
            + count_materializable_node_occurrences(
                expr.right,
                dag_nodes_by_identity=dag_nodes_by_identity,
                identity_for_expr=identity_for_expr,
                node_lifecycle_class_for_identity=node_lifecycle_class_for_identity,
                node_lifecycle_class=node_lifecycle_class,
            )
        )

    if isinstance(expr, CallNode):
        return sum(
            count_materializable_node_occurrences(
                arg,
                dag_nodes_by_identity=dag_nodes_by_identity,
                identity_for_expr=identity_for_expr,
                node_lifecycle_class_for_identity=node_lifecycle_class_for_identity,
                node_lifecycle_class=node_lifecycle_class,
            )
            for arg in expr.args
        ) + sum(
            count_materializable_node_occurrences(
                value,
                dag_nodes_by_identity=dag_nodes_by_identity,
                identity_for_expr=identity_for_expr,
                node_lifecycle_class_for_identity=node_lifecycle_class_for_identity,
                node_lifecycle_class=node_lifecycle_class,
            )
            for value in expr.kwargs.values()
        )

    raise ExecutionError(f"Unsupported AST node for DAG occurrence count: {type(expr).__name__}")


def initialize_dag_execution_context(batch_dag) -> DagExecutionContext:
    result_store = NodeResultStore()
    dag_nodes_by_output: dict[str, str] = {}
    dag_identity_by_node_id: dict[str, tuple] = {}
    dag_nodes_by_identity: dict[tuple, DagNode] = {}
    lifecycle_plans_by_node_id: dict[str, object] = {}
    lifecycle_read_cursor_by_node_id: dict[str, int] = {}
    materialized_column_by_identity: dict[tuple, str] = {}
    if batch_dag is not None:
        lifecycle_plans_by_node_id = batch_dag.lifecycle_plan_by_node_id()
        for node in batch_dag.nodes:
            dag_nodes_by_identity[node.identity] = node
            dag_identity_by_node_id[node.node_id] = node.identity
            for output_name in node.output_names:
                dag_nodes_by_output[output_name] = node.node_id
            if node.materialize:
                result_store.register_policy(
                    node_id=node.node_id,
                    identity=node.identity,
                    materialization_kind=node.materialization_kind,
                    consumer_count=materialized_consumer_count(node),
                    materialization_reason=node.materialization_reason,
                    materialization_eligibility=node.materialization_eligibility,
                    recomputation_expansion_if_inline=node.recomputation_expansion_if_inline,
                    recomputation_guardrail_pass=node.recomputation_guardrail_pass,
                )
    return DagExecutionContext(
        result_store=result_store,
        dag_nodes_by_output=dag_nodes_by_output,
        dag_identity_by_node_id=dag_identity_by_node_id,
        dag_nodes_by_identity=dag_nodes_by_identity,
        lifecycle_plans_by_node_id=lifecycle_plans_by_node_id,
        lifecycle_read_cursor_by_node_id=lifecycle_read_cursor_by_node_id,
        materialized_column_by_identity=materialized_column_by_identity,
    )
