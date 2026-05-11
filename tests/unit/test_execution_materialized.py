from __future__ import annotations

import polars as pl

from factor_engine.execution_materialized import (
    evaluate_many_staged_columns,
    evaluate_materialized_ordered_column,
    evaluate_staged_column,
)
from factor_engine.execution_ordering import build_prepared_frame


def test_evaluate_staged_column_restores_original_order_without_helper_leak():
    df = pl.DataFrame(
        {
            "code": ["b", "a", "b", "a"],
            "time": [2, 2, 1, 1],
            "value": [20, 12, 10, 11],
        }
    )
    prepared = build_prepared_frame(df, code_col="code", time_col="time")

    def materialize(sorted_df: pl.DataFrame):
        return sorted_df.with_columns((pl.col("value") + 1).alias("__stage_value")), "__stage_value", {}

    result = evaluate_staged_column(
        prepared,
        df,
        output_name="alpha",
        materialize_staged_chain=materialize,
    )

    assert result.columns == ["code", "time", "value", "alpha"]
    assert result.get_column("alpha").to_list() == [21, 13, 11, 12]


def test_evaluate_many_staged_columns_preserves_output_order():
    df = pl.DataFrame(
        {
            "code": ["b", "a", "b", "a"],
            "time": [2, 2, 1, 1],
            "value": [20, 12, 10, 11],
        }
    )
    prepared = build_prepared_frame(df, code_col="code", time_col="time")

    def materialize(sorted_df, staged_plan, reserved_names, stage_cache):
        stage_name = f"__stage_{staged_plan}"
        return sorted_df.with_columns((pl.col("value") + staged_plan).alias(stage_name)), stage_name, stage_cache

    result = evaluate_many_staged_columns(
        prepared,
        df,
        [("alpha", 1), ("beta", 2)],
        materialize_staged_chain=materialize,
    )

    assert result.columns == ["code", "time", "value", "alpha", "beta"]
    assert result.get_column("alpha").to_list() == [21, 13, 11, 12]
    assert result.get_column("beta").to_list() == [22, 14, 12, 13]


def test_evaluate_materialized_ordered_column_restores_boundary_output():
    df = pl.DataFrame(
        {
            "code": ["b", "a", "b", "a"],
            "time": [2, 2, 1, 1],
            "value": [20, 12, 10, 11],
        }
    )
    prepared = build_prepared_frame(df, code_col="code", time_col="time")

    def materialize(sorted_df: pl.DataFrame):
        return sorted_df.with_columns((pl.col("value") * 2).alias("__materialized")), "__materialized", {}

    result = evaluate_materialized_ordered_column(
        prepared,
        df,
        output_name="alpha",
        materialize_ordered_plan=materialize,
    )

    assert result.columns == ["code", "time", "value", "alpha"]
    assert result.get_column("alpha").to_list() == [40, 24, 20, 22]
