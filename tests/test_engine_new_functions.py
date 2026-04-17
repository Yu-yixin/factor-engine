import polars as pl
import pytest

from factor_engine.engine import FactorEngine
from factor_engine.executor import Executor


def build_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [10.0, 15.0, 12.0],
            "open": [9.0, 11.0, 11.0],
        }
    )


def build_grouped_nested_window_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "time": [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3],
            "code": ["A", "B", "C", "D"] * 3,
            "industry": ["X", "X", "Y", "Y"] * 3,
            "close": [10.0, 20.0, 100.0, 200.0, 11.0, 19.0, 101.0, 199.0, 12.0, 18.0, 102.0, 198.0],
        }
    )


def assert_optional_lists_close(actual: list[object], expected: list[object]) -> None:
    assert len(actual) == len(expected)
    for observed, target in zip(actual, expected, strict=True):
        if observed is None or target is None:
            assert observed is None and target is None
            continue
        assert observed == pytest.approx(target, nan_ok=True)


def test_engine_evaluate_ts_min():
    result = FactorEngine().evaluate("ts_min(close, 2)", build_df())
    assert result["result"].to_list() == [10.0, 10.0, 12.0]


def test_engine_evaluate_ts_max():
    result = FactorEngine().evaluate("ts_max(close, 2)", build_df())
    assert result["result"].to_list() == [10.0, 15.0, 15.0]


def test_engine_evaluate_ts_median():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [5.0, 1.0, 7.0, 3.0],
        }
    )

    result = FactorEngine().evaluate("ts_median(close, 3)", df)
    assert result["result"].to_list() == [5.0, 3.0, 5.0, 3.0]


def test_engine_evaluate_argmax_and_argmin():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [5.0, 1.0, 7.0, 3.0],
        }
    )

    argmax_result = FactorEngine().evaluate("argmax(close, 3)", df)
    argmin_result = FactorEngine().evaluate("argmin(close, 3)", df)

    assert argmax_result["result"].to_list() == [0, 1, 0, 1]
    assert argmin_result["result"].to_list() == [0, 0, 1, 2]


def test_engine_evaluate_delta():
    result = FactorEngine().evaluate("delta(close, 1)", build_df())
    assert result["result"].to_list() == [None, 5.0, -3.0]


def test_engine_evaluate_pct_change():
    result = FactorEngine().evaluate("pct_change(close, 1)", build_df())
    values = result["result"].to_list()

    assert values[0] is None
    assert values[1] == pytest.approx(0.5)
    assert values[2] == pytest.approx(-0.2)


def test_engine_evaluate_scalar_math_helpers():
    df = pl.DataFrame({"close": [-3.0, 0.0, 8.0, None]})

    abs_result = FactorEngine().evaluate("abs(close)", df)
    clip_result = FactorEngine().evaluate("clip(close, -1, 5)", df)
    sign_result = FactorEngine().evaluate("sign(close)", df)

    assert abs_result["result"].to_list() == [3.0, 0.0, 8.0, None]
    assert clip_result["result"].to_list() == [-1.0, 0.0, 5.0, None]
    assert sign_result["result"].to_list() == [-1.0, 0.0, 1.0, None]


def test_engine_evaluate_alpha101_pointwise_helpers():
    df = pl.DataFrame({"close": [-4.0, 0.0, 1.0, 9.0, None]})

    signedpower_result = FactorEngine().evaluate("signedpower(close, 2)", df)
    log_result = FactorEngine().evaluate("log(abs(close))", df)

    assert signedpower_result["result"].to_list() == [-16.0, 0.0, 1.0, 81.0, None]
    assert log_result["result"].to_list()[0] == pytest.approx(1.3862943611)
    assert log_result["result"].to_list()[1] == float("-inf")
    assert log_result["result"].to_list()[4] is None


