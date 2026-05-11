import polars as pl

from factor_engine.lexer import Lexer
from factor_engine.parser import Parser
from factor_engine.validator import Validator


def parse_expression(text: str):
    tokens = Lexer(text).tokenize()
    return Parser(tokens).parse()


def validate_expression(text: str, df: pl.DataFrame):
    expr = parse_expression(text)
    return Validator(schema=df.schema).validate(expr)


def build_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "time": [1, 1, 2, 2],
            "code": ["A", "B", "A", "B"],
            "close": [10.0, 30.0, 20.0, 40.0],
            "open": [8.0, 28.0, 18.0, 35.0],
            "volume": [100.0, 200.0, 300.0, 400.0],
        }
    )


def test_pointwise_expression_profile():
    validation = validate_expression("where(close > open, close, open)", build_df())

    assert validation.profile.result_kind == "column"
    assert validation.profile.execution_kind == "pointwise"
    assert validation.profile.needs_code_group is False
    assert validation.profile.needs_time_group is False
    assert validation.profile.needs_time_order is False


def test_cross_sectional_expression_profile():
    validation = validate_expression("demean(close)", build_df())

    assert validation.profile.execution_kind == "cross_sectional"
    assert validation.profile.needs_time_group is True
    assert validation.profile.needs_time_order is False


def test_grouped_cross_sectional_expression_profile():
    df = build_df().with_columns(pl.Series("industry", ["X", "X", "Y", None]))
    validation = validate_expression("group_demean(close, industry)", df)

    assert validation.profile.execution_kind == "cross_sectional"
    assert validation.profile.needs_time_group is True
    assert validation.profile.needs_time_order is False


def test_time_series_expression_profile():
    validation = validate_expression("delay(close, 1)", build_df())

    assert validation.profile.execution_kind == "time_series"
    assert validation.profile.needs_code_group is True
    assert validation.profile.needs_time_order is True


def test_mixed_expression_profile_merges_child_requirements():
    validation = validate_expression("delay(demean(close), 1)", build_df())

    assert validation.profile.execution_kind == "time_series"
    assert validation.profile.needs_code_group is True
    assert validation.profile.needs_time_group is True
    assert validation.profile.needs_time_order is True


def test_where_expression_inherits_time_series_child_requirements():
    validation = validate_expression(
        "where(volume > ts_mean(volume, 2), close, open)",
        build_df(),
    )

    assert validation.profile.execution_kind == "time_series"
    assert validation.profile.needs_code_group is True
    assert validation.profile.needs_time_group is False
    assert validation.profile.needs_time_order is True


def test_segmented_expression_profile_is_time_series():
    validation = validate_expression("seg_mean(close, 2)", build_df())

    assert validation.profile.execution_kind == "time_series"
    assert validation.profile.needs_code_group is True
    assert validation.profile.needs_time_group is False
    assert validation.profile.needs_time_order is True


def test_where_expression_inherits_segmented_child_requirements():
    validation = validate_expression(
        "where(close > seg_mean(close, 2), close, open)",
        build_df(),
    )

    assert validation.profile.execution_kind == "time_series"
    assert validation.profile.needs_code_group is True
    assert validation.profile.needs_time_group is False
    assert validation.profile.needs_time_order is True


def test_segmented_boolean_expression_profile_is_time_series():
    validation = validate_expression("seg_count(close > open, 2)", build_df())

    assert validation.profile.execution_kind == "time_series"
    assert validation.profile.needs_code_group is True
    assert validation.profile.needs_time_group is False
    assert validation.profile.needs_time_order is True


def test_ts_median_expression_profile_is_time_series():
    validation = validate_expression("ts_median(close, 3)", build_df())

    assert validation.profile.execution_kind == "time_series"
    assert validation.profile.needs_code_group is True
    assert validation.profile.needs_time_group is False
    assert validation.profile.needs_time_order is True


def test_argpos_expression_profile_is_time_series():
    validation = validate_expression("argmax(close, 3)", build_df())

    assert validation.profile.execution_kind == "time_series"
    assert validation.profile.needs_code_group is True
    assert validation.profile.needs_time_group is False
    assert validation.profile.needs_time_order is True
