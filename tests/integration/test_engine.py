import polars as pl
import pytest

from factor_engine.executor import Executor
from factor_engine.errors import ArgumentError
from factor_engine.engine import FactorEngine
from factor_engine.lexer import Lexer
from factor_engine.validator import Validator


def build_nested_window_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "time": [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3],
            "code": ["A", "B", "C", "D"] * 3,
            "industry": ["X", "X", "Y", "Y"] * 3,
            "close": [10.0, 20.0, 100.0, 200.0, 11.0, 19.0, 101.0, 199.0, 12.0, 18.0, 102.0, 198.0],
        }
    )


def assert_optional_float_lists_close(actual: list[object], expected: list[object]) -> None:
    assert len(actual) == len(expected)
    for observed, target in zip(actual, expected, strict=True):
        if observed is None or target is None:
            assert observed is None and target is None
            continue
        if isinstance(observed, float) and isinstance(target, float):
            if observed != observed or target != target:
                assert observed != observed and target != target
                continue
        assert observed == pytest.approx(target)


def test_engine_evaluate_delay():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [10.0, 20.0, 30.0],
        }
    )

    engine = FactorEngine()
    result = engine.evaluate("delay(close, 1)", df)

    assert result["result"].to_list() == [None, 10.0, 20.0]


def test_engine_evaluate_rank():
    df = pl.DataFrame(
        {
            "time": [1, 1, 1],
            "code": ["A", "B", "C"],
            "close": [10.0, 30.0, 20.0],
        }
    )

    engine = FactorEngine()
    result = engine.evaluate("rank(close, pct=true)", df)

    assert result["result"].to_list() == [1.0, 1 / 3, 2 / 3]


def test_engine_evaluate_many_with_logical_and_null_functions():
    df = pl.DataFrame(
        {
            "close": [1.0, None, 3.0],
            "open": [0.0, 2.0, 1.0],
            "flag": [True, None, False],
        }
    )

    result = FactorEngine().evaluate_many(
        [
            ("missing_close", "is_null(close)"),
            ("safe_flag", "fill_null(flag, false)"),
            ("usable", "not is_null(close) and fill_null(flag, false)"),
        ],
        df,
    )

    assert result["missing_close"].to_list() == [False, True, False]
    assert result["safe_flag"].to_list() == [True, False, False]
    assert result["usable"].to_list() == [True, False, False]


def test_engine_evaluate_many_returns_original_frame_plus_result_columns():
    df = pl.DataFrame(
        {
            "time": [2, 1, 1],
            "code": ["A", "A", "B"],
            "close": [20.0, 10.0, 100.0],
            "open": [18.0, 9.0, 90.0],
        }
    )

    engine = FactorEngine()
    result = engine.evaluate_many(
        [
            ("lagged", "delay(close, 1)"),
            ("spread", "close - open"),
            ("demeaned", "demean(close)"),
        ],
        df,
    )

    assert result.columns == ["time", "code", "close", "open", "lagged", "spread", "demeaned"]
    assert result["spread"].to_list() == [2.0, 1.0, 10.0]
    assert result["lagged"].to_list() == [10.0, None, None]


def test_engine_evaluate_many_supports_positional_ordered_route():
    df = pl.DataFrame(
        {
            "time": [2, 1, 3, 2, 1, 3],
            "code": ["A", "A", "A", "B", "B", "B"],
            "close": [1.0, 5.0, 3.0, 20.0, 10.0, 30.0],
        }
    )

    result = FactorEngine().evaluate_many([("argmaxed", "argmax(close, 2)")], df)

    assert result["argmaxed"].to_list() == [1, 0, 0, 0, 0, 0]


def test_engine_evaluate_many_rejects_duplicate_output_names():
    df = pl.DataFrame({"close": [1.0]})

    with pytest.raises(ArgumentError, match="Duplicate output column name"):
        FactorEngine().evaluate_many([("x", "close"), ("x", "close + 1")], df)