def test_engine_evaluate_scale():
    df = pl.DataFrame(
        {
            "time": [1, 1, 2, 2, 3, 3],
            "code": ["A", "B", "A", "B", "A", "B"],
            "close": [1.0, -3.0, 2.0, 4.0, None, 5.0],
        }
    )

    scale_result = FactorEngine().evaluate("scale(close)", df)

    assert_optional_lists_close(
        scale_result["result"].to_list(),
        [0.25, -0.75, 1.0 / 3.0, 2.0 / 3.0, None, 1.0],
    )


def test_engine_aliases_match_canonical_functions_in_evaluate_and_evaluate_many():
    df = build_df()
    engine = FactorEngine()

    alias_pairs = [
        ("sum(close, 2)", "ts_sum(close, 2)"),
        ("stddev(close, 2)", "ts_std(close, 2)"),
        ("min(close, 2)", "ts_min(close, 2)"),
        ("max(close, 2)", "ts_max(close, 2)"),
        ("correlation(open, close, 2)", "corr(open, close, 2)"),
        ("covariance(open, close, 2)", "cov(open, close, 2)"),
    ]

    for alias_expr, canonical_expr in alias_pairs:
        alias = engine.evaluate(alias_expr, df)["result"].to_list()
        canonical = engine.evaluate(canonical_expr, df)["result"].to_list()
        assert_optional_lists_close(alias, canonical)

    many = engine.evaluate_many(
        [
            ("alias_sum", "sum(close, 2)"),
            ("canonical_sum", "ts_sum(close, 2)"),
            ("alias_nested", "sum(abs(close - open), 2)"),
            ("canonical_nested", "ts_sum(abs(close - open), 2)"),
        ],
        df,
    )
    assert many["alias_sum"].to_list() == many["canonical_sum"].to_list()
    assert many["alias_nested"].to_list() == many["canonical_nested"].to_list()


def test_engine_new_functions_keep_result_column_contract():
    result = FactorEngine().evaluate("delta(close - open, 1)", build_df())

    assert result.columns[-1] == "result"
    assert result.height == 3


def test_engine_scalar_math_helpers_can_compose_with_time_series():
    abs_result = FactorEngine().evaluate("abs(delta(close, 1))", build_df())
    clip_result = FactorEngine().evaluate("clip(ts_mean(close, 2), 0, 12)", build_df())

    assert abs_result["result"].to_list() == [None, 5.0, 3.0]
    assert clip_result["result"].to_list() == [10.0, 12.0, 12.0]


def test_engine_evaluate_boolean_time_series_functions():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [2.0, None, 5.0],
            "open": [1.0, 1.0, 4.0],
        }
    )

    count_result = FactorEngine().evaluate("ts_count(close > open, 2)", df)
    any_result = FactorEngine().evaluate("ts_any(close > open, 2)", df)
    all_result = FactorEngine().evaluate("ts_all(close > open, 2)", df)

    assert count_result["result"].to_list() == [1, 1, 1]
    assert any_result["result"].to_list() == [True, True, True]
    assert all_result["result"].to_list() == [True, False, False]


def test_engine_evaluate_ts_rank():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [10.0, 30.0, 30.0, 20.0],
        }
    )

    result = FactorEngine().evaluate("ts_rank(close, 3, pct=true)", df)

    assert result["result"].to_list() == pytest.approx([1.0, 0.5, 0.5, 1.0])


def test_engine_evaluate_seg_mean():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [1.0, 3.0, 10.0, 14.0],
        }
    )

    result = FactorEngine().evaluate("seg_mean(close, 2)", df)

    assert result["result"].to_list() == [2.0, 2.0, 12.0, 12.0]


def test_engine_evaluate_segmented_family():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [1.0, None, 10.0, 14.0],
            "open": [0.0, 1.0, 8.0, 13.0],
        }
    )

    sum_result = FactorEngine().evaluate("seg_sum(open, 2)", df)
    count_result = FactorEngine().evaluate("seg_count(close > open, 2)", df)
    any_result = FactorEngine().evaluate("seg_any(close > open, 2)", df)
    all_result = FactorEngine().evaluate("seg_all(close > open, 2)", df)

    assert sum_result["result"].to_list() == [1.0, 1.0, 21.0, 21.0]
    assert count_result["result"].to_list() == [1, 1, 2, 2]
    assert any_result["result"].to_list() == [True, True, True, True]
    assert all_result["result"].to_list() == [False, False, True, True]


