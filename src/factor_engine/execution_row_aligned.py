from __future__ import annotations

import polars as pl


def evaluate_row_aligned_no_time_order(
    df: pl.DataFrame,
    compiled: pl.Expr,
    *,
    output_name: str,
) -> pl.DataFrame:
    # Pointwise and cross-sectional expressions can stay on the original row order.
    return df.with_columns(compiled.alias(output_name))


def evaluate_many_row_aligned_no_time_order(
    base_df: pl.DataFrame,
    items: list[tuple[str, pl.Expr]],
) -> pl.DataFrame:
    compiled = [expr.alias(output_name) for output_name, expr in items]
    return base_df.with_columns(compiled)
