import polars as pl
import pytest

from factor_engine.errors import ArgumentError, UnknownVariableError
from factor_engine.lexer import Lexer
from factor_engine.parser import Parser
from factor_engine.validator import Validator


def parse_expression(text: str):
    tokens = Lexer(text).tokenize()
    return Parser(tokens).parse()


def validate_with_df(text: str, df: pl.DataFrame) -> None:
    expr = parse_expression(text)
    Validator(schema=df.schema).validate(expr)


def test_validate_new_time_series_functions():
    df = pl.DataFrame(
        {
            "time": [1, 2],
            "code": ["A", "A"],
            "close": [1.0, 2.0],
            "open": [0.5, 1.5],
        }
    )

    validate_with_df("ts_min(close, 5)", df)
    validate_with_df("ts_max(close, 5)", df)
    validate_with_df("ts_median(close, 5)", df)
    validate_with_df("argmax(close, 5)", df)
    validate_with_df("argmin(close, 5)", df)
    validate_with_df("delta(close, 1)", df)
    validate_with_df("pct_change(close, 1)", df)
    validate_with_df("ts_count(close > open, 2)", df)
    validate_with_df("ts_any(close > open, 2)", df)
    validate_with_df("ts_all(close > open, 2)", df)
    validate_with_df("ts_rank(close, 2)", df)
    validate_with_df("seg_mean(close, 2)", df)
    validate_with_df("seg_sum(close, 2)", df)
    validate_with_df("seglen_mean(close, [1, 1])", df)
    validate_with_df("seglen_sum(close, [1, 1])", df)
    validate_with_df("seg_count(close > open, 2)", df)
    validate_with_df("seg_any(close > open, 2)", df)
    validate_with_df("seg_all(close > open, 2)", df)
    validate_with_df("seglen_count(close > open, [1, 1])", df)
    validate_with_df("seglen_any(close > open, [1, 1])", df)
    validate_with_df("seglen_all(close > open, [1, 1])", df)


def test_validate_new_functions_accept_numeric_expressions():
    df = pl.DataFrame(
        {
            "time": [1, 2],
            "code": ["A", "A"],
            "close": [3.0, 4.0],
            "open": [1.0, 2.0],
        }
    )

    validate_with_df("delta(close - open, 1)", df)
    validate_with_df("pct_change(close - open, 1)", df)
    validate_with_df("ts_min(close - open, 5)", df)
    validate_with_df("ts_max(close - open, 5)", df)
    validate_with_df("ts_median(close - open, 5)", df)
    validate_with_df("seg_mean(close - open, 2)", df)
    validate_with_df("seglen_mean(close - open, [1, 1])", df)
    validate_with_df("seg_sum(close - open, 2)", df)
    validate_with_df("seglen_sum(close - open, [1, 1])", df)
    validate_with_df("abs(close - open)", df)
    validate_with_df("clip(close - open, 0, 3)", df)
    validate_with_df("sign(close - open)", df)


def test_validate_new_functions_reject_non_numeric_columns():
    df = pl.DataFrame(
        {
            "time": [1, 2],
            "code": ["A", "A"],
            "label": ["x", "y"],
            "flag": [True, False],
        }
    )

    with pytest.raises(ArgumentError, match="numeric input column"):
        validate_with_df("ts_min(label, 5)", df)

    with pytest.raises(ArgumentError, match="numeric input column"):
        validate_with_df("pct_change(label, 1)", df)

    with pytest.raises(ArgumentError, match="numeric input column"):
        validate_with_df("ts_rank(flag, 2)", df)

    with pytest.raises(ArgumentError, match="numeric input column"):
        validate_with_df("ts_median(label, 2)", df)

    with pytest.raises(ArgumentError, match="numeric input column"):
        validate_with_df("argmax(flag, 2)", df)

    with pytest.raises(ArgumentError, match="numeric input column"):
        validate_with_df("argmin(label, 2)", df)

    with pytest.raises(ArgumentError, match="numeric input column"):
        validate_with_df("seg_mean(label, 2)", df)

    with pytest.raises(ArgumentError, match="numeric input column"):
        validate_with_df("seglen_mean(label, [1, 1])", df)

    with pytest.raises(ArgumentError, match="numeric input column"):
        validate_with_df("seg_sum(label, 2)", df)

    with pytest.raises(ArgumentError, match="numeric input column"):
        validate_with_df("seglen_sum(label, [1, 1])", df)

    with pytest.raises(ArgumentError, match="numeric input column"):
        validate_with_df("abs(label)", df)

    with pytest.raises(ArgumentError, match="numeric input column"):
        validate_with_df("clip(flag, 0, 1)", df)

    with pytest.raises(ArgumentError, match="numeric input column"):
        validate_with_df("sign(label)", df)


def test_validate_new_functions_reject_boolean_expressions():
    df = pl.DataFrame(
        {
            "time": [1, 2],
            "code": ["A", "A"],
            "close": [1.0, 2.0],
            "open": [0.5, 1.5],
        }
    )

    with pytest.raises(ArgumentError, match="numeric input expression"):
        validate_with_df("delta(close > open, 1)", df)

    with pytest.raises(ArgumentError, match="numeric input expression"):
        validate_with_df("ts_max(close > open, 5)", df)

    with pytest.raises(ArgumentError, match="numeric input expression"):
        validate_with_df("seg_mean(close > open, 2)", df)

    with pytest.raises(ArgumentError, match="numeric input expression"):
        validate_with_df("seg_sum(close > open, 2)", df)

    with pytest.raises(ArgumentError, match="numeric input expression"):
        validate_with_df("abs(close > open)", df)

    with pytest.raises(ArgumentError, match="numeric input expression"):
        validate_with_df("clip(close > open, 0, 1)", df)

    with pytest.raises(ArgumentError, match="numeric input expression"):
        validate_with_df("sign(close > open)", df)