def test_engine_evaluate_seglen_family():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [1.0, None, 10.0, 14.0],
            "open": [0.0, 1.0, 8.0, 13.0],
        }
    )

    sum_result = FactorEngine().evaluate("seglen_sum(open, [3, 5])", df)
    count_result = FactorEngine().evaluate("seglen_count(close > open, [3, 5])", df)
    any_result = FactorEngine().evaluate("seglen_any(close > open, [3, 5])", df)
    all_result = FactorEngine().evaluate("seglen_all(close > open, [3, 5])", df)

    assert sum_result["result"].to_list() == [9.0, 9.0, 9.0, 13.0]
    assert count_result["result"].to_list() == [2, 2, 2, 1]
    assert any_result["result"].to_list() == [True, True, True, True]
    assert all_result["result"].to_list() == [False, False, False, True]


def test_engine_evaluate_seglen_mean():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [1.0, 3.0, 10.0, 14.0],
        }
    )

    result = FactorEngine().evaluate("seglen_mean(close, [3, 5])", df)

    assert result["result"].to_list() == [14.0 / 3.0, 14.0 / 3.0, 14.0 / 3.0, 14.0]


def test_engine_evaluate_many_with_segmented_expression():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [1.0, 3.0, 10.0, 14.0],
            "open": [0.0, 1.0, 8.0, 13.0],
        }
    )

    result = FactorEngine().evaluate_many(
        [
            ("seg", "seg_mean(close, 2)"),
            ("delta_1", "delta(close, 1)"),
        ],
        df,
    )

    assert result["seg"].to_list() == [2.0, 2.0, 12.0, 12.0]
    assert result["delta_1"].to_list() == [None, 2.0, 7.0, 4.0]


def test_engine_evaluate_many_reuses_segmented_view_for_same_length_spec_family(monkeypatch):
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [1.0, 3.0, 10.0, 14.0],
            "open": [0.0, 1.0, 8.0, 13.0],
        }
    )
    calls: list[tuple[str, int | tuple[int, ...]]] = []
    original = Executor._prepare_segmented_sorted_df

    def counting_prepare(self, sorted_df, *, segment_spec_key):
        calls.append(segment_spec_key)
        return original(self, sorted_df, segment_spec_key=segment_spec_key)

    monkeypatch.setattr(Executor, "_prepare_segmented_sorted_df", counting_prepare)

    result = FactorEngine().evaluate_many(
        [
            ("seg_close", "seglen_mean(close, [3, 5])"),
            ("seg_open_sum", "seglen_sum(open, [3, 5])"),
            ("seg_up_any", "seglen_any(close > open, [3, 5])"),
        ],
        df,
    )

    assert result["seg_close"].to_list() == [14.0 / 3.0, 14.0 / 3.0, 14.0 / 3.0, 14.0]
    assert result["seg_open_sum"].to_list() == [9.0, 9.0, 9.0, 13.0]
    assert result["seg_up_any"].to_list() == [True, True, True, True]
    assert calls == [("length", (3, 5))]


def test_engine_evaluate_many_with_ts_median_and_other_ts_functions():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [5.0, 1.0, 7.0, 3.0],
        }
    )

    result = FactorEngine().evaluate_many(
        [
            ("med_3", "ts_median(close, 3)"),
            ("mean_2", "ts_mean(close, 2)"),
        ],
        df,
    )

    assert result["med_3"].to_list() == [5.0, 3.0, 5.0, 3.0]
    assert result["mean_2"].to_list() == [5.0, 3.0, 4.0, 5.0]


def test_engine_argpos_helpers_can_participate_in_larger_expression():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [5.0, 1.0, 7.0, 3.0],
        }
    )

    result = FactorEngine().evaluate("argmax(close, 3) + 1", df)
    assert result["result"].to_list() == [1.0, 2.0, 1.0, 2.0]


