from __future__ import annotations

import pytest
import polars as pl

from factor_engine.errors import ExecutionError
from factor_engine.execution_output import (
    append_ordered_output_columns,
    ensure_unique_output_names,
    restore_mapped_output_columns,
    restore_output_columns,
    restore_selected_columns,
)


def test_restore_selected_columns_preserves_requested_order_and_original_rows():
    sorted_df = pl.DataFrame(
        {
            "__row_idx": [2, 0, 1],
            "helper": [99, 98, 97],
            "alpha": [30, 10, 20],
            "beta": [300, 100, 200],
        }
    )

    restored = restore_selected_columns(sorted_df, "__row_idx", ["beta", "alpha"])

    assert restored.columns == ["beta", "alpha"]
    assert restored.to_dict(as_series=False) == {
        "beta": [100, 200, 300],
        "alpha": [10, 20, 30],
    }


def test_restore_output_columns_does_not_leak_helper_columns():
    sorted_df = pl.DataFrame(
        {
            "__row_idx": [1, 0],
            "helper": [10, 20],
            "alpha": [2.0, 1.0],
        }
    )

    restored = restore_output_columns(sorted_df, "__row_idx", ["alpha"])

    assert restored.columns == ["alpha"]
    assert restored.get_column("alpha").to_list() == [1.0, 2.0]


def test_restore_mapped_output_columns_preserves_aliases_and_order():
    sorted_df = pl.DataFrame(
        {
            "__row_idx": [1, 0],
            "value": [5, 3],
        }
    )

    restored = restore_mapped_output_columns(
        sorted_df,
        "__row_idx",
        [("alpha", pl.col("value") + 1)],
    )

    assert restored.columns == ["alpha"]
    assert restored.get_column("alpha").to_list() == [4, 6]


def test_append_ordered_output_columns_preserves_base_shape_and_output_order():
    base_df = pl.DataFrame({"code": ["a", "b"], "time": [1, 1]})
    ordered_outputs = pl.DataFrame({"beta": [20, 30], "alpha": [2, 3]})

    result = append_ordered_output_columns(base_df, ordered_outputs, ["alpha", "beta"])

    assert result.columns == ["code", "time", "alpha", "beta"]
    assert result.get_column("alpha").to_list() == [2, 3]
    assert result.get_column("beta").to_list() == [20, 30]


def test_ensure_unique_output_names_preserves_duplicate_guard():
    ensure_unique_output_names(["alpha", "beta"])

    with pytest.raises(ExecutionError, match="Duplicate output name: alpha"):
        ensure_unique_output_names(["alpha", "beta", "alpha"])
