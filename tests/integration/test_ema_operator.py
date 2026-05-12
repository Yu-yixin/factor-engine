from __future__ import annotations

import pytest
import polars as pl

from factor_engine.engine import FactorEngine
from factor_engine.errors import ArgumentError
from factor_engine.registry import get_function_spec


def build_unsorted_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "time": [3, 1, 2, 1, 4, 3, 2, 4],
            "code": ["BTC", "BTC", "BTC", "ETH", "BTC", "ETH", "ETH", "ETH"],
            "close": [13.0, 10.0, 12.0, 100.0, 16.0, 105.0, 102.0, 109.0],
        }
    )


def recursive_ema(values: list[float], span: int) -> list[float]:
    alpha = 2 / (span + 1)
    state: float | None = None
    result: list[float] = []
    for value in values:
        if state is None:
            state = value
        else:
            state = alpha * value + (1 - alpha) * state
        result.append(state)
    return result


def expected_by_code(df: pl.DataFrame, span: int) -> list[float]:
    sorted_df = df.with_row_index("__row_idx").sort(["code", "time"])
    expected: dict[int, float] = {}
    for code in sorted_df["code"].unique(maintain_order=True).to_list():
        group = sorted_df.filter(pl.col("code") == code)
        values = group["close"].to_list()
        for row_idx, value in zip(
            group["__row_idx"].to_list(),
            recursive_ema(values, span),
            strict=True,
        ):
            expected[row_idx] = value
    return [expected[index] for index in range(df.height)]


def expected_macd_by_code(df: pl.DataFrame) -> dict[str, list[float]]:
    sorted_df = df.with_row_index("__row_idx").sort(["code", "time"])
    expected: dict[int, dict[str, float]] = {}
    for code in sorted_df["code"].unique(maintain_order=True).to_list():
        group = sorted_df.filter(pl.col("code") == code)
        close_values = group["close"].to_list()
        ema12 = recursive_ema(close_values, 12)
        ema26 = recursive_ema(close_values, 26)
        dif_values = [fast - slow for fast, slow in zip(ema12, ema26, strict=True)]
        dea_values = recursive_ema(dif_values, 9)
        hist_values = [dif - dea for dif, dea in zip(dif_values, dea_values, strict=True)]
        for row_idx, dif, dea, hist in zip(
            group["__row_idx"].to_list(),
            dif_values,
            dea_values,
            hist_values,
            strict=True,
        ):
            expected[row_idx] = {
                "macd_dif": dif,
                "macd_dea": dea,
                "macd_hist": hist,
            }

    return {
        name: [expected[index][name] for index in range(df.height)]
        for name in ["macd_dif", "macd_dea", "macd_hist"]
    }


def assert_float_lists_close(actual: list[object], expected: list[object]) -> None:
    assert len(actual) == len(expected)
    for observed, target in zip(actual, expected, strict=True):
        if observed is None or target is None:
            assert observed is None and target is None
            continue
        assert observed == pytest.approx(target)


@pytest.mark.parametrize("span", [3, 12, 26])
def test_ema_matches_adjust_false_recursive_reference_by_code(span: int) -> None:
    df = build_unsorted_df()
    result = FactorEngine().evaluate(f"ema(close, {span})", df)

    assert result.height == df.height
    assert result.select(df.columns).to_dict(as_series=False) == df.to_dict(as_series=False)
    assert_float_lists_close(result["result"].to_list(), expected_by_code(df, span))


def test_ema_state_is_isolated_between_codes() -> None:
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 1, 2, 3],
            "code": ["BTC", "BTC", "BTC", "ETH", "ETH", "ETH"],
            "close": [10.0, 12.0, 14.0, 1000.0, 1000.0, 1000.0],
        }
    )

    result = FactorEngine().evaluate("ema(close, 3)", df)

    assert_float_lists_close(result["result"].to_list()[:3], [10.0, 11.0, 12.5])
    assert_float_lists_close(result["result"].to_list()[3:], [1000.0, 1000.0, 1000.0])


def test_ema_uses_pandas_adjust_false_null_output_policy() -> None:
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4, 5],
            "code": ["BTC", "BTC", "BTC", "BTC", "BTC"],
            "close": [None, 1.0, None, 3.0, 4.0],
        },
        schema={"time": pl.Int64, "code": pl.String, "close": pl.Float64},
    )

    result = FactorEngine().evaluate("ema(close, 3)", df)

    assert_float_lists_close(
        result["result"].to_list(),
        [None, 1.0, 1.0, 2.333333333333333, 3.1666666666666665],
    )


def test_ema_expression_composition_supports_macd_shape_without_macd_primitive() -> None:
    df = build_unsorted_df()
    engine = FactorEngine()
    expressions = [
        ("macd_dif", "ema(close, 12) - ema(close, 26)"),
        ("macd_dea", "ema(ema(close, 12) - ema(close, 26), 9)"),
        (
            "macd_hist",
            "(ema(close, 12) - ema(close, 26)) - ema(ema(close, 12) - ema(close, 26), 9)",
        ),
    ]

    for _name, expression in expressions:
        engine.parse(expression)
        engine.validate(expression, df)
    result = engine.evaluate_many(expressions, df)

    assert result.height == df.height
    assert result.select(df.columns).to_dict(as_series=False) == df.to_dict(as_series=False)
    assert result.columns == df.columns + ["macd_dif", "macd_dea", "macd_hist"]
    expected = expected_macd_by_code(df)
    assert_float_lists_close(result["macd_dif"].to_list(), expected["macd_dif"])
    assert_float_lists_close(result["macd_dea"].to_list(), expected["macd_dea"])
    assert_float_lists_close(result["macd_hist"].to_list(), expected["macd_hist"])


@pytest.mark.parametrize(
    ("expression", "error_type"),
    [
        ("ema(close)", ArgumentError),
        ("ema(close, 0)", ArgumentError),
        ("ema(close, -3)", ArgumentError),
        ("ema(close, 12.5)", ArgumentError),
        ('ema(close, "12")', Exception),
    ],
)
def test_ema_rejects_invalid_span_arguments(
    expression: str,
    error_type: type[Exception],
) -> None:
    df = build_unsorted_df()

    with pytest.raises(error_type):
        FactorEngine().validate(expression, df)


def test_ema_is_planned_as_ordered_recursive_on_existing_ordered_route() -> None:
    trace = FactorEngine().inspect_plan("ema(close, 12)", build_unsorted_df())

    assert trace["route"] == "compiled"
    assert trace["needs_time_order"] is True
    assert trace["needs_code_group"] is True
    assert trace["root_window_kind"] == "recursive"


def test_ema_does_not_register_macd_primitive() -> None:
    assert get_function_spec("macd") is None