def test_engine_evaluate_many_rejects_table_expressions():
    df = pl.DataFrame(
        {
            "time": [1, 2],
            "code": ["A", "A"],
            "close": [1.0, 2.0],
        }
    )

    with pytest.raises(ArgumentError, match="only supports column expressions"):
        FactorEngine().evaluate_many([("spec", "fft(close)")], df)


def test_engine_reuses_cached_parse_validate_and_compile(
    monkeypatch: pytest.MonkeyPatch,
):
    df = pl.DataFrame(
        {
            "time": [1, 2],
            "code": ["A", "A"],
            "close": [10.0, 20.0],
            "open": [8.0, 18.0],
        }
    )
    counts = {"tokenize": 0, "validate": 0, "compile": 0}

    original_tokenize = Lexer.tokenize
    original_validate = Validator.validate
    original_compile = Executor.compile

    def track_tokenize(self):
        counts["tokenize"] += 1
        return original_tokenize(self)

    def track_validate(self, expr):
        counts["validate"] += 1
        return original_validate(self, expr)

    def track_compile(self, expr):
        counts["compile"] += 1
        return original_compile(self, expr)

    monkeypatch.setattr(Lexer, "tokenize", track_tokenize)
    monkeypatch.setattr(Validator, "validate", track_validate)
    monkeypatch.setattr(Executor, "compile", track_compile)

    engine = FactorEngine()
    first = engine.evaluate("close - open", df)
    second = engine.evaluate("close - open", df)

    assert first["result"].to_list() == [2.0, 2.0]
    assert second["result"].to_list() == [2.0, 2.0]
    assert counts == {"tokenize": 1, "validate": 1, "compile": 1}


def test_engine_evaluate_many_reuses_compiled_expression_once(
    monkeypatch: pytest.MonkeyPatch,
):
    df = pl.DataFrame(
        {
            "time": [1, 2],
            "code": ["A", "A"],
            "close": [10.0, 20.0],
            "open": [8.0, 18.0],
        }
    )
    counts = {"compile": 0}
    original_compile = Executor.compile

    def track_compile(self, expr):
        counts["compile"] += 1
        return original_compile(self, expr)

    monkeypatch.setattr(Executor, "compile", track_compile)

    result = FactorEngine().evaluate_many(
        [
            ("spread_a", "close - open"),
            ("spread_b", "close - open"),
        ],
        df,
    )

    assert result["spread_a"].to_list() == [2.0, 2.0]
    assert result["spread_b"].to_list() == [2.0, 2.0]
    assert counts["compile"] == 1


def test_engine_cache_is_invalidated_by_schema_changes(
    monkeypatch: pytest.MonkeyPatch,
):
    base_df = pl.DataFrame(
        {
            "time": [1, 2],
            "code": ["A", "A"],
            "close": [10.0, 20.0],
            "open": [8.0, 18.0],
        }
    )
    widened_df = base_df.with_columns(pl.lit(1.0).alias("volume"))
    counts = {"tokenize": 0, "validate": 0, "compile": 0}

    original_tokenize = Lexer.tokenize
    original_validate = Validator.validate
    original_compile = Executor.compile

    def track_tokenize(self):
        counts["tokenize"] += 1
        return original_tokenize(self)

    def track_validate(self, expr):
        counts["validate"] += 1
        return original_validate(self, expr)

    def track_compile(self, expr):
        counts["compile"] += 1
        return original_compile(self, expr)

    monkeypatch.setattr(Lexer, "tokenize", track_tokenize)
    monkeypatch.setattr(Validator, "validate", track_validate)
    monkeypatch.setattr(Executor, "compile", track_compile)

    engine = FactorEngine()
    engine.evaluate("close - open", base_df)
    engine.evaluate("close - open", widened_df)

    assert counts == {"tokenize": 1, "validate": 2, "compile": 2}


