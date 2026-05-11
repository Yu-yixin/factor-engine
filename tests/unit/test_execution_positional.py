from __future__ import annotations

import polars as pl

from factor_engine.ast_nodes import CallNode, NumberNode, VariableNode
from factor_engine.execution_ordering import build_prepared_frame
from factor_engine.execution_positional import (
    evaluate_positional_kernel,
    evaluate_positional_ordered_column,
    materialize_positional_call_on_sorted_df,
    scan_group_positional_extreme,
)


def test_scan_group_positional_extreme_preserves_recent_tie_rule():
    values = [1, 3, 3, 2]
    output: list[int | None] = [None] * len(values)

    scan_group_positional_extreme(values, 0, len(values), 3, mode="argmax", output=output)

    assert output == [0, 0, 0, 1]


def test_evaluate_positional_kernel_uses_python_fallback_when_native_unavailable():
    series, profile = evaluate_positional_kernel(
        pl.Series("close", [1.0, 3.0, 2.0, 5.0]),
        pl.Series("code", ["a", "a", "a", "a"]),
        3,
        mode="argmax",
        native_kernel=lambda *_args, **_kwargs: None,
    )

    assert series.to_list() == [0, 0, 1, 0]
    assert profile["native_kernel_used"] is False
    assert profile["python_object_bridge_used"] is True


def test_evaluate_positional_ordered_column_restores_original_order():
    df = pl.DataFrame(
        {
            "code": ["b", "a", "b", "a"],
            "time": [2, 2, 1, 1],
            "close": [20, 12, 10, 11],
        }
    )
    prepared = build_prepared_frame(df, code_col="code", time_col="time")

    def materialize(sorted_df: pl.DataFrame):
        return sorted_df.with_columns((pl.col("close") * 0).alias("__positional")), "__positional", {}

    result = evaluate_positional_ordered_column(
        prepared,
        df,
        VariableNode("unused"),
        output_name="argmaxed",
        materialize_positional_call=materialize,
    )

    assert result.columns == ["code", "time", "close", "argmaxed"]
    assert result.get_column("argmaxed").to_list() == [0, 0, 0, 0]


def test_materialize_positional_call_reuses_stage_cache_without_recomputing():
    expr = CallNode("argmax", [VariableNode("close"), NumberNode(2.0)])
    sorted_df = pl.DataFrame({"code": ["a"], "close": [1.0]})
    cache_key = ("positional_kernel", "argmax", ("var", "close"), 2)

    result_df, stage_name, stage_cache = materialize_positional_call_on_sorted_df(
        sorted_df,
        expr=expr,
        reserved_names=set(sorted_df.columns),
        stage_cache={cache_key: "__cached"},
        expect_positive_numeric_literal=lambda _expr, _name: 2,
        expr_key=lambda item: ("var", item.name) if isinstance(item, VariableNode) else ("call", "argmax"),
        materialize_expr_on_sorted_df=lambda *_args, **_kwargs: (_fail(), "", {}),
        temporary_helper_name=lambda *_args, **_kwargs: "__stage_value",
        attach_positional_kernel_from_stage=lambda *_args, **_kwargs: _fail(),
    )

    assert result_df is sorted_df
    assert stage_name == "__cached"
    assert stage_cache[cache_key] == "__cached"


def _fail():
    raise AssertionError("callback should not be called")
