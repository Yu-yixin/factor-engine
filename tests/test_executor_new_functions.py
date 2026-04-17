import math

import polars as pl
import pytest

from factor_engine.engine import FactorEngine
from factor_engine.errors import ExecutionError
from factor_engine.executor import Executor
from factor_engine.lexer import Lexer
from factor_engine.parser import Parser


def parse_expression(text: str):
    tokens = Lexer(text).tokenize()
    return Parser(tokens).parse()


def evaluate_positional_list_fallback(df: pl.DataFrame, text: str) -> pl.DataFrame:
    expr = parse_expression(text)
    assert expr.name in {"argmax", "argmin"}
    executor = Executor(df)
    value_expr = executor._compile_time_series_input(expr.args[0])
    window = executor._expect_positive_numeric_literal(expr.args[1], expr.name)
    compiled = executor._compile_positional_list_fallback(
        value_expr,
        window,
        mode=expr.name,
    )
    return executor._evaluate_row_aligned_time_ordered(compiled, output_name="result")


def test_evaluate_ts_min():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [3.0, 1.0, 2.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("ts_min(close, 2)"))
    assert result["result"].to_list() == [3.0, 1.0, 1.0]


def test_evaluate_ts_max():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [3.0, 1.0, 2.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("ts_max(close, 2)"))
    assert result["result"].to_list() == [3.0, 3.0, 2.0]


def test_evaluate_ts_median():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [5.0, 1.0, 7.0, 3.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("ts_median(close, 3)"))
    assert result["result"].to_list() == [5.0, 3.0, 5.0, 3.0]


def test_evaluate_argmax_and_argmin():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [5.0, 1.0, 7.0, 3.0],
        }
    )

    argmax_result = Executor(df).evaluate(parse_expression("argmax(close, 3)"))
    argmin_result = Executor(df).evaluate(parse_expression("argmin(close, 3)"))

    assert argmax_result["result"].to_list() == [0, 1, 0, 1]
    assert argmin_result["result"].to_list() == [0, 0, 1, 2]


def test_evaluate_delta():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [10.0, 15.0, 12.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("delta(close, 1)"))
    assert result["result"].to_list() == [None, 5.0, -3.0]


def test_evaluate_pct_change():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [10.0, 15.0, 12.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("pct_change(close, 1)"))
    values = result["result"].to_list()

    assert values[0] is None
    assert values[1] == pytest.approx(0.5)
    assert values[2] == pytest.approx(-0.2)


def test_evaluate_abs_clip_and_sign():
    df = pl.DataFrame(
        {
            "close": [-3.0, 0.0, 8.0, None],
        }
    )

    abs_result = Executor(df).evaluate(parse_expression("abs(close)"))
    clip_result = Executor(df).evaluate(parse_expression("clip(close, -1, 5)"))
    sign_result = Executor(df).evaluate(parse_expression("sign(close)"))

    assert abs_result["result"].to_list() == [3.0, 0.0, 8.0, None]
    assert clip_result["result"].to_list() == [-1.0, 0.0, 5.0, None]
    assert sign_result["result"].to_list() == [-1.0, 0.0, 1.0, None]


def test_evaluate_alpha101_pointwise_helpers():
    df = pl.DataFrame(
        {
            "close": [-4.0, 0.0, 1.0, 9.0, None],
        }
    )

    log_result = Executor(df).evaluate(parse_expression("log(close)"))
    signedpower_result = Executor(df).evaluate(parse_expression("signedpower(close, 0.5)"))

    log_values = log_result["result"].to_list()
    assert math.isnan(log_values[0])
    assert math.isinf(log_values[1]) and log_values[1] < 0
    assert log_values[2] == pytest.approx(0.0)
    assert log_values[3] == pytest.approx(math.log(9.0))
    assert log_values[4] is None

    signedpower_values = signedpower_result["result"].to_list()
    assert signedpower_values[0] == pytest.approx(-2.0)
    assert signedpower_values[1] == pytest.approx(0.0)
    assert signedpower_values[2] == pytest.approx(1.0)
    assert signedpower_values[3] == pytest.approx(3.0)
    assert signedpower_values[4] is None


