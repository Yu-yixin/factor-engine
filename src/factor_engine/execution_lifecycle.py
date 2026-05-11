from __future__ import annotations

from typing import Any

import polars as pl

from factor_engine.dag import NodeResultStore
from factor_engine.errors import ExecutionError
from factor_engine.lifecycle import is_lifecycle_active


def materialized_helper_has_nested_dependency(
    *,
    result_store: NodeResultStore,
    lifecycle_plans_by_node_id: dict[str, object],
) -> bool:
    materialized_node_ids = {
        stats.node_id
        for stats in result_store.stats.values()
        if stats.compute_count > 0
        and stats.helper_column_name is not None
        and stats.materialization_kind == "shared_intermediate"
    }
    return any(
        getattr(plan, "parent_node_id", None) in materialized_node_ids
        for node_id, plan in lifecycle_plans_by_node_id.items()
        if node_id in materialized_node_ids
    )


def append_helper_trace_event(stats: Any, event: str) -> None:
    if event in stats.nested_helper_trace_events:
        return
    stats.nested_helper_trace_events = (*stats.nested_helper_trace_events, event)


def revalidate_helper_drop(
    *,
    stats: Any,
    frame: pl.DataFrame,
    output_source_columns: set[str],
) -> tuple[bool, str]:
    column_name = stats.helper_column_name
    if stats.helper_dropped_at_step is not None:
        return False, "already_dropped"
    if column_name is None or column_name not in frame.columns:
        return False, "not_in_frame"
    if column_name in output_source_columns:
        return False, "output_pinned"
    if stats.helper_drop_blocker_reason:
        return False, stats.helper_drop_blocker_reason
    if not stats.helper_drop_candidate:
        return False, stats.nested_helper_miss_reason or "unsupported_shape"
    if stats.helper_drop_safe_step is None:
        return False, "safe_step_mismatch"
    return True, ""


def nested_drop_order_valid(
    *,
    result_store: NodeResultStore,
    lifecycle_plans_by_node_id: dict[str, object],
) -> bool:
    for stats in result_store.stats.values():
        lifecycle_plan = lifecycle_plans_by_node_id.get(stats.node_id)
        parent_node_id = (
            getattr(lifecycle_plan, "parent_node_id", None)
            if lifecycle_plan is not None
            else None
        )
        if parent_node_id is None:
            continue
        parent_stats = result_store.stats.get(parent_node_id)
        if parent_stats is None:
            continue
        if stats.dropped_at_step is None or parent_stats.dropped_at_step is None:
            continue
        if stats.dropped_at_step > parent_stats.dropped_at_step:
            return False
    return True


def assert_lifecycle_step_model(
    *,
    result_store: NodeResultStore,
    lifecycle_plans_by_node_id: dict[str, object],
    restore_assemble_step: int,
    append_step: int,
    finalize_step: int,
    batch_end_step: int,
    nested_drop_order_valid: bool,
    lifecycle_mode: str,
) -> None:
    max_last_use_step = max(
        (
            getattr(plan, "last_use_step", 0) or 0
            for plan in lifecycle_plans_by_node_id.values()
        ),
        default=0,
    )
    if not (
        batch_end_step >= finalize_step >= append_step >= restore_assemble_step >= max_last_use_step
    ):
        raise ExecutionError(
            "Lifecycle step ordering invariant failed: expected "
            "producer/consumer -> restore_assemble -> append -> finalize -> batch_end"
        )

    for stats in result_store.stats.values():
        if stats.helper_dropped_at_step is not None:
            if (
                stats.helper_drop_safe_step is None
                or stats.helper_dropped_at_step < stats.helper_drop_safe_step
            ):
                raise ExecutionError(
                    f"Helper lifecycle dropped node {stats.node_id} before safe step"
                )
            if (
                stats.helper_last_use_step is not None
                and stats.helper_drop_safe_step < stats.helper_last_use_step
            ):
                raise ExecutionError(
                    f"Helper lifecycle safe step precedes last use for node {stats.node_id}"
                )
        if stats.dropped_at_step is None:
            continue
        if stats.drop_expected_step != stats.theoretical_release_step:
            raise ExecutionError(
                f"Lifecycle drop expected step drifted for node {stats.node_id}"
            )
        if stats.drop_expected_step is None or stats.dropped_at_step < stats.drop_expected_step:
            raise ExecutionError(
                f"Lifecycle dropped node {stats.node_id} before its expected step"
            )

    if is_lifecycle_active(lifecycle_mode) and not nested_drop_order_valid:
        raise ExecutionError("Lifecycle nested drop order invariant failed")
