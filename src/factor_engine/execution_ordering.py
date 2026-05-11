from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable

import polars as pl

from factor_engine.errors import ExecutionError
from factor_engine.execution_output import (
    restore_mapped_output_columns,
    restore_output_columns,
)


SegmentSpecKey = tuple[str, int | tuple[int, ...]]


@dataclass
class PreparedFrame:
    # PreparedFrame is an internal optimization helper for ordered time-series work.
    original_df: pl.DataFrame
    sorted_df: pl.DataFrame
    row_index_name: str
    segmented_views: dict[SegmentSpecKey, pl.DataFrame]

    def restore_output_columns(self, output_names: list[str]) -> pl.DataFrame:
        return restore_output_columns(self.sorted_df, self.row_index_name, output_names)

    def restore_mapped_output_columns(
        self,
        output_expressions: list[tuple[str, pl.Expr]],
    ) -> pl.DataFrame:
        return restore_mapped_output_columns(
            self.sorted_df,
            self.row_index_name,
            output_expressions,
        )


def choose_row_index_name(columns: Iterable[str], base_name: str = "__row_idx") -> str:
    row_index_name = base_name
    existing_names = set(columns)
    while row_index_name in existing_names:
        row_index_name = f"_{row_index_name}"
    return row_index_name


def validate_ordering_columns(df: pl.DataFrame, *, code_col: str, time_col: str) -> None:
    if time_col not in df.columns or code_col not in df.columns:
        raise ExecutionError(
            f"Ordered time-series execution requires columns: {code_col}, {time_col}"
        )


def build_prepared_frame(df: pl.DataFrame, *, code_col: str, time_col: str) -> PreparedFrame:
    validate_ordering_columns(df, code_col=code_col, time_col=time_col)
    row_index_name = choose_row_index_name(df.columns)
    sorted_df = df.with_row_index(row_index_name).sort([code_col, time_col])
    return PreparedFrame(
        original_df=df,
        sorted_df=sorted_df,
        row_index_name=row_index_name,
        segmented_views={},
    )