def test_new_functions_respect_code_groups_and_restore_input_order():
    df = pl.DataFrame(
        {
            "time": [2, 1, 2, 1],
            "code": ["A", "A", "B", "B"],
            "close": [20.0, 10.0, 200.0, 100.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("delta(close, 1)"))
    assert result["result"].to_list() == [10.0, None, 100.0, None]


def test_ts_median_respects_code_groups_and_restores_input_order():
    df = pl.DataFrame(
        {
            "time": [2, 1, 2, 1],
            "code": ["A", "A", "B", "B"],
            "close": [1.0, 5.0, 7.0, 3.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("ts_median(close, 2)"))
    assert result["result"].to_list() == [3.0, 5.0, 5.0, 3.0]


def test_scale_cross_section_contract_and_zero_denominator():
    df = pl.DataFrame(
        {
            "time": [1, 1, 2, 2, 3, 3],
            "code": ["A", "B", "A", "B", "A", "B"],
            "close": [1.0, -3.0, 0.0, 0.0, None, None],
        }
    )

    result = Executor(df).evaluate(parse_expression("scale(close, 2)"))

    assert result["result"].to_list() == [0.5, -1.5, None, None, None, None]


def test_alpha101_low_risk_functions_do_not_use_python_rolling_map(monkeypatch):
    original = pl.Expr.rolling_map

    def fail(self, *args, **kwargs):
        raise AssertionError("low-risk Alpha101 functions should not call rolling_map")

    monkeypatch.setattr(pl.Expr, "rolling_map", fail)
    df = pl.DataFrame(
        {
            "time": [1, 1, 2, 2, 3, 3],
            "code": ["A", "B", "A", "B", "A", "B"],
            "close": [1.0, -2.0, 3.0, 4.0, None, 5.0],
            "open": [2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
        }
    )

    try:
        engine = FactorEngine()
        engine.evaluate("log(abs(close))", df)
        engine.evaluate("signedpower(close, 2)", df)
        engine.evaluate("scale(close)", df)
        engine.evaluate("sum(close, 2)", df)
        engine.evaluate("stddev(close, 2)", df)
        engine.evaluate("correlation(open, close, 2)", df)
        engine.evaluate("covariance(open, close, 2)", df)
        engine.evaluate("min(close, 2)", df)
        engine.evaluate("max(close, 2)", df)
    finally:
        monkeypatch.setattr(pl.Expr, "rolling_map", original)


def test_argmax_respects_recent_tie_break_and_input_order():
    df = pl.DataFrame(
        {
            "time": [2, 1, 4, 3],
            "code": ["A", "A", "A", "A"],
            "close": [7.0, 5.0, 3.0, 7.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("argmax(close, 3)"))
    assert result["result"].to_list() == [0, 0, 1, 0]


def test_argpos_helpers_lock_distance_to_current_semantics_for_prefix_rows():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [5.0, 1.0, 7.0, 3.0],
        }
    )

    argmax_result = Executor(df).evaluate(parse_expression("argmax(close, 3)"))
    argmin_result = Executor(df).evaluate(parse_expression("argmin(close, 3)"))

    assert argmax_result["result"].to_list() == [0, 1, 0, 1]
    assert argmin_result["result"].to_list() == [0, 0, 1, 2]


def test_new_functions_accept_numeric_expressions():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [10.0, 15.0, 12.0],
            "open": [9.0, 11.0, 11.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("delta(close - open, 1)"))
    assert result["result"].to_list() == [None, 3.0, -3.0]


def test_scalar_math_helpers_compose_with_time_series_functions():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [10.0, 15.0, 12.0],
            "open": [9.0, 11.0, 11.0],
        }
    )

    abs_result = Executor(df).evaluate(parse_expression("abs(delta(close, 1))"))
    clip_result = Executor(df).evaluate(parse_expression("clip(ts_mean(close, 2), 0, 13)"))

    assert abs_result["result"].to_list() == [None, 5.0, 3.0]
    assert clip_result["result"].to_list() == [10.0, 12.5, 13.0]


def test_pct_change_returns_inf_when_delayed_value_is_zero():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [0.0, 1.0, 2.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("pct_change(close, 1)"))
    values = result["result"].to_list()

    assert values[0] is None
    assert values[1] == float("inf")
    assert values[2] == pytest.approx(1.0)


def test_evaluate_ts_median_with_nulls_locks_backend_behavior():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4, 5],
            "code": ["A", "A", "A", "A", "A"],
            "close": [5.0, 1.0, 7.0, 3.0, None],
        }
    )

    result = Executor(df).evaluate(parse_expression("ts_median(close, 3)"))
    assert result["result"].to_list() == [5.0, 3.0, 5.0, 3.0, 5.0]


