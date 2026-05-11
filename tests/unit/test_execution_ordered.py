from __future__ import annotations

import polars as pl

from factor_engine.execution_ordered import (
    evaluate_many_row_aligned_time_ordered,
    evaluate_row_aligned_time_ordered,
)
from factor_engine.execution_ordering import build_prepared_frame


def test_ordered_row_aligned_restores_original_order():
    df = pl.DataFrame(
        {
            "code": ["b", "a", "b", "a"],
            "time": [2, 2, 1, 1],
            "value": [20, 12, 10, 11],
        }
    )
    prepared = build_prepared_frame(df, code_col="code", time_col="time")

    result = evaluate_row_aligned_time_ordered(
        prepared,
        pl.col("value").shift(1).over("code"),
        output_name="delay_1",
    )

    assert result.columns == ["code", "time", "value", "delay_1"]
    assert result.get_column("delay_1").to_list() == [10, 11, None, None]


def test_ordered_batch_preserves_output_order_and_values():
    df = pl.DataFrame(
        {
            "code": ["b", "a", "b", "a"],
            "time": [2, 2, 1, 1],
            "value": [20, 12, 10, 11],
        }
    )
    prepared = build_prepared_frame(df, code_col="code", time_col="time")

    result = evaluate_many_row_aligned_time_ordered(
        prepared,
        [
            ("delay_1", pl.col("value").shift(1).over("code")),
            ("delta_1", pl.col("value") - pl.col("value").shift(1).over("code")),
        ],
    )

    assert result.columns == ["delay_1", "delta_1"]
    assert result.get_column("delay_1").to_list() == [10, 11, None, None]
    assert result.get_column("delta_1").to_list() == [10, 1, None, None]


def test_ordered_window_expression_uses_sorted_code_time_order():
    df = pl.DataFrame(
        {
            "code": ["b", "a", "b", "a"],
            "time": [2, 2, 1, 1],
            "value": [20, 12, 10, 11],
        }
    )
    prepared = build_prepared_frame(df, code_col="code", time_col="time")

    result = evaluate_many_row_aligned_time_ordered(
        prepared,
        [("ts_sum_2", pl.col("value").rolling_sum(2).over("code"))],
    )

    assert result.get_column("ts_sum_2").to_list() == [30, 23, None, None]
