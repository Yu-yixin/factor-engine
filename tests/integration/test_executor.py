import polars as pl
import pytest

from factor_engine.executor import Executor
from factor_engine.lexer import Lexer
from factor_engine.parser import Parser
from factor_engine.validator import Validator


def parse_expression(text: str):
    tokens = Lexer(text).tokenize()
    return Parser(tokens).parse()


def build_nested_window_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "time": [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3],
            "code": ["A", "B", "C", "D"] * 3,
            "industry": ["X", "X", "Y", "Y"] * 3,
            "close": [10.0, 20.0, 100.0, 200.0, 11.0, 19.0, 101.0, 199.0, 12.0, 18.0, 102.0, 198.0],
        }
    )


def test_evaluate_number_literal():
    df = pl.DataFrame({"close": [10.0, 20.0]})
    expr = parse_expression("1")
    result = Executor(df).evaluate(expr)

    assert result["result"].to_list() == [1.0, 1.0]


def test_evaluate_variable_reference():
    df = pl.DataFrame({"close": [10.0, 20.0]})
    expr = parse_expression("close")
    result = Executor(df).evaluate(expr)

    assert result["result"].to_list() == [10.0, 20.0]


def test_evaluate_arithmetic_expression():
    df = pl.DataFrame(
        {
            "close": [10.0, 20.0],
            "open": [8.0, 25.0],
        }
    )
    expr = parse_expression("close - open")
    result = Executor(df).evaluate(expr)

    assert result["result"].to_list() == [2.0, -5.0]


def test_evaluate_comparison_expression():
    df = pl.DataFrame({"volume": [100.0, 0.0]})
    expr = parse_expression("volume > 0")
    result = Executor(df).evaluate(expr)

    assert result["result"].to_list() == [True, False]


def test_evaluate_logical_expression():
    df = pl.DataFrame(
        {
            "close": [2.0, 1.0, 3.0],
            "open": [1.0, 1.0, 4.0],
            "volume": [10.0, 5.0, 0.0],
        }
    )
    expr = parse_expression("close > open and volume > 0")
    result = Executor(df).evaluate(expr)

    assert result["result"].to_list() == [True, False, False]


def test_evaluate_logical_not_expression():
    df = pl.DataFrame({"close": [1.0, None]})
    expr = parse_expression("not is_null(close)")
    result = Executor(df).evaluate(expr)

    assert result["result"].to_list() == [True, False]


def test_evaluate_where_function():
    df = pl.DataFrame(
        {
            "volume": [100.0, 0.0],
            "ret_1d": [0.05, -0.02],
        }
    )
    expr = parse_expression("where(volume > 0, ret_1d, 0)")
    result = Executor(df).evaluate(expr)

    assert result["result"].to_list() == [0.05, 0.0]


def test_evaluate_is_null_and_fill_null():
    df = pl.DataFrame({"close": [1.0, None, 3.0]})

    is_null_result = Executor(df).evaluate(parse_expression("is_null(close)"))
    fill_null_result = Executor(df).evaluate(parse_expression("fill_null(close, 0)"))

    assert is_null_result["result"].to_list() == [False, True, False]
    assert fill_null_result["result"].to_list() == [1.0, 0.0, 3.0]


def test_fill_null_boolean_path_and_composed_expression():
    df = pl.DataFrame(
        {
            "flag": [True, None, False],
            "close": [1.0, None, 3.0],
            "open": [0.0, 2.0, 1.0],
        }
    )
    result = Executor(df).evaluate(
        parse_expression("where(fill_null(flag, false), fill_null(close, 0), open)")
    )

    assert result["result"].to_list() == [1.0, 2.0, 1.0]


def test_evaluate_nested_expression():
    df = pl.DataFrame(
        {
            "close": [10.0, 20.0],
            "open": [8.0, 25.0],
            "volume": [100.0, 0.0],
        }
    )
    expr = parse_expression("where(volume > 0, close - open, 0)")
    result = Executor(df).evaluate(expr)

    assert result["result"].to_list() == [2.0, 0.0]
def test_evaluate_delay():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [10.0, 20.0, 30.0],
        }
    )
    expr = parse_expression("delay(close, 1)")
    result = Executor(df).evaluate(expr)

    assert result["result"].to_list() == [None, 10.0, 20.0]


def test_evaluate_ts_mean():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [10.0, 20.0, 30.0],
        }
    )
    expr = parse_expression("ts_mean(close, 2)")
    result = Executor(df).evaluate(expr)

    values = result["result"].to_list()
    assert values[0] == 10.0
    assert values[1] == 15.0
    assert values[2] == 25.0