def test_engine_evaluate_many_reuses_segmented_view_for_same_segment_count(monkeypatch):
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [1.0, 3.0, 10.0, 14.0],
            "open": [0.0, 1.0, 8.0, 13.0],
        }
    )
    calls: list[tuple[str, int | tuple[int, ...]]] = []
    original = Executor._prepare_segmented_sorted_df

    def counting_prepare(self, sorted_df, *, segment_spec_key):
        calls.append(segment_spec_key)
        return original(self, sorted_df, segment_spec_key=segment_spec_key)

    monkeypatch.setattr(Executor, "_prepare_segmented_sorted_df", counting_prepare)

    result = FactorEngine().evaluate_many(
        [
            ("seg_close", "seg_mean(close, 2)"),
            ("seg_open", "seg_mean(open, 2)"),
            ("seg_spread", "seg_mean(close - open, 2)"),
            ("seg_up", "seg_count(close > open, 2)"),
        ],
        df,
    )

    assert result["seg_close"].to_list() == [2.0, 2.0, 12.0, 12.0]
    assert result["seg_open"].to_list() == [0.5, 0.5, 10.5, 10.5]
    assert result["seg_spread"].to_list() == [1.5, 1.5, 1.5, 1.5]
    assert result["seg_up"].to_list() == [2, 2, 2, 2]
    assert calls == [("equal", 2)]


def test_engine_evaluate_many_keeps_segmented_views_isolated_by_segment_count(monkeypatch):
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4, 5],
            "code": ["A", "A", "A", "A", "A"],
            "close": [1.0, 3.0, 10.0, 14.0, 20.0],
        }
    )
    calls: list[tuple[str, int | tuple[int, ...]]] = []
    original = Executor._prepare_segmented_sorted_df

    def counting_prepare(self, sorted_df, *, segment_spec_key):
        calls.append(segment_spec_key)
        return original(self, sorted_df, segment_spec_key=segment_spec_key)

    monkeypatch.setattr(Executor, "_prepare_segmented_sorted_df", counting_prepare)

    result = FactorEngine().evaluate_many(
        [
            ("seg3", "seg_mean(close, 3)"),
            ("seg5", "seg_mean(close, 5)"),
        ],
        df,
    )

    assert result["seg3"].to_list() == [2.0, 2.0, 12.0, 12.0, 20.0]
    assert result["seg5"].to_list() == [1.0, 3.0, 10.0, 14.0, 20.0]
    assert sorted(calls) == [("equal", 3), ("equal", 5)]


def test_engine_evaluate_many_reuses_segmented_view_for_same_length_spec(monkeypatch):
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [1.0, 3.0, 10.0, 14.0],
            "open": [0.0, 1.0, 8.0, 13.0],
        }
    )
    calls: list[tuple[str, int | tuple[int, ...]]] = []
    original = Executor._prepare_segmented_sorted_df

    def counting_prepare(self, sorted_df, *, segment_spec_key):
        calls.append(segment_spec_key)
        return original(self, sorted_df, segment_spec_key=segment_spec_key)

    monkeypatch.setattr(Executor, "_prepare_segmented_sorted_df", counting_prepare)

    result = FactorEngine().evaluate_many(
        [
            ("seg_close", "seglen_mean(close, [3, 5])"),
            ("seg_open", "seglen_mean(open, [3, 5])"),
        ],
        df,
    )

    assert result["seg_close"].to_list() == [14.0 / 3.0, 14.0 / 3.0, 14.0 / 3.0, 14.0]
    assert result["seg_open"].to_list() == [3.0, 3.0, 3.0, 13.0]
    assert calls == [("length", (3, 5))]