def test_engine_cache_preserves_validation_errors(
    monkeypatch: pytest.MonkeyPatch,
):
    df = pl.DataFrame(
        {
            "time": [1, 2],
            "code": ["A", "A"],
            "label": ["x", "y"],
        }
    )
    counts = {"validate": 0}
    original_validate = Validator.validate

    def track_validate(self, expr):
        counts["validate"] += 1
        return original_validate(self, expr)

    monkeypatch.setattr(Validator, "validate", track_validate)

    engine = FactorEngine()

    with pytest.raises(ArgumentError, match="numeric input column"):
        engine.evaluate("ts_rank(label, 2)", df)

    with pytest.raises(ArgumentError, match="numeric input column"):
        engine.evaluate("ts_rank(label, 2)", df)

    assert counts["validate"] == 2


def test_engine_evaluate_materializes_nested_time_series_for_demean_and_zscore():
    df = build_nested_window_df()
    engine = FactorEngine()

    staged_input = engine.evaluate_many([("rank", "ts_rank(close, 2)")], df)
    staged_demean = engine.evaluate("demean(rank)", staged_input)
    staged_zscore = engine.evaluate("zscore(rank)", staged_input)

    nested_demean = engine.evaluate("demean(ts_rank(close, 2))", df)
    nested_zscore = engine.evaluate("zscore(ts_rank(close, 2))", df)

    assert nested_demean["result"].to_list() == pytest.approx(staged_demean["result"].to_list())
    assert nested_zscore["result"].to_list() == pytest.approx(
        staged_zscore["result"].to_list(),
        nan_ok=True,
    )


def test_engine_evaluate_many_supports_staged_nested_time_series_expression():
    df = build_nested_window_df()
    engine = FactorEngine()

    result = engine.evaluate_many(
        [
            ("nested_demean", "demean(ts_rank(close, 2))"),
            ("lagged_close", "delay(close, 1)"),
        ],
        df,
    )

    staged = engine.evaluate(
        "demean(rank)",
        engine.evaluate_many([("rank", "ts_rank(close, 2)")], df),
    )

    assert result["nested_demean"].to_list() == pytest.approx(staged["result"].to_list())
    assert result["lagged_close"].to_list() == [None, None, None, None, 10.0, 20.0, 100.0, 200.0, 11.0, 19.0, 101.0, 199.0]


def test_engine_evaluate_materializes_nested_time_series_for_rank():
    df = build_nested_window_df()
    engine = FactorEngine()

    staged_input = engine.evaluate_many([("x", "ts_rank(close, 2)")], df)
    staged_rank = engine.evaluate("rank(x)", staged_input)
    staged_rank_pct = engine.evaluate("rank(x, pct=true)", staged_input)

    nested_rank = engine.evaluate("rank(ts_rank(close, 2))", df)
    nested_rank_pct = engine.evaluate("rank(ts_rank(close, 2), pct=true)", df)

    assert nested_rank["result"].to_list() == pytest.approx(staged_rank["result"].to_list())
    assert nested_rank_pct["result"].to_list() == pytest.approx(staged_rank_pct["result"].to_list())


def test_engine_evaluate_deep_staged_chain_matches_manual_steps():
    df = build_nested_window_df()
    engine = FactorEngine()

    manual = engine.evaluate_many([("x", "ts_mean(close, 2)")], df)
    manual = engine.evaluate("demean(x)", manual, output_name="y")
    manual = engine.evaluate("rank(y, pct=true)", manual)

    nested = engine.evaluate("rank(demean(ts_mean(close, 2)), pct=true)", df)

    assert nested["result"].to_list() == pytest.approx(manual["result"].to_list())