def test_evaluate_argpos_helpers_ignore_nulls_and_return_null_for_all_null_window():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [None, 2.0, None, 2.0],
        }
    )

    argmax_result = Executor(df).evaluate(parse_expression("argmax(close, 3)"))
    argmin_result = Executor(df).evaluate(parse_expression("argmin(close, 3)"))

    assert argmax_result["result"].to_list() == [None, 0, 1, 0]
    assert argmin_result["result"].to_list() == [None, 0, 1, 0]


def test_argpos_helpers_respect_code_groups_and_time_order():
    df = pl.DataFrame(
        {
            "time": [2, 1, 3, 2, 1, 3],
            "code": ["A", "A", "A", "B", "B", "B"],
            "close": [1.0, 5.0, 3.0, 20.0, 10.0, 30.0],
        }
    )

    argmax_result = Executor(df).evaluate(parse_expression("argmax(close, 2)"))
    argmin_result = Executor(df).evaluate(parse_expression("argmin(close, 2)"))

    assert argmax_result["result"].to_list() == [1, 0, 0, 0, 0, 0]
    assert argmin_result["result"].to_list() == [0, 0, 1, 1, 0, 1]


@pytest.mark.parametrize(
    ("values", "expected_argmax", "expected_argmin"),
    [
        ([1.0, 2.0, 3.0, 4.0], [0, 0, 0, 0], [0, 1, 2, 2]),
        ([4.0, 3.0, 2.0, 1.0], [0, 1, 2, 2], [0, 0, 0, 0]),
        ([2.0, 2.0, 2.0, 2.0], [0, 0, 0, 0], [0, 0, 0, 0]),
        ([1.0, 3.0, 3.0, 2.0], [0, 0, 0, 1], [0, 1, 2, 0]),
        ([None, 3.0, None, 2.0], [None, 0, 1, 2], [None, 0, 1, 0]),
        ([None, None, None, None], [None, None, None, None], [None, None, None, None]),
    ],
)
def test_argpos_short_window_semantics(
    values: list[float | None],
    expected_argmax: list[int | None],
    expected_argmin: list[int | None],
):
    df = pl.DataFrame(
        {
            "time": list(range(1, len(values) + 1)),
            "code": ["A"] * len(values),
            "close": values,
        }
    )

    argmax_result = Executor(df).evaluate(parse_expression("argmax(close, 3)"))
    argmin_result = Executor(df).evaluate(parse_expression("argmin(close, 3)"))

    assert argmax_result["result"].to_list() == expected_argmax
    assert argmin_result["result"].to_list() == expected_argmin


@pytest.mark.parametrize("window", [5, 10, 20, 60])
def test_argpos_kernel_matches_list_fallback(window: int):
    values = [None, 5.0, 1.0, 7.0, 7.0, 2.0, None, 3.0, 9.0, 9.0, 4.0, None] * 2
    df = pl.DataFrame(
        {
            "time": list(range(1, len(values) + 1)),
            "code": ["A"] * len(values),
            "close": values,
        }
    )

    kernel_argmax = Executor(df).evaluate(parse_expression(f"argmax(close, {window})"))
    kernel_argmin = Executor(df).evaluate(parse_expression(f"argmin(close, {window})"))
    fallback_argmax = evaluate_positional_list_fallback(df, f"argmax(close, {window})")
    fallback_argmin = evaluate_positional_list_fallback(df, f"argmin(close, {window})")

    assert kernel_argmax["result"].to_list() == fallback_argmax["result"].to_list()
    assert kernel_argmin["result"].to_list() == fallback_argmin["result"].to_list()


