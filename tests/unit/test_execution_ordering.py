from __future__ import annotations

import pytest
import polars as pl

from factor_engine.errors import ExecutionError
from factor_engine.execution_ordering import (
    build_prepared_frame,
    choose_row_index_name,
    validate_ordering_columns,
)


def test_build_prepared_frame_adds_row_index_and_sorts_by_code_time():
    df = pl.DataFrame(
        {
            "code": ["b", "a", "b", "a"],
            "time": [2, 2, 1, 1],
            "value": [20, 12, 10, 11],
        }
    )

    prepared = build_prepared_frame(df, code_col="code", time_col="time")

    assert prepared.row_index_name == "__row_idx"
    assert prepared.sorted_df.select(["code", "time"]).to_dict(as_series=False) == {
        "code": ["a", "a", "b", "b"],
        "time": [1, 2, 1, 2],
    }
    assert prepared.sorted_df.get_column("__row_idx").to_list() == [3, 1, 2, 0]


def test_restore_output_columns_preserves_original_input_order():
    df = pl.DataFrame(
        {
            "code": ["b", "a", "b", "a"],
            "time": [2, 2, 1, 1],
            "value": [20, 12, 10, 11],
        }
    )
    prepared = build_prepared_frame(df, code_col="code", time_col="time")

    restored = prepared.restore_output_columns(["value"])

    assert restored.get_column("value").to_list() == [20, 12, 10, 11]


def test_restore_mapped_output_columns_preserves_original_input_order():
    df = pl.DataFrame(
        {
            "code": ["b", "a", "b", "a"],
            "time": [2, 2, 1, 1],
            "value": [20, 12, 10, 11],
        }
    )
    prepared = build_prepared_frame(df, code_col="code", time_col="time")

    restored = prepared.restore_mapped_output_columns([("answer", pl.col("value") + 1)])

    assert restored.columns == ["answer"]
    assert restored.get_column("answer").to_list() == [21, 13, 11, 12]


def test_choose_row_index_name_avoids_collisions():
    assert choose_row_index_name(["__row_idx"]) == "___row_idx"
    assert choose_row_index_name(["__row_idx", "___row_idx"]) == "____row_idx"


def test_validate_ordering_columns_preserves_error_message():
    df = pl.DataFrame({"code": ["a"], "value": [1]})

    with pytest.raises(
        ExecutionError,
        match="Ordered time-series execution requires columns: code, time",
    ):
        validate_ordering_columns(df, code_col="code", time_col="time")