def test_engine_evaluate_many_supports_deep_staged_chain_expression():
    df = build_nested_window_df()
    engine = FactorEngine()

    result = engine.evaluate_many(
        [
            ("deep_rank", "rank(demean(ts_mean(close, 2)), pct=true)"),
            ("lagged_close", "delay(close, 1)"),
        ],
        df,
    )

    manual = engine.evaluate_many([("x", "ts_mean(close, 2)")], df)
    manual = engine.evaluate("demean(x)", manual, output_name="y")
    manual = engine.evaluate("rank(y, pct=true)", manual)

    assert result["deep_rank"].to_list() == pytest.approx(manual["result"].to_list())
    assert result["lagged_close"].to_list() == [None, None, None, None, 10.0, 20.0, 100.0, 200.0, 11.0, 19.0, 101.0, 199.0]


def test_engine_evaluate_many_fuses_ordered_compiled_and_staged_paths(
    monkeypatch: pytest.MonkeyPatch,
):
    df = build_nested_window_df()
    engine = FactorEngine()
    manual = engine.evaluate_many([("x", "ts_mean(close, 2)")], df)
    manual = engine.evaluate("demean(x)", manual, output_name="y")
    manual_rank = engine.evaluate("rank(y, pct=true)", manual)
    manual_lagged = engine.evaluate("delay(close, 1)", df)

    counts = {"prepared": 0}
    original_get_prepared_frame = Executor._get_prepared_frame

    def track_get_prepared_frame(self):
        counts["prepared"] += 1
        return original_get_prepared_frame(self)

    monkeypatch.setattr(Executor, "_get_prepared_frame", track_get_prepared_frame)

    result = engine.evaluate_many(
        [
            ("lagged_close", "delay(close, 1)"),
            ("deep_rank", "rank(demean(ts_mean(close, 2)), pct=true)"),
        ],
        df,
    )

    assert result["deep_rank"].to_list() == pytest.approx(manual_rank["result"].to_list())
    assert result["lagged_close"].to_list() == manual_lagged["result"].to_list()
    assert counts["prepared"] == 1


def test_engine_evaluate_many_reuses_staged_source_and_prefix(monkeypatch: pytest.MonkeyPatch):
    df = build_nested_window_df()
    engine = FactorEngine()

    manual = engine.evaluate_many([("x", "ts_mean(close, 2)")], df)
    manual = engine.evaluate("demean(x)", manual, output_name="y")
    manual_rank = engine.evaluate("rank(y, pct=true)", manual)
    manual_zscore = engine.evaluate("zscore(y)", manual)

    source_expr = engine.parse("ts_mean(close, 2)")
    counts = {"source_compile": 0, "demean_step": 0}
    original_compile_expr = Executor._compile_expr
    original_build_staged_expr = Executor._build_staged_cross_section_expr

    def track_compile_expr(self, expr):
        if expr == source_expr:
            counts["source_compile"] += 1
        return original_compile_expr(self, expr)

    def track_build_staged_expr(self, staged_spec, *, stage_name):
        if staged_spec.func_name == "demean":
            counts["demean_step"] += 1
        return original_build_staged_expr(self, staged_spec, stage_name=stage_name)

    monkeypatch.setattr(Executor, "_compile_expr", track_compile_expr)
    monkeypatch.setattr(Executor, "_build_staged_cross_section_expr", track_build_staged_expr)

    result = engine.evaluate_many(
        [
            ("ranked", "rank(demean(ts_mean(close, 2)), pct=true)"),
            ("scored", "zscore(demean(ts_mean(close, 2)))"),
        ],
        df,
    )

    assert result["ranked"].to_list() == pytest.approx(manual_rank["result"].to_list())
    assert result["scored"].to_list() == pytest.approx(
        manual_zscore["result"].to_list(),
        nan_ok=True,
    )
    assert counts["source_compile"] == 1
    assert counts["demean_step"] == 1


