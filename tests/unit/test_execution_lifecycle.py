from __future__ import annotations

from types import SimpleNamespace

import polars as pl
import pytest

from factor_engine.dag import NodeResultStore
from factor_engine.errors import ExecutionError
from factor_engine.execution_lifecycle import (
    append_helper_trace_event,
    assert_lifecycle_step_model,
    materialized_helper_has_nested_dependency,
    nested_drop_order_valid,
    revalidate_helper_drop,
)


def _stats(node_id: str, **overrides):
    values = {
        "node_id": node_id,
        "compute_count": 1,
        "helper_column_name": f"__{node_id}",
        "materialization_kind": "shared_intermediate",
        "nested_helper_trace_events": (),
        "helper_dropped_at_step": None,
        "helper_drop_safe_step": 3,
        "helper_last_use_step": 2,
        "dropped_at_step": None,
        "drop_expected_step": None,
        "theoretical_release_step": None,
        "helper_drop_blocker_reason": "",
        "helper_drop_candidate": True,
        "nested_helper_miss_reason": "",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_materialized_helper_has_nested_dependency_detects_parent_child_relation():
    store = NodeResultStore()
    store.stats["parent"] = _stats("parent", helper_column_name="__parent")
    store.stats["child"] = _stats("child", helper_column_name="__child")

    assert materialized_helper_has_nested_dependency(
        result_store=store,
        lifecycle_plans_by_node_id={"child": SimpleNamespace(parent_node_id="parent")},
    )


def test_append_helper_trace_event_is_idempotent():
    stats = _stats("node-a")

    append_helper_trace_event(stats, "nested_helper_candidate")
    append_helper_trace_event(stats, "nested_helper_candidate")

    assert stats.nested_helper_trace_events == ("nested_helper_candidate",)


def test_revalidate_helper_drop_rejects_pinned_or_missing_columns():
    frame = pl.DataFrame({"__node": [1]})
    stats = _stats("node", helper_column_name="__node")

    assert revalidate_helper_drop(
        stats=stats,
        frame=frame,
        output_source_columns={"__node"},
    ) == (False, "output_pinned")

    stats.helper_column_name = "__missing"
    assert revalidate_helper_drop(
        stats=stats,
        frame=frame,
        output_source_columns=set(),
    ) == (False, "not_in_frame")


def test_nested_drop_order_valid_rejects_child_drop_after_parent():
    store = NodeResultStore()
    store.stats["parent"] = _stats("parent", dropped_at_step=4)
    store.stats["child"] = _stats("child", dropped_at_step=5)

    assert not nested_drop_order_valid(
        result_store=store,
        lifecycle_plans_by_node_id={"child": SimpleNamespace(parent_node_id="parent")},
    )


def test_assert_lifecycle_step_model_preserves_ordering_invariant():
    store = NodeResultStore()
    store.stats["node-a"] = _stats(
        "node-a",
        dropped_at_step=4,
        drop_expected_step=4,
        theoretical_release_step=4,
    )

    assert_lifecycle_step_model(
        result_store=store,
        lifecycle_plans_by_node_id={"node-a": SimpleNamespace(last_use_step=2)},
        restore_assemble_step=3,
        append_step=4,
        finalize_step=5,
        batch_end_step=6,
        nested_drop_order_valid=True,
        lifecycle_mode="off",
    )

    with pytest.raises(ExecutionError, match="Lifecycle step ordering invariant failed"):
        assert_lifecycle_step_model(
            result_store=store,
            lifecycle_plans_by_node_id={"node-a": SimpleNamespace(last_use_step=10)},
            restore_assemble_step=3,
            append_step=4,
            finalize_step=5,
            batch_end_step=6,
            nested_drop_order_valid=True,
            lifecycle_mode="off",
        )
