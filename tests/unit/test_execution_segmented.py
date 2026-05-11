from __future__ import annotations

import polars as pl

from factor_engine.execution_ordering import build_prepared_frame
from factor_engine.execution_segmented import (
    evaluate_many_segmented_columns,
    evaluate_segmented_column,
    get_segmented_view,
    prepare_segmented_sorted_df,
)


CODE_POS = "__code_pos"
CODE_LEN = "__code_len"
SEGMENT_ID = "__segment_id"


def _prepared():
    df = pl.DataFrame(
        {
            "code": ["b", "a", "b", "a"],
            "time": [2, 2, 1, 1],
            "value": [20, 12, 10, 11],
        }
    )
    return df, build_prepared_frame(df, code_col="code", time_col="time")


def _prepare_view(sorted_df: pl.DataFrame, segment_spec_key):
    return prepare_segmented_sorted_df(
        sorted_df,
        segment_spec_key=segment_spec_key,
        code_col="code",
        code_pos_name=CODE_POS,
        code_len_name=CODE_LEN,
        segment_id_name=SEGMENT_ID,
    )


def test_prepare_segmented_sorted_df_adds_equal_count_segments():
    _df, prepared = _prepared()

    segmented = _prepare_view(prepared.sorted_df, ("equal", 2))

    assert {CODE_POS, CODE_LEN, SEGMENT_ID} <= set(segmented.columns)
    assert segmented.select(["code", "time", SEGMENT_ID]).to_dict(as_series=False) == {
        "code": ["a", "a", "b", "b"],
        "time": [1, 2, 1, 2],
        SEGMENT_ID: [0, 1, 0, 1],
    }


def test_prepare_segmented_sorted_df_adds_length_segments():
    _df, prepared = _prepared()

    segmented = _prepare_view(prepared.sorted_df, ("length", (1, 1)))

    assert segmented.get_column(SEGMENT_ID).to_list() == [0, 1, 0, 1]


def test_get_segmented_view_caches_by_segment_spec():
    _df, prepared = _prepared()
    calls = 0

    def prepare(sorted_df, key):
        nonlocal calls
        calls += 1
        return _prepare_view(sorted_df, key)

    first = get_segmented_view(prepared, ("equal", 2), prepare_segmented_sorted_df=prepare)
    second = get_segmented_view(prepared, ("equal", 2), prepare_segmented_sorted_df=prepare)

    assert calls == 1
    assert first is second


def test_evaluate_segmented_column_restores_original_order():
    df, prepared = _prepared()

    result = evaluate_segmented_column(
        prepared,
        df,
        "expr",
        output_name="alpha",
        get_segment_spec_key=lambda _expr: ("equal", 2),
        get_segmented_view_for_key=lambda key: _prepare_view(prepared.sorted_df, key),
        compile_expr=lambda _expr: pl.sum("value").over(["code", SEGMENT_ID]),
    )

    assert result.columns == ["code", "time", "value", "alpha"]
    assert result.get_column("alpha").to_list() == [20, 12, 10, 11]


def test_evaluate_many_segmented_columns_preserves_output_order():
    df, prepared = _prepared()

    result = evaluate_many_segmented_columns(
        prepared,
        df,
        [("alpha", "expr-a", None), ("beta", "expr-b", None)],
        get_segment_spec_key=lambda _expr: ("length", (1, 1)),
        get_segmented_view_for_key=lambda key: _prepare_view(prepared.sorted_df, key),
        compile_expr=lambda expr: (
            pl.sum("value").over(["code", SEGMENT_ID])
            if expr == "expr-a"
            else pl.count("value").over(["code", SEGMENT_ID])
        ),
    )

    assert result.columns == ["code", "time", "value", "alpha", "beta"]
    assert result.get_column("alpha").to_list() == [20, 12, 10, 11]
    assert result.get_column("beta").to_list() == [1, 1, 1, 1]
