import polars as pl
import pytest

from factor_engine.engine import FactorEngine
from factor_engine.errors import ArgumentError


def test_engine_evaluate_fft_returns_frequency_table():
    df = pl.DataFrame(
        {
            "time": [2, 1, 2, 1],
            "code": ["A", "A", "B", "B"],
            "close": [0.0, 1.0, 1.0, 0.0],
        }
    )

    result = FactorEngine().evaluate("fft(close)", df)

    assert result.columns == [
        "code",
        "frequency",
        "sample_count",
        "real",
        "imag",
        "magnitude",
        "phase",
    ]

    result_a = result.filter(pl.col("code") == "A").sort("frequency")
    result_b = result.filter(pl.col("code") == "B").sort("frequency")

    assert result_a["real"].to_list() == pytest.approx([1.0, 1.0])
    assert result_a["imag"].to_list() == pytest.approx([0.0, 0.0])
    assert result_b["real"].to_list() == pytest.approx([1.0, -1.0])
    assert result_b["imag"].to_list() == pytest.approx([0.0, 0.0])


def test_engine_evaluate_fft_with_custom_time_and_code_columns():
    df = pl.DataFrame(
        {
            "ts": [2, 1],
            "symbol": ["A", "A"],
            "close": [0.0, 1.0],
        }
    )

    engine = FactorEngine(time_col="ts", code_col="symbol")
    result = engine.evaluate("fft(close)", df)

    assert result.columns == [
        "symbol",
        "frequency",
        "sample_count",
        "real",
        "imag",
        "magnitude",
        "phase",
    ]
    assert result["symbol"].to_list() == ["A", "A"]
    assert result["real"].to_list() == pytest.approx([1.0, 1.0])


def test_engine_rejects_fft_inside_arithmetic_expression():
    df = pl.DataFrame(
        {
            "time": [1, 2],
            "code": ["A", "A"],
            "close": [1.0, 2.0],
        }
    )

    with pytest.raises(ArgumentError, match="root expression"):
        FactorEngine().evaluate("fft(close) + 1", df)


def test_engine_rejects_fft_without_code_column():
    df = pl.DataFrame(
        {
            "time": [1, 2],
            "close": [1.0, 2.0],
        }
    )

    with pytest.raises(ArgumentError, match="code column"):
        FactorEngine().evaluate("fft(close)", df)
