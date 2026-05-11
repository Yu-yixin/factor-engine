from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

import polars as pl

from factor_engine.errors import ExecutionError


def restore_selected_columns(
    sorted_df: pl.DataFrame,
    row_index_name: str,
    columns: Sequence[str],
) -> pl.DataFrame:
    return (
        sorted_df.select([row_index_name, *columns])
        .sort(row_index_name)
        .drop(row_index_name)
    )


def restore_output_columns(
    sorted_df: pl.DataFrame,
    row_index_name: str,
    output_names: Sequence[str],
) -> pl.DataFrame:
    return restore_selected_columns(sorted_df, row_index_name, output_names)


def restore_mapped_output_columns(
    sorted_df: pl.DataFrame,
    row_index_name: str,
    output_expressions: Sequence[tuple[str, pl.Expr]],
) -> pl.DataFrame:
    return (
        sorted_df.select(
            [
                row_index_name,
                *[expr.alias(output_name) for output_name, expr in output_expressions],
            ]
        )
        .sort(row_index_name)
        .drop(row_index_name)
    )


def append_ordered_output_columns(
    base_df: pl.DataFrame,
    ordered_outputs: pl.DataFrame,
    output_names: Sequence[str],
) -> pl.DataFrame:
    return base_df.with_columns([ordered_outputs.get_column(output_name) for output_name in output_names])


def ensure_unique_output_names(output_names: Sequence[str]) -> None:
    duplicate_names = [name for name, count in Counter(output_names).items() if count > 1]
    if duplicate_names:
        raise ExecutionError(f"Duplicate output name: {duplicate_names[0]}")
