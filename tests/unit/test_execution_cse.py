from __future__ import annotations

from types import SimpleNamespace

import polars as pl

from factor_engine.ast_nodes import VariableNode
from factor_engine.dag import NodeResultStore
from factor_engine.execution_cse import (
    estimate_column_bytes,
    materialize_shared_dag_nodes_on_sorted_df,
    record_cse_child_read,
)


def test_record_cse_child_read_updates_store_stats_without_changing_schema():
    store = NodeResultStore()
    store.register_policy(
        node_id="node-a",
        identity=("var", "close"),
        materialization_kind="shared_intermediate",
        consumer_count=2,
    )

    record_cse_child_read(
        store,
        node_id="node-a",
        count=2,
        producer_step=3,
        lifecycle_active=True,
    )

    stats = store.stats["node-a"]
    assert stats.node_store_read_count == 2
    assert stats.reuse_consumer_count == 1
    assert stats.last_read_step == 3


def test_materialize_shared_dag_nodes_records_stage_and_store_entry():
    node = SimpleNamespace(
        node_id="node-a",
        identity=("var", "close"),
        expr=VariableNode("close"),
        materialize=True,
        materialization_kind="shared_intermediate",
        materialization_reason="shared_reuse",
        materialization_eligibility="materialize_for_reuse",
    )
    store = NodeResultStore()
    frame = pl.DataFrame({"close": [1, 2, 3]})
    reserved = set(frame.columns)
    stage_cache: dict[tuple, str] = {}
    materialized: dict[tuple, str] = {}

    result, stage_cache = materialize_shared_dag_nodes_on_sorted_df(
        frame,
        dag_nodes=[node],
        reserved_names=reserved,
        stage_cache=stage_cache,
        result_store=store,
        materialized_column_by_identity=materialized,
        dag_nodes_by_identity={node.identity: node},
        lifecycle_plans_by_node_id={},
        runtime=None,
        lifecycle_active=False,
        dag_cse_enabled=True,
        rewrite_expr_with_materialized_nodes=lambda expr, **_kwargs: (expr, {}),
        compile_expr=lambda _expr: pl.col("close") + 1,
        temporary_helper_name=lambda _base, **_kwargs: "__dag_node",
        node_lifecycle_class=lambda _identity: "other",
    )

    assert result.get_column("__dag_node").to_list() == [2, 3, 4]
    assert stage_cache == {("dag_node", "node-a"): "__dag_node"}
    assert materialized == {("var", "close"): "__dag_node"}
    assert store.get_materialized("node-a").column_name == "__dag_node"


def test_materialize_shared_dag_nodes_skips_existing_materialized_identity():
    node = SimpleNamespace(
        node_id="node-a",
        identity=("var", "close"),
        expr=VariableNode("close"),
        materialize=True,
    )
    frame = pl.DataFrame({"close": [1]})

    result, stage_cache = materialize_shared_dag_nodes_on_sorted_df(
        frame,
        dag_nodes=[node],
        reserved_names=set(frame.columns),
        stage_cache={},
        result_store=NodeResultStore(),
        materialized_column_by_identity={("var", "close"): "__existing"},
        dag_nodes_by_identity={},
        lifecycle_plans_by_node_id={},
        runtime=None,
        lifecycle_active=False,
        dag_cse_enabled=True,
        rewrite_expr_with_materialized_nodes=lambda *_args, **_kwargs: (_fail(), {}),
        compile_expr=lambda _expr: _fail(),
        temporary_helper_name=lambda *_args, **_kwargs: _fail(),
        node_lifecycle_class=lambda _identity: "other",
    )

    assert result is frame
    assert stage_cache == {}


def test_estimate_column_bytes_is_non_negative_for_existing_column():
    assert estimate_column_bytes(pl.DataFrame({"x": [1, 2]}), "x") >= 0


def _fail():
    raise AssertionError("callback should not be called")
