from __future__ import annotations

from collections.abc import Callable
from typing import Any

import polars as pl

from factor_engine.errors import ExecutionError
from factor_engine.execution_ordering import PreparedFrame, SegmentSpecKey
from factor_engine.execution_output import restore_selected_columns


def get_segmented_view(
    prepared: PreparedFrame,
    segment_spec_key: SegmentSpecKey,
    *,
    prepare_segmented_sorted_df: Callable[[pl.DataFrame, SegmentSpecKey], pl.DataFrame],
) -> pl.DataFrame:
    segmented_view = prepared.segmented_views.get(segment_spec_key)
    if segmented_view is not None:
        return segmented_view

    segmented_view = prepare_segmented_sorted_df(prepared.sorted_df, segment_spec_key)
    prepared.segmented_views[segment_spec_key] = segmented_view
    return segmented_view


def evaluate_segmented_column(
    prepared: PreparedFrame,
    base_df: pl.DataFrame,
    expr: Any,
    *,
    output_name: str,
    get_segment_spec_key: Callable[[Any], SegmentSpecKey],
    get_segmented_view_for_key: Callable[[SegmentSpecKey], pl.DataFrame],
    compile_expr: Callable[[Any], pl.Expr],
) -> pl.DataFrame:
    segment_spec_key = get_segment_spec_key(expr)
    segmented_df = get_segmented_view_for_key(segment_spec_key)
    compiled = compile_expr(expr)
    result_df = segmented_df.with_columns(compiled.alias(output_name))

    return restore_selected_columns(
        result_df,
        prepared.row_index_name,
        [*base_df.columns, output_name],
    )


def evaluate_many_segmented_columns(
    prepared: PreparedFrame,
    base_df: pl.DataFrame,
    items: list[tuple[str, Any, Any]],
    *,
    get_segment_spec_key: Callable[[Any], SegmentSpecKey],
    get_segmented_view_for_key: Callable[[SegmentSpecKey], pl.DataFrame],
    compile_expr: Callable[[Any], pl.Expr],
) -> pl.DataFrame:
    if not items:
        return base_df

    outputs_by_name: dict[str, pl.Series] = {}
    items_by_segment_spec: dict[SegmentSpecKey, list[tuple[str, Any]]] = {}

    for output_name, expr, _validation in items:
        segment_spec_key = get_segment_spec_key(expr)
        items_by_segment_spec.setdefault(segment_spec_key, []).append((output_name, expr))

    for segment_spec_key, grouped_items in items_by_segment_spec.items():
        segmented_df = get_segmented_view_for_key(segment_spec_key)
        compiled = [
            compile_expr(expr).alias(output_name)
            for output_name, expr in grouped_items
        ]
        grouped_result = restore_selected_columns(
            segmented_df.select([prepared.row_index_name, *compiled]),
            prepared.row_index_name,
            [output_name for output_name, _expr in grouped_items],
        )
        for output_name, _expr in grouped_items:
            outputs_by_name[output_name] = grouped_result.get_column(output_name)

    return base_df.with_columns(
        [outputs_by_name[output_name] for output_name, _expr, _validation in items]
    )


def prepare_segmented_sorted_df(
    sorted_df: pl.DataFrame,
    *,
    segment_spec_key: SegmentSpecKey,
    code_col: str,
    code_pos_name: str,
    code_len_name: str,
    segment_id_name: str,
) -> pl.DataFrame:
    with_group_position = sorted_df.with_columns(
        [
            (pl.col(code_col).cum_count().over(code_col) - 1).alias(code_pos_name),
            pl.len().over(code_col).alias(code_len_name),
        ]
    )

    kind, spec_value = segment_spec_key
    if kind == "equal":
        if not isinstance(spec_value, int):
            raise ExecutionError("Internal error: invalid equal segment specification")
        segment_id_expr = build_equal_segment_id_expr(
            spec_value,
            code_pos_name=code_pos_name,
            code_len_name=code_len_name,
        )
    elif kind == "length":
        if not isinstance(spec_value, tuple):
            raise ExecutionError("Internal error: invalid length segment specification")
        ensure_segment_lengths_cover_groups(
            with_group_position,
            spec_value,
            code_len_name=code_len_name,
        )
        segment_id_expr = build_length_segment_id_expr(spec_value, code_pos_name=code_pos_name)
    else:
        raise ExecutionError(f"Internal error: unsupported segment specification kind '{kind}'")

    return with_group_position.with_columns(segment_id_expr.alias(segment_id_name))


def build_equal_segment_id_expr(
    segment_count: int,
    *,
    code_pos_name: str,
    code_len_name: str,
) -> pl.Expr:
    code_pos = pl.col(code_pos_name)
    code_len = pl.col(code_len_name)
    segment_count_lit = pl.lit(segment_count)
    base_size = code_len // segment_count_lit
    larger_segment_count = code_len % segment_count_lit
    larger_segment_rows = (base_size + 1) * larger_segment_count

    return (
        pl.when(code_pos < larger_segment_rows)
        .then(code_pos // (base_size + 1))
        .otherwise(
            pl.when(base_size > 0)
            .then(larger_segment_count + ((code_pos - larger_segment_rows) // base_size))
            .otherwise(code_pos)
        )
        .cast(pl.Int64)
    )


def build_length_segment_id_expr(lengths: tuple[int, ...], *, code_pos_name: str) -> pl.Expr:
    code_pos = pl.col(code_pos_name)
    cumulative = 0
    segment_id_expr: pl.Expr | None = None

    for index, length in enumerate(lengths):
        cumulative += length
        if segment_id_expr is None:
            segment_id_expr = pl.when(code_pos < cumulative).then(index)
        else:
            segment_id_expr = segment_id_expr.when(code_pos < cumulative).then(index)

    if segment_id_expr is None:
        raise ExecutionError("Internal error: empty length segment specification")

    return segment_id_expr.otherwise(len(lengths) - 1).cast(pl.Int64)


def ensure_segment_lengths_cover_groups(
    prepared_df: pl.DataFrame,
    lengths: tuple[int, ...],
    *,
    code_len_name: str,
) -> None:
    total_length = sum(lengths)
    uncovered = prepared_df.filter(pl.col(code_len_name) > total_length).head(1)
    if uncovered.height > 0:
        raise ExecutionError("segment lengths do not cover full group")
