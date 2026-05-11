from __future__ import annotations

import polars as pl

from factor_engine.execution_ordering import PreparedFrame
from factor_engine.execution_output import restore_selected_columns


def evaluate_row_aligned_time_ordered(
    prepared: PreparedFrame,
    compiled: pl.Expr,
    *,
    output_name: str,
) -> pl.DataFrame:
    sorted_df = prepared.sorted_df.with_columns(compiled.alias(output_name))
    return restore_selected_columns(
        sorted_df,
        prepared.row_index_name,
        [column for column in sorted_df.columns if column != prepared.row_index_name],
    )


def evaluate_many_row_aligned_time_ordered(
    prepared: PreparedFrame,
    items: list[tuple[str, pl.Expr]],
) -> pl.DataFrame:
    compiled = [expr.alias(output_name) for output_name, expr in items]
    prepared.sorted_df = prepared.sorted_df.with_columns(compiled)
    return prepared.restore_output_columns([output_name for output_name, _ in items])
