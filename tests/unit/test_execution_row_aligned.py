from __future__ import annotations

import polars as pl

from factor_engine.execution_row_aligned import (
    evaluate_many_row_aligned_no_time_order,
    evaluate_row_aligned_no_time_order,
)


def test_row_aligned_single_expression_preserves_rows_and_columns():
    df = pl.DataFrame({"x": [1, 2, None], "y": [10, 20, 30]})

    result = evaluate_row_aligned_no_time_order(
        df,
        pl.col("x") + pl.col("y"),
        output_name="alpha",
    )

    assert result.columns == ["x", "y", "alpha"]
    assert result.get_column("alpha").to_list() == [11, 22, None]


def test_row_aligned_batch_preserves_output_order():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]})

    result = evaluate_many_row_aligned_no_time_order(
        df,
        [
            ("alpha", pl.col("x") + pl.col("y")),
            ("beta", pl.col("y") - pl.col("x")),
        ],
    )

    assert result.columns == ["x", "y", "alpha", "beta"]
    assert result.get_column("alpha").to_list() == [11, 22, 33]
    assert result.get_column("beta").to_list() == [9, 18, 27]


def test_row_aligned_where_and_null_behavior_is_polars_native():
    df = pl.DataFrame({"x": [1, None, 3]})
    expr = pl.when(pl.col("x").is_null()).then(0).otherwise(pl.col("x"))

    result = evaluate_row_aligned_no_time_order(df, expr, output_name="filled")

    assert result.get_column("filled").to_list() == [1, 0, 3]


def test_row_aligned_does_not_create_helper_columns():
    df = pl.DataFrame({"x": [1, 2]})

    result = evaluate_many_row_aligned_no_time_order(
        df,
        [("alpha", pl.col("x") * 2)],
    )

    assert result.columns == ["x", "alpha"]