def test_evaluate_ts_sum():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [10.0, 20.0, 30.0],
        }
    )
    expr = parse_expression("ts_sum(close, 2)")
    result = Executor(df).evaluate(expr)

    assert result["result"].to_list() == [10.0, 30.0, 50.0]


def test_evaluate_ts_std():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [10.0, 20.0, 30.0],
        }
    )
    expr = parse_expression("ts_std(close, 2)")
    result = Executor(df).evaluate(expr)

    values = result["result"].to_list()
    assert values[0] is None
    assert values[1] is not None
    assert values[2] is not None


def test_time_series_respects_code_group():
    df = pl.DataFrame(
        {
            "time": [1, 2, 1, 2],
            "code": ["A", "A", "B", "B"],
            "close": [10.0, 20.0, 100.0, 200.0],
        }
    )
    expr = parse_expression("delay(close, 1)")
    result = Executor(df).evaluate(expr)

    assert result["result"].to_list() == [None, 10.0, None, 100.0]


def test_delay_does_not_look_ahead():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [10.0, 999.0, 30.0],
        }
    )
    expr = parse_expression("delay(close, 1)")
    result = Executor(df).evaluate(expr)

    assert result["result"].to_list() == [None, 10.0, 999.0]

def test_evaluate_demean():
    df = pl.DataFrame(
        {
            "time": [1, 1, 2, 2],
            "code": ["A", "B", "A", "B"],
            "close": [10.0, 30.0, 20.0, 40.0],
        }
    )
    expr = parse_expression("demean(close)")
    result = Executor(df).evaluate(expr)

    assert result["result"].to_list() == [-10.0, 10.0, -10.0, 10.0]


def test_evaluate_zscore():
    df = pl.DataFrame(
        {
            "time": [1, 1],
            "code": ["A", "B"],
            "close": [10.0, 30.0],
        }
    )
    expr = parse_expression("zscore(close)")
    result = Executor(df).evaluate(expr)

    values = result["result"].to_list()
    assert values[0] is not None
    assert values[1] is not None
    assert round(values[0], 6) == -0.707107
    assert round(values[1], 6) == 0.707107


def test_evaluate_demean_materializes_nested_time_series_result():
    df = build_nested_window_df()
    executor = Executor(df)
    nested = executor.evaluate(parse_expression("demean(ts_rank(close, 2))"))

    staged_input = executor.evaluate(parse_expression("ts_rank(close, 2)")).rename({"result": "rank"})
    staged = Executor(staged_input).evaluate(parse_expression("demean(rank)"))

    assert nested["result"].to_list() == pytest.approx(staged["result"].to_list(), nan_ok=True)


def test_evaluate_zscore_materializes_nested_time_series_result():
    df = build_nested_window_df()
    executor = Executor(df)
    nested = executor.evaluate(parse_expression("zscore(ts_rank(close, 2))"))

    staged_input = executor.evaluate(parse_expression("ts_rank(close, 2)")).rename({"result": "rank"})
    staged = Executor(staged_input).evaluate(parse_expression("zscore(rank)"))

    assert nested["result"].to_list() == pytest.approx(staged["result"].to_list(), nan_ok=True)


def test_group_cross_section_materializes_nested_time_series_result():
    df = build_nested_window_df()
    executor = Executor(df)

    nested_demean = executor.evaluate(parse_expression("group_demean(ts_rank(close, 2), industry)"))
    nested_zscore = executor.evaluate(parse_expression("group_zscore(ts_rank(close, 2), industry)"))

    staged_input = executor.evaluate(parse_expression("ts_rank(close, 2)")).rename({"result": "rank"})
    staged_demean = Executor(staged_input).evaluate(parse_expression("group_demean(rank, industry)"))
    staged_zscore = Executor(staged_input).evaluate(parse_expression("group_zscore(rank, industry)"))

    assert nested_demean["result"].to_list() == pytest.approx(staged_demean["result"].to_list())
    assert nested_zscore["result"].to_list() == pytest.approx(
        staged_zscore["result"].to_list(),
        nan_ok=True,
    )


def test_rank_materializes_nested_time_series_result():
    df = build_nested_window_df()
    executor = Executor(df)

    nested_rank = executor.evaluate(parse_expression("rank(ts_rank(close, 2))"))
    nested_rank_pct = executor.evaluate(parse_expression("rank(ts_rank(close, 2), pct=true)"))

    staged_input = executor.evaluate(parse_expression("ts_rank(close, 2)")).rename({"result": "x"})
    staged_rank = Executor(staged_input).evaluate(parse_expression("rank(x)"))
    staged_rank_pct = Executor(staged_input).evaluate(parse_expression("rank(x, pct=true)"))

    assert nested_rank["result"].to_list() == pytest.approx(staged_rank["result"].to_list())
    assert nested_rank_pct["result"].to_list() == pytest.approx(staged_rank_pct["result"].to_list())