@pytest.mark.parametrize("window", [20, 65])
def test_argpos_kernel_replaces_large_window_list_fallback(monkeypatch, window: int):
    values = [5.0, 1.0, 7.0, 3.0, None, 2.0] * 12
    df = pl.DataFrame(
        {
            "time": list(range(1, len(values) + 1)),
            "code": ["A"] * len(values),
            "close": values,
        }
    )
    expected = evaluate_positional_list_fallback(df, f"argmax(close, {window})")["result"].to_list()

    def fail(*args, **kwargs):
        raise AssertionError("dedicated positional kernel should not call concat_list")

    monkeypatch.setattr(pl, "concat_list", fail)

    result = Executor(df).evaluate(parse_expression(f"argmax(close, {window})"))

    assert "result" in result.columns
    assert result["result"].to_list() == expected


def test_argpos_short_window_does_not_use_list_materialization(monkeypatch):
    original = pl.concat_list

    def fail(*args, **kwargs):
        raise AssertionError("short-window argmax/argmin should not call concat_list")

    monkeypatch.setattr(pl, "concat_list", fail)
    try:
        df = pl.DataFrame(
            {
                "time": [1, 2, 3, 4],
                "code": ["A", "A", "A", "A"],
                "close": [5.0, 1.0, 7.0, 3.0],
            }
        )

        argmax_result = Executor(df).evaluate(parse_expression("argmax(close, 20)"))
        argmin_result = Executor(df).evaluate(parse_expression("argmin(close, 20)"))

        assert argmax_result["result"].to_list() == [0, 1, 0, 1]
        assert argmin_result["result"].to_list() == [0, 0, 1, 2]
    finally:
        monkeypatch.setattr(pl, "concat_list", original)


def test_materialized_argpos_kernel_does_not_use_list_materialization(monkeypatch):
    original = pl.concat_list

    def fail(*args, **kwargs):
        raise AssertionError("materialized argmax/argmin should use the dedicated kernel")

    monkeypatch.setattr(pl, "concat_list", fail)
    try:
        df = pl.DataFrame(
            {
                "time": [1, 1, 2, 2, 3, 3],
                "code": ["A", "B", "A", "B", "A", "B"],
                "close": [2.0, 1.0, 4.0, 3.0, 4.0, 5.0],
            }
        )

        result = FactorEngine().evaluate("argmax(rank(close), 2)", df)

        assert "result" in result.columns
    finally:
        monkeypatch.setattr(pl, "concat_list", original)


def test_argpos_helpers_do_not_use_python_rolling_map(monkeypatch):
    original = pl.Expr.rolling_map

    def fail(*args, **kwargs):
        raise AssertionError("argmax/argmin should not call rolling_map")

    monkeypatch.setattr(pl.Expr, "rolling_map", fail)
    try:
        df = pl.DataFrame(
            {
                "time": [1, 2, 3, 4],
                "code": ["A", "A", "A", "A"],
                "close": [5.0, 1.0, 7.0, 3.0],
            }
        )

        argmax_result = Executor(df).evaluate(parse_expression("argmax(close, 3)"))
        argmin_result = Executor(df).evaluate(parse_expression("argmin(close, 3)"))

        assert argmax_result["result"].to_list() == [0, 1, 0, 1]
        assert argmin_result["result"].to_list() == [0, 0, 1, 2]
    finally:
        monkeypatch.setattr(pl.Expr, "rolling_map", original)


def test_evaluate_boolean_time_series_functions_with_nulls():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [2.0, None, 5.0],
            "open": [1.0, 1.0, 4.0],
        }
    )

    ts_count = Executor(df).evaluate(parse_expression("ts_count(close > open, 2)"))
    ts_any = Executor(df).evaluate(parse_expression("ts_any(close > open, 2)"))
    ts_all = Executor(df).evaluate(parse_expression("ts_all(close > open, 2)"))

    assert ts_count["result"].to_list() == [1, 1, 1]
    assert ts_any["result"].to_list() == [True, True, True]
    assert ts_all["result"].to_list() == [True, False, False]


def test_evaluate_ts_rank_with_ties_and_pct():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [10.0, 30.0, 30.0, 20.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("ts_rank(close, 3, pct=true)"))

    assert result["result"].to_list() == pytest.approx([1.0, 0.5, 0.5, 1.0])