def test_engine_evaluate_many_fuses_ordered_compiled_and_materialized_ordered_paths(
    monkeypatch: pytest.MonkeyPatch,
):
    df = build_nested_window_df()
    engine = FactorEngine()

    manual = engine.evaluate_many(
        [
            ("rank_close", "rank(close)"),
            ("rank_shifted", "rank(close + 1)"),
        ],
        df,
    )
    manual_corr = engine.evaluate("corr(rank_close, rank_shifted, 3)", manual)
    manual_lagged = engine.evaluate("delay(close, 1)", df)

    counts = {"prepared": 0}
    original_get_prepared_frame = Executor._get_prepared_frame

    def track_get_prepared_frame(self):
        counts["prepared"] += 1
        return original_get_prepared_frame(self)

    monkeypatch.setattr(Executor, "_get_prepared_frame", track_get_prepared_frame)

    result = engine.evaluate_many(
        [
            ("lagged_close", "delay(close, 1)"),
            ("corr_ranked", "corr(rank(close), rank(close + 1), 3)"),
        ],
        df,
    )

    assert result["lagged_close"].to_list() == manual_lagged["result"].to_list()
    assert_optional_float_lists_close(
        result["corr_ranked"].to_list(),
        manual_corr["result"].to_list(),
    )
    assert counts["prepared"] == 1


def test_engine_evaluate_many_supports_single_input_materialized_ordered_family(
    monkeypatch: pytest.MonkeyPatch,
):
    df = build_nested_window_df()
    engine = FactorEngine()

    staged_input = engine.evaluate("rank(close)", df, output_name="rank_col")
    manual_mean = engine.evaluate("ts_mean(rank_col, 2)", staged_input)
    manual_lagged = engine.evaluate("delay(close, 1)", df)

    counts = {"prepared": 0}
    original_get_prepared_frame = Executor._get_prepared_frame

    def track_get_prepared_frame(self):
        counts["prepared"] += 1
        return original_get_prepared_frame(self)

    monkeypatch.setattr(Executor, "_get_prepared_frame", track_get_prepared_frame)

    result = engine.evaluate_many(
        [
            ("lagged_close", "delay(close, 1)"),
            ("mean_ranked", "ts_mean(rank(close), 2)"),
        ],
        df,
    )

    assert result["lagged_close"].to_list() == manual_lagged["result"].to_list()
    assert_optional_float_lists_close(
        result["mean_ranked"].to_list(),
        manual_mean["result"].to_list(),
    )
    assert counts["prepared"] == 1


@pytest.mark.parametrize("root_name, window", [
    ("ts_mean", 2),
    ("ts_std", 2),
    ("ts_min", 2),
    ("ts_max", 2),
    ("ts_median", 2),
    ("ts_sum", 2),
    ("skew", 3),
    ("kurt", 4),
])
def test_engine_materializes_single_input_ordered_over_cross_family(root_name: str, window: int):
    df = build_nested_window_df()
    engine = FactorEngine()

    staged_input = engine.evaluate("rank(close)", df, output_name="rank_col")
    manual = engine.evaluate(f"{root_name}(rank_col, {window})", staged_input)
    nested = engine.evaluate(f"{root_name}(rank(close), {window})", df)

    assert_optional_float_lists_close(
        nested["result"].to_list(),
        manual["result"].to_list(),
    )


@pytest.mark.parametrize("expr_text", [
    "ts_min(rank(close), 2)",
    "ts_max(rank(close), 2)",
    "ts_median(rank(close), 2)",
    "ts_sum(rank(close), 2)",
    "skew(rank(close), 3)",
    "kurt(rank(close), 4)",
])
def test_engine_evaluate_many_supports_expanded_single_input_materialized_ordered_family(
    expr_text: str,
):
    df = build_nested_window_df()
    result = FactorEngine().evaluate_many([("derived", expr_text)], df)

    assert "derived" in result.columns


def test_engine_materializes_argmax_over_cross_family():
    df = build_nested_window_df()
    engine = FactorEngine()

    staged_input = engine.evaluate("rank(close)", df, output_name="rank_col")
    manual = engine.evaluate("argmax(rank_col, 2)", staged_input)
    nested = engine.evaluate("argmax(rank(close), 2)", df)

    assert_optional_float_lists_close(
        nested["result"].to_list(),
        manual["result"].to_list(),
    )