def test_validate_boolean_time_series_functions_reject_numeric_inputs():
    df = pl.DataFrame(
        {
            "time": [1, 2],
            "code": ["A", "A"],
            "close": [1.0, 2.0],
        }
    )

    with pytest.raises(ArgumentError, match="boolean input column"):
        validate_with_df("ts_any(close, 2)", df)

    with pytest.raises(ArgumentError, match="boolean input column"):
        validate_with_df("ts_all(close, 2)", df)

    with pytest.raises(ArgumentError, match="boolean input column"):
        validate_with_df("seg_count(close, 2)", df)

    with pytest.raises(ArgumentError, match="boolean input column"):
        validate_with_df("seg_any(close, 2)", df)

    with pytest.raises(ArgumentError, match="boolean input column"):
        validate_with_df("seg_all(close, 2)", df)

    with pytest.raises(ArgumentError, match="boolean input column"):
        validate_with_df("seglen_count(close, [1, 1])", df)

    with pytest.raises(ArgumentError, match="boolean input column"):
        validate_with_df("seglen_any(close, [1, 1])", df)

    with pytest.raises(ArgumentError, match="boolean input column"):
        validate_with_df("seglen_all(close, [1, 1])", df)


def test_validate_new_functions_require_time_and_code_context():
    df = pl.DataFrame({"close": [1.0, 2.0]})

    with pytest.raises(ArgumentError, match="time column"):
        validate_with_df("ts_min(close, 5)", df)

    with pytest.raises(ArgumentError, match="time column"):
        validate_with_df("ts_median(close, 5)", df)

    with pytest.raises(ArgumentError, match="time column"):
        validate_with_df("argmax(close, 5)", df)


def test_validate_new_functions_require_correct_argument_count():
    df = pl.DataFrame(
        {
            "time": [1, 2],
            "code": ["A", "A"],
            "close": [1.0, 2.0],
        }
    )

    with pytest.raises(ArgumentError, match="delta"):
        validate_with_df("delta(close)", df)

    with pytest.raises(ArgumentError, match="pct_change"):
        validate_with_df("pct_change(close)", df)

    with pytest.raises(ArgumentError, match="clip"):
        validate_with_df("clip(close, 0)", df)

    with pytest.raises(ArgumentError, match="ts_median"):
        validate_with_df("ts_median(close)", df)


def test_validate_segmented_function_requires_positive_integer_literal():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [1.0, 2.0, 3.0],
            "k": [2, 2, 2],
        }
    )

    with pytest.raises(ArgumentError, match="positive integer literal segment count"):
        validate_with_df("seg_mean(close, k)", df)

    with pytest.raises(ArgumentError, match="positive integer literal segment count"):
        validate_with_df("seg_mean(close, 1 + 1)", df)

    with pytest.raises(ArgumentError, match="positive integer literal segment count"):
        validate_with_df("seg_mean(close, 0)", df)

    with pytest.raises(ArgumentError, match="positive integer literal segment count"):
        validate_with_df("seg_count(close > 0, 0)", df)


def test_validate_seglen_mean_requires_positive_integer_literal_list():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [1.0, 2.0, 3.0],
            "k": [2, 2, 2],
        }
    )

    with pytest.raises(ArgumentError, match="positive integer literal length list"):
        validate_with_df("seglen_mean(close, k)", df)

    with pytest.raises(ArgumentError, match="positive integer literal length list"):
        validate_with_df("seglen_mean(close, [])", df)

    with pytest.raises(ArgumentError, match="positive integer literal length list"):
        validate_with_df("seglen_mean(close, [1.5, 2])", df)

    with pytest.raises(ArgumentError, match="positive integer literal length list"):
        validate_with_df("seglen_mean(close, [0, 2])", df)

    with pytest.raises(ArgumentError, match="positive integer literal length list"):
        validate_with_df("seglen_mean(close, [-1, 2])", df)

    with pytest.raises(ArgumentError, match="positive integer literal length list"):
        validate_with_df("seglen_mean(close, [k, 2])", df)

    with pytest.raises(ArgumentError, match="positive integer literal length list"):
        validate_with_df("seglen_mean(close, [1 + 1, 2])", df)


def test_validate_grouped_cross_sectional_functions():
    df = pl.DataFrame(
        {
            "time": [1, 1],
            "industry": ["A", "B"],
            "close": [1.0, 2.0],
            "ret_1d": [0.1, 0.2],
        }
    )

    validate_with_df("group_demean(close, industry)", df)
    validate_with_df("group_zscore(ret_1d, industry)", df)
    validate_with_df("group_rank(close, industry, ascending=false, pct=true)", df)


def test_validate_grouped_functions_require_direct_group_column_reference():
    df = pl.DataFrame(
        {
            "time": [1, 1],
            "industry": ["A", "B"],
            "close": [1.0, 2.0],
        }
    )

    with pytest.raises(ArgumentError, match="direct group column reference"):
        validate_with_df("group_demean(close, industry == industry)", df)


def test_validate_grouped_functions_require_group_column_to_exist():
    df = pl.DataFrame(
        {
            "time": [1, 1],
            "close": [1.0, 2.0],
        }
    )

    with pytest.raises(UnknownVariableError, match="Unknown variable: industry"):
        validate_with_df("group_rank(close, industry)", df)
