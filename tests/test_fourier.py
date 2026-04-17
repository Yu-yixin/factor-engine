import cmath
import math

import polars as pl
import pytest

from factor_engine.fourier import (
    fourier_transform,
    fourier_transform_frame,
    inverse_fourier_transform,
)


def assert_complex_sequences_close(
    actual: list[complex],
    expected: list[complex],
) -> None:
    assert len(actual) == len(expected)

    for left, right in zip(actual, expected, strict=True):
        assert left.real == pytest.approx(right.real)
        assert left.imag == pytest.approx(right.imag)


def test_fourier_transform_delta_signal():
    result = fourier_transform([1.0, 0.0, 0.0, 0.0])

    assert_complex_sequences_close(
        result,
        [1.0 + 0.0j, 1.0 + 0.0j, 1.0 + 0.0j, 1.0 + 0.0j],
    )


def test_inverse_fourier_transform_recovers_signal():
    signal = [0.0, 1.0, 0.0, -1.0]
    coefficients = fourier_transform(signal)
    recovered = inverse_fourier_transform(coefficients)

    assert_complex_sequences_close(
        recovered,
        [complex(value, 0.0) for value in signal],
    )


def test_fourier_transform_non_power_of_two_matches_direct_dft():
    signal = [1.0, -1.0, 2.0]
    size = len(signal)

    expected = [
        sum(
            complex(signal[index], 0.0)
            * cmath.exp((-2j * math.pi * frequency * index) / size)
            for index in range(size)
        )
        for frequency in range(size)
    ]

    result = fourier_transform(signal)
    assert_complex_sequences_close(result, expected)


def test_fourier_transform_frame_groups_by_code_and_sorts_time():
    df = pl.DataFrame(
        {
            "time": [2, 1, 2, 1],
            "code": ["A", "A", "B", "B"],
            "close": [0.0, 1.0, 1.0, 0.0],
        }
    )

    result = fourier_transform_frame(df, value_col="close")

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
    assert result_a["sample_count"].to_list() == [2, 2]
    assert result_b["sample_count"].to_list() == [2, 2]


def test_fourier_transform_frame_requires_columns():
    df = pl.DataFrame({"time": [1], "code": ["A"]})

    with pytest.raises(ValueError, match="close"):
        fourier_transform_frame(df, value_col="close")


def test_fourier_transform_frame_requires_numeric_column():
    df = pl.DataFrame(
        {
            "time": [1, 2],
            "code": ["A", "A"],
            "label": ["x", "y"],
        }
    )

    with pytest.raises(ValueError, match="must be numeric"):
        fourier_transform_frame(df, value_col="label")
