from __future__ import annotations

from collections.abc import Callable, Sequence
import time
from typing import Any

import polars as pl

from factor_engine.ast_nodes import Expr
from factor_engine.dag import DagNode, NodeResultStore, NodeResultStoreEntry
from factor_engine.lifecycle import FirstWaveCandidateInput, is_first_wave_candidate


def materialize_shared_dag_nodes_on_sorted_df(
    sorted_df: pl.DataFrame,
    *,
    dag_nodes: Sequence[DagNode],
    reserved_names: set[str],
    stage_cache: dict[tuple, str],
    result_store: NodeResultStore,
    materialized_column_by_identity: dict[tuple, str],
    dag_nodes_by_identity: dict[tuple, DagNode],
    lifecycle_plans_by_node_id: dict[str, object],
    runtime: Any,
    lifecycle_active: bool,
    dag_cse_enabled: bool,
    rewrite_expr_with_materialized_nodes: Callable[..., tuple[Expr, dict[str, int]]],
    compile_expr: Callable[[Expr], pl.Expr],
    temporary_helper_name: Callable[..., str],
    node_lifecycle_class: Callable[[tuple], str],
) -> tuple[pl.DataFrame, dict[tuple, str]]:
    for node in dag_nodes:
        if not node.materialize or node.identity in materialized_column_by_identity:
            continue
        lifecycle_plan = lifecycle_plans_by_node_id.get(node.node_id)
        producer_step = (
            getattr(lifecycle_plan, "producer_step", None)
            if lifecycle_plan is not None
            else None
        )

        rewritten_expr, child_hits = rewrite_expr_with_materialized_nodes(
            node.expr,
            materialized_column_by_identity=materialized_column_by_identity,
            dag_nodes_by_identity=dag_nodes_by_identity,
            skip_identity=node.identity,
        )
        for node_id, count in child_hits.items():
            record_cse_child_read(
                result_store,
                node_id=node_id,
                count=count,
                producer_step=producer_step,
                lifecycle_active=lifecycle_active,
            )

        stage_name = temporary_helper_name("__dag_node", reserved=reserved_names)
        compute_started_at = time.perf_counter()
        sorted_df = sorted_df.with_columns(compile_expr(rewritten_expr).alias(stage_name))
        compute_time_ms = (time.perf_counter() - compute_started_at) * 1000
        bytes_estimate = estimate_column_bytes(sorted_df, stage_name)
        store_started_at = time.perf_counter()
        reserved_names.add(stage_name)
        materialized_column_by_identity[node.identity] = stage_name
        stage_cache[("dag_node", node.node_id)] = stage_name
        result_store.put_materialized(
            NodeResultStoreEntry(
                node_id=node.node_id,
                identity=node.identity,
                materialization_kind=node.materialization_kind,
                materialization_reason=node.materialization_reason,
                materialization_eligibility=node.materialization_eligibility,
                column_name=stage_name,
            ),
            compute_time_ms=compute_time_ms,
            store_write_time_ms=(time.perf_counter() - store_started_at) * 1000,
            materialized_at_step=(
                getattr(lifecycle_plan, "producer_step", None)
                if lifecycle_plan is not None
                else None
            ),
            theoretical_release_step=(
                getattr(lifecycle_plan, "last_use_step", None)
                if lifecycle_plan is not None
                else None
            ),
            bytes_estimate=bytes_estimate,
            ref_count_initial=(
                getattr(lifecycle_plan, "ref_count_initial", 0)
                if lifecycle_plan is not None
                else 0
            ),
            active_drop_eligible=(
                lifecycle_active
                and dag_cse_enabled
                and is_first_wave_candidate(
                    FirstWaveCandidateInput(
                        materialization_eligibility=node.materialization_eligibility,
                        drop_candidate=(
                            getattr(lifecycle_plan, "drop_candidate", False)
                            if lifecycle_plan is not None
                            else False
                        ),
                        drop_blocker_reason=(
                            getattr(lifecycle_plan, "drop_blocker_reason", "")
                            if lifecycle_plan is not None
                            else "missing_lifecycle_plan"
                        ),
                        structural_release_lag_steps=(
                            getattr(lifecycle_plan, "structural_release_lag_steps", 0)
                            if lifecycle_plan is not None
                            else 0
                        ),
                        node_lifecycle_class=node_lifecycle_class(node.identity),
                        bytes_estimate=bytes_estimate,
                    )
                )
            ),
        )
        if runtime is not None:
            runtime.register_stage(
                expr_key=("dag_node", node.node_id),
                column_name=stage_name,
                stage_kind="dag_shared_intermediate",
                producer_route="dag_cse",
                frame=sorted_df,
                cache_key=("dag_node", node.node_id),
            )

    return sorted_df, stage_cache


def record_cse_child_read(
    result_store: NodeResultStore,
    *,
    node_id: str,
    count: int,
    producer_step: int | None,
    lifecycle_active: bool,
) -> None:
    result_store.record_reads(
        node_id,
        read_count=count,
        consumer_count=1,
        read_step=producer_step,
    )
    result_store.record_planned_consumption(
        node_id,
        step=producer_step,
        multiplicity=count,
        active_drop_enabled=lifecycle_active,
    )


def estimate_column_bytes(frame: pl.DataFrame, column_name: str) -> int:
    try:
        return int(frame.get_column(column_name).estimated_size())
    except Exception:
        return 0
