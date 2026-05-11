import pytest
import polars as pl

from factor_engine.errors import (
    ArgumentError,
    UnknownFunctionError,
    UnknownVariableError,
)
from factor_engine.lexer import Lexer
from factor_engine.parser import Parser
from factor_engine.validator import Validator


def parse_expression(text: str):
    tokens = Lexer(text).tokenize()
    return Parser(tokens).parse()


def validate_expression(text: str, variables: set[str]) -> None:
    expr = parse_expression(text)
    Validator(variables).validate(expr)


def validate_dataframe_expression(
    text: str,
    df: pl.DataFrame,
    *,
    time_col: str = "time",
    code_col: str = "code",
) -> None:
    expr = parse_expression(text)
    Validator(schema=df.schema, time_col=time_col, code_col=code_col).validate(expr)


def test_validate_simple_variable_expression():
    validate_expression("close + open", {"close", "open"})


def test_validate_time_series_function():
    validate_expression("ts_mean(close, 5)", {"close", "time", "code"})


def test_validate_rank_with_kwargs():
    validate_expression(
        "rank(close, ascending=false, pct=true)",
        {"close", "time"},
    )


def test_unknown_variable_raises():
    with pytest.raises(UnknownVariableError, match="foo"):
        validate_expression("foo + close", {"close"})


def test_unknown_function_raises():
    with pytest.raises(UnknownFunctionError, match="unknown_func"):
        validate_expression("unknown_func(close)", {"close"})


def test_wrong_argument_count_raises():
    with pytest.raises(ArgumentError, match="ts_mean"):
        validate_expression("ts_mean(close)", {"close"})


def test_unsupported_keyword_argument_raises():
    with pytest.raises(ArgumentError, match="method"):
        validate_expression("rank(close, method=true)", {"close"})


def test_where_requires_three_args():
    with pytest.raises(ArgumentError, match="where"):
        validate_expression("where(close > 0, close)", {"close"})


def test_validate_logical_expression():
    validate_expression(
        "close > open and volume > 0",
        {"close", "open", "volume"},
    )


def test_logical_and_requires_boolean_operands():
    df = pl.DataFrame({"close": [1.0], "open": [2.0]})

    with pytest.raises(ArgumentError, match="boolean input"):
        validate_dataframe_expression("close and open", df)


def test_logical_not_requires_boolean_operand():
    df = pl.DataFrame({"close": [1.0]})

    with pytest.raises(ArgumentError, match="boolean input"):
        validate_dataframe_expression("not close", df)


def test_is_null_requires_one_argument():
    with pytest.raises(ArgumentError, match="is_null"):
        validate_expression("is_null(close, open)", {"close", "open"})


def test_fill_null_requires_two_arguments():
    with pytest.raises(ArgumentError, match="fill_null"):
        validate_expression("fill_null(close)", {"close"})


def test_fill_null_rejects_mixed_numeric_and_boolean_types():
    df = pl.DataFrame(
        {
            "close": [1.0, None],
            "flag": [True, False],
        }
    )

    with pytest.raises(ArgumentError, match="share the same type"):
        validate_dataframe_expression("fill_null(close, flag)", df)


def test_validate_fft_root_expression():
    df = pl.DataFrame(
        {
            "time": [1, 2],
            "code": ["A", "A"],
            "close": [1.0, 2.0],
        }
    )

    validate_dataframe_expression("fft(close)", df)


def test_fft_must_be_root_expression():
    df = pl.DataFrame(
        {
            "time": [1, 2],
            "code": ["A", "A"],
            "close": [1.0, 2.0],
        }
    )

    with pytest.raises(ArgumentError, match="root expression"):
        validate_dataframe_expression("rank(fft(close))", df)


def test_fft_requires_direct_column_reference():
    df = pl.DataFrame(
        {
            "time": [1, 2],
            "code": ["A", "A"],
            "close": [1.0, 2.0],
            "open": [0.5, 1.5],
        }
    )

    with pytest.raises(ArgumentError, match="direct column reference"):
        validate_dataframe_expression("fft(close - open)", df)


def test_fft_requires_numeric_input_column():
    df = pl.DataFrame(
        {
            "time": [1, 2],
            "code": ["A", "A"],
            "label": ["x", "y"],
        }
    )

    with pytest.raises(ArgumentError, match="numeric input column"):
        validate_dataframe_expression("fft(label)", df)


def test_fft_requires_time_and_code_columns():
    df = pl.DataFrame({"close": [1.0, 2.0]})

    with pytest.raises(ArgumentError, match="time column"):
        validate_dataframe_expression("fft(close)", df)