def test_evaluate_ts_rank_respects_code_groups_and_input_order():
    df = pl.DataFrame(
        {
            "time": [2, 1, 2, 1],
            "code": ["A", "A", "B", "B"],
            "close": [20.0, 10.0, 50.0, 100.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("ts_rank(close, 2)"))

    assert result["result"].to_list() == [1.0, 1.0, 2.0, 1.0]


def test_evaluate_seg_mean_broadcasts_segment_means():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4, 5, 6],
            "code": ["A", "A", "A", "A", "A", "A"],
            "close": [1.0, 2.0, 10.0, 20.0, 100.0, 200.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("seg_mean(close, 3)"))

    assert result["result"].to_list() == [1.5, 1.5, 15.0, 15.0, 150.0, 150.0]


def test_evaluate_seg_sum_broadcasts_segment_sums():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4, 5, 6],
            "code": ["A", "A", "A", "A", "A", "A"],
            "close": [1.0, 2.0, 10.0, 20.0, 100.0, 200.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("seg_sum(close, 3)"))

    assert result["result"].to_list() == [3.0, 3.0, 30.0, 30.0, 300.0, 300.0]


def test_evaluate_seglen_mean_broadcasts_length_segment_means():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4, 5, 6, 7],
            "code": ["A", "A", "A", "A", "A", "A", "A"],
            "close": [1.0, 2.0, 3.0, 10.0, 20.0, 30.0, 40.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("seglen_mean(close, [3, 5, 2])"))

    assert result["result"].to_list() == [2.0, 2.0, 2.0, 25.0, 25.0, 25.0, 25.0]


def test_evaluate_seglen_sum_and_boolean_family():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [1.0, None, 10.0, 14.0],
            "open": [0.0, 1.0, 8.0, 13.0],
        }
    )

    seglen_sum = Executor(df).evaluate(parse_expression("seglen_sum(open, [3, 5])"))
    seglen_count = Executor(df).evaluate(parse_expression("seglen_count(close > open, [3, 5])"))
    seglen_any = Executor(df).evaluate(parse_expression("seglen_any(close > open, [3, 5])"))
    seglen_all = Executor(df).evaluate(parse_expression("seglen_all(close > open, [3, 5])"))

    assert seglen_sum["result"].to_list() == [9.0, 9.0, 9.0, 13.0]
    assert seglen_count["result"].to_list() == [2, 2, 2, 1]
    assert seglen_any["result"].to_list() == [True, True, True, True]
    assert seglen_all["result"].to_list() == [False, False, False, True]


def test_evaluate_segmented_boolean_functions_with_nulls():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [2.0, None, 5.0, 7.0],
            "open": [1.0, 1.0, 4.0, 8.0],
        }
    )

    seg_count = Executor(df).evaluate(parse_expression("seg_count(close > open, 2)"))
    seg_any = Executor(df).evaluate(parse_expression("seg_any(close > open, 2)"))
    seg_all = Executor(df).evaluate(parse_expression("seg_all(close > open, 2)"))

    assert seg_count["result"].to_list() == [1, 1, 1, 1]
    assert seg_any["result"].to_list() == [True, True, True, True]
    assert seg_all["result"].to_list() == [False, False, False, False]


def test_evaluate_seg_mean_respects_code_groups_and_restores_input_order():
    df = pl.DataFrame(
        {
            "time": [2, 1, 3, 2, 1, 3],
            "code": ["A", "A", "A", "B", "B", "B"],
            "close": [20.0, 10.0, 30.0, 200.0, 100.0, 300.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("seg_mean(close, 2)"))

    assert result["result"].to_list() == [15.0, 15.0, 30.0, 150.0, 150.0, 300.0]


def test_evaluate_seg_mean_allows_more_segments_than_samples():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [4.0, 5.0, 6.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("seg_mean(close, 5)"))

    assert result["result"].to_list() == [4.0, 5.0, 6.0]


def test_evaluate_seglen_mean_allows_truncated_last_segment():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [1.0, 3.0, 10.0, 14.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("seglen_mean(close, [3, 5])"))

    assert result["result"].to_list() == [14.0 / 3.0, 14.0 / 3.0, 14.0 / 3.0, 14.0]


def test_evaluate_seglen_mean_errors_when_lengths_do_not_cover_group():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [1.0, 3.0, 10.0, 14.0],
        }
    )

    with pytest.raises(ExecutionError, match="segment lengths do not cover full group"):
        Executor(df).evaluate(parse_expression("seglen_mean(close, [2, 1])"))

    with pytest.raises(ExecutionError, match="segment lengths do not cover full group"):
        Executor(df).evaluate(parse_expression("seglen_sum(close, [2, 1])"))