def test_group_rank_materializes_nested_time_series_result():
    df = build_nested_window_df()
    executor = Executor(df)

    nested_rank = executor.evaluate(parse_expression("group_rank(ts_rank(close, 2), industry)"))
    nested_rank_pct = executor.evaluate(
        parse_expression("group_rank(ts_rank(close, 2), industry, pct=true)")
    )

    staged_input = executor.evaluate(parse_expression("ts_rank(close, 2)")).rename({"result": "x"})
    staged_rank = Executor(staged_input).evaluate(parse_expression("group_rank(x, industry)"))
    staged_rank_pct = Executor(staged_input).evaluate(
        parse_expression("group_rank(x, industry, pct=true)")
    )

    assert nested_rank["result"].to_list() == pytest.approx(staged_rank["result"].to_list())
    assert nested_rank_pct["result"].to_list() == pytest.approx(staged_rank_pct["result"].to_list())


def test_evaluate_rank_default_desc():
    df = pl.DataFrame(
        {
            "time": [1, 1, 1],
            "code": ["A", "B", "C"],
            "close": [10.0, 30.0, 20.0],
        }
    )
    expr = parse_expression("rank(close)")
    result = Executor(df).evaluate(expr)

    assert result["result"].to_list() == [3.0, 1.0, 2.0]


def test_evaluate_rank_pct():
    df = pl.DataFrame(
        {
            "time": [1, 1, 1],
            "code": ["A", "B", "C"],
            "close": [10.0, 30.0, 20.0],
        }
    )
    expr = parse_expression("rank(close, pct=true)")
    result = Executor(df).evaluate(expr)

    assert result["result"].to_list() == [1.0, 1 / 3, 2 / 3]


def test_evaluate_rank_ascending():
    df = pl.DataFrame(
        {
            "time": [1, 1, 1],
            "code": ["A", "B", "C"],
            "close": [10.0, 30.0, 20.0],
        }
    )
    expr = parse_expression("rank(close, ascending=true)")
    result = Executor(df).evaluate(expr)

    assert result["result"].to_list() == [1.0, 3.0, 2.0]


def test_pointwise_expression_uses_no_time_order_path(monkeypatch: pytest.MonkeyPatch):
    df = pl.DataFrame(
        {
            "time": [2, 1],
            "code": ["A", "A"],
            "close": [20.0, 10.0],
        }
    )
    expr = parse_expression("close")
    validation = Validator(schema=df.schema).validate(expr)
    executor = Executor(df)
    calls: list[str] = []

    def track_no_time_order(compiled, *, output_name):
        calls.append("no_time_order")
        return df.with_columns(compiled.alias(output_name))

    def fail_time_ordered(compiled, *, output_name):
        raise AssertionError("time-ordered path should not be used")

    monkeypatch.setattr(executor, "_evaluate_row_aligned_no_time_order", track_no_time_order)
    monkeypatch.setattr(executor, "_evaluate_row_aligned_time_ordered", fail_time_ordered)

    result = executor.evaluate(expr, validation=validation)

    assert calls == ["no_time_order"]
    assert result["result"].to_list() == [20.0, 10.0]


def test_time_series_expression_uses_time_ordered_path(monkeypatch: pytest.MonkeyPatch):
    df = pl.DataFrame(
        {
            "time": [2, 1],
            "code": ["A", "A"],
            "close": [20.0, 10.0],
        }
    )
    expr = parse_expression("delay(close, 1)")
    validation = Validator(schema=df.schema).validate(expr)
    executor = Executor(df)
    calls: list[str] = []

    def fail_no_time_order(compiled, *, output_name):
        raise AssertionError("no-time-order path should not be used")

    def track_time_ordered(compiled, *, output_name):
        calls.append("time_ordered")
        return Executor(df)._evaluate_row_aligned_time_ordered(compiled, output_name=output_name)

    monkeypatch.setattr(executor, "_evaluate_row_aligned_no_time_order", fail_no_time_order)
    monkeypatch.setattr(executor, "_evaluate_row_aligned_time_ordered", track_time_ordered)

    result = executor.evaluate(expr, validation=validation)

    assert calls == ["time_ordered"]
    assert result["result"].to_list() == [10.0, None]
