from __future__ import annotations

from collections.abc import Callable
from typing import Any

import polars as pl

from factor_engine.execution_ordering import PreparedFrame
from factor_engine.execution_output import append_ordered_output_columns, restore_selected_columns


MaterializeStagedChain = Callable[
    [pl.DataFrame],
    tuple[pl.DataFrame, str, dict[tuple, str]],
]
MaterializeOrderedPlan = Callable[
    [pl.DataFrame],
    tuple[pl.DataFrame, str, dict[tuple, str]],
]


def evaluate_staged_column(
    prepared: PreparedFrame,
    base_df: pl.DataFrame,
    *,
    output_name: str,
    materialize_staged_chain: MaterializeStagedChain,
) -> pl.DataFrame:
    sorted_df, final_stage_name, _stage_cache = materialize_staged_chain(prepared.sorted_df)
    if final_stage_name != output_name:
        sorted_df = sorted_df.with_columns(pl.col(final_stage_name).alias(output_name))

    return restore_selected_columns(
        sorted_df,
        prepared.row_index_name,
        [*base_df.columns, output_name],
    )


def evaluate_many_staged_columns(
    prepared: PreparedFrame,
    base_df: pl.DataFrame,
    items: list[tuple[str, Any]],
    *,
    materialize_staged_chain: Callable[
        [pl.DataFrame, Any, set[str], dict[tuple, str]],
        tuple[pl.DataFrame, str, dict[tuple, str]],
    ],
) -> pl.DataFrame:
    if not items:
        return base_df

    sorted_df = prepared.sorted_df
    reserved_names = set(sorted_df.columns)
    output_names: list[str] = []
    stage_cache: dict[tuple, str] = {}
    output_stage_names: dict[str, str] = {}

    for output_name, staged_plan in items:
        sorted_df, final_stage_name, stage_cache = materialize_staged_chain(
            sorted_df,
            staged_plan,
            reserved_names,
            stage_cache,
        )
        output_stage_names[output_name] = final_stage_name
        output_names.append(output_name)

    sorted_df = sorted_df.with_columns(
        [pl.col(output_stage_names[output_name]).alias(output_name) for output_name in output_names]
    )
    prepared.sorted_df = sorted_df
    ordered_outputs = prepared.restore_output_columns(output_names)
    return append_ordered_output_columns(base_df, ordered_outputs, output_names)


def evaluate_materialized_ordered_column(
    prepared: PreparedFrame,
    base_df: pl.DataFrame,
    *,
    output_name: str,
    materialize_ordered_plan: MaterializeOrderedPlan,
) -> pl.DataFrame:
    sorted_df, final_stage_name, _stage_cache = materialize_ordered_plan(prepared.sorted_df)
    if final_stage_name != output_name:
        sorted_df = sorted_df.with_columns(pl.col(final_stage_name).alias(output_name))

    return restore_selected_columns(
        sorted_df,
        prepared.row_index_name,
        [*base_df.columns, output_name],
    )