def test_evaluate_seg_count_allows_more_segments_than_samples():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [4.0, 5.0, 6.0],
            "open": [1.0, 6.0, 2.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("seg_count(close > open, 5)"))

    assert result["result"].to_list() == [1, 0, 1]


def test_evaluate_seg_mean_can_participate_in_larger_expression():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [1.0, 3.0, 10.0, 14.0],
            "open": [0.0, 0.0, 0.0, 0.0],
        }
    )

    result = Executor(df).evaluate(
        parse_expression("where(close > seg_mean(close, 2), close, open)")
    )

    assert result["result"].to_list() == [0.0, 3.0, 0.0, 14.0]


def test_evaluate_seglen_mean_respects_code_groups_and_restores_input_order():
    df = pl.DataFrame(
        {
            "time": [2, 1, 3, 2, 1],
            "code": ["A", "A", "A", "B", "B"],
            "close": [2.0, 1.0, 3.0, 20.0, 10.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("seglen_mean(close, [2, 2])"))

    assert result["result"].to_list() == [1.5, 1.5, 3.0, 15.0, 15.0]


def test_evaluate_segmented_functions_can_mix_in_larger_expression():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [1.0, 3.0, 10.0, 14.0],
            "open": [0.0, 1.0, 8.0, 13.0],
        }
    )

    result = Executor(df).evaluate(
        parse_expression("seg_sum(close, 2) / seg_count(close > open, 2)")
    )

    assert result["result"].to_list() == [2.0, 2.0, 12.0, 12.0]


def test_evaluate_seglen_mean_can_participate_in_larger_expression():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [1.0, 3.0, 10.0, 14.0],
            "open": [0.0, 0.0, 0.0, 0.0],
        }
    )

    result = Executor(df).evaluate(
        parse_expression("where(close > seglen_mean(close, [3, 5]), close, open)")
    )

    assert result["result"].to_list() == [0.0, 0.0, 10.0, 0.0]


def test_grouped_cross_sectional_functions_isolate_groups():
    df = pl.DataFrame(
        {
            "time": [1, 1, 1, 1],
            "code": ["A", "B", "C", "D"],
            "industry": ["X", "X", "Y", None],
            "close": [10.0, 20.0, 30.0, 50.0],
            "ret_1d": [1.0, 3.0, 10.0, 50.0],
        }
    )

    demean_result = Executor(df).evaluate(parse_expression("group_demean(close, industry)"))
    zscore_result = Executor(df).evaluate(parse_expression("group_zscore(ret_1d, industry)"))
    rank_result = Executor(df).evaluate(
        parse_expression("group_rank(close, industry, ascending=false, pct=true)")
    )

    assert demean_result["result"].to_list() == [-5.0, 5.0, 0.0, 0.0]
    assert zscore_result["result"].to_list()[0] == pytest.approx(-0.70710678)
    assert zscore_result["result"].to_list()[1] == pytest.approx(0.70710678)
    assert zscore_result["result"].to_list()[2:] == [None, None]
    assert rank_result["result"].to_list() == [1.0, 0.5, 1.0, 1.0]


def test_grouped_cross_sectional_functions_preserve_input_order():
    df = pl.DataFrame(
        {
            "time": [1, 1, 1, 1],
            "code": ["B", "A", "D", "C"],
            "industry": ["X", "X", None, "Y"],
            "close": [20.0, 10.0, 50.0, 30.0],
        }
    )

    result = Executor(df).evaluate(parse_expression("group_demean(close, industry)"))
    assert result["result"].to_list() == [5.0, -5.0, 0.0, 0.0]