def test_engine_evaluate_many_keeps_count_and_length_specs_isolated(monkeypatch):
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [1.0, 3.0, 10.0, 14.0],
        }
    )
    calls: list[tuple[str, int | tuple[int, ...]]] = []
    original = Executor._prepare_segmented_sorted_df

    def counting_prepare(self, sorted_df, *, segment_spec_key):
        calls.append(segment_spec_key)
        return original(self, sorted_df, segment_spec_key=segment_spec_key)

    monkeypatch.setattr(Executor, "_prepare_segmented_sorted_df", counting_prepare)

    result = FactorEngine().evaluate_many(
        [
            ("seg_count", "seg_mean(close, 2)"),
            ("seg_length", "seglen_mean(close, [3, 5])"),
        ],
        df,
    )

    assert result["seg_count"].to_list() == [2.0, 2.0, 12.0, 12.0]
    assert result["seg_length"].to_list() == [14.0 / 3.0, 14.0 / 3.0, 14.0 / 3.0, 14.0]
    assert sorted(calls) == [("equal", 2), ("length", (3, 5))]


def test_engine_grouped_cross_sectional_functions():
    df = pl.DataFrame(
        {
            "time": [1, 1, 1, 1],
            "code": ["A", "B", "C", "D"],
            "industry": ["X", "X", "Y", None],
            "close": [10.0, 20.0, 30.0, 50.0],
            "ret_1d": [1.0, 3.0, 10.0, 50.0],
        }
    )

    demean_result = FactorEngine().evaluate("group_demean(close, industry)", df)
    zscore_result = FactorEngine().evaluate("group_zscore(ret_1d, industry)", df)
    rank_result = FactorEngine().evaluate(
        "group_rank(close, industry, ascending=false, pct=true)",
        df,
    )

    assert demean_result["result"].to_list() == [-5.0, 5.0, 0.0, 0.0]
    assert zscore_result["result"].to_list()[0] == pytest.approx(-0.70710678)
    assert zscore_result["result"].to_list()[1] == pytest.approx(0.70710678)
    assert zscore_result["result"].to_list()[2:] == [None, None]
    assert rank_result["result"].to_list() == [1.0, 0.5, 1.0, 1.0]


def test_engine_evaluate_many_with_grouped_and_normal_cross_sectional_functions():
    df = pl.DataFrame(
        {
            "time": [1, 1, 1, 1],
            "code": ["A", "B", "C", "D"],
            "industry": ["X", "X", "Y", None],
            "close": [10.0, 20.0, 30.0, 50.0],
        }
    )

    result = FactorEngine().evaluate_many(
        [
            ("grouped", "group_demean(close, industry)"),
            ("global_rank", "rank(close, pct=true)"),
        ],
        df,
    )

    assert result["grouped"].to_list() == [-5.0, 5.0, 0.0, 0.0]
    assert result["global_rank"].to_list() == [1.0, 0.75, 0.5, 0.25]


def test_engine_group_cross_section_materializes_nested_time_series_result():
    df = build_grouped_nested_window_df()
    engine = FactorEngine()

    staged_input = engine.evaluate_many([("rank", "ts_rank(close, 2)")], df)
    staged_demean = engine.evaluate("group_demean(rank, industry)", staged_input)
    staged_zscore = engine.evaluate("group_zscore(rank, industry)", staged_input)

    nested_demean = engine.evaluate("group_demean(ts_rank(close, 2), industry)", df)
    nested_zscore = engine.evaluate("group_zscore(ts_rank(close, 2), industry)", df)

    assert nested_demean["result"].to_list() == pytest.approx(staged_demean["result"].to_list())
    assert nested_zscore["result"].to_list() == pytest.approx(
        staged_zscore["result"].to_list(),
        nan_ok=True,
    )


def test_engine_group_rank_materializes_nested_time_series_result():
    df = build_grouped_nested_window_df()
    engine = FactorEngine()

    staged_input = engine.evaluate_many([("x", "ts_rank(close, 2)")], df)
    staged_rank = engine.evaluate("group_rank(x, industry)", staged_input)
    staged_rank_pct = engine.evaluate("group_rank(x, industry, pct=true)", staged_input)

    nested_rank = engine.evaluate("group_rank(ts_rank(close, 2), industry)", df)
    nested_rank_pct = engine.evaluate("group_rank(ts_rank(close, 2), industry, pct=true)", df)

    assert nested_rank["result"].to_list() == pytest.approx(staged_rank["result"].to_list())
    assert nested_rank_pct["result"].to_list() == pytest.approx(staged_rank_pct["result"].to_list())
