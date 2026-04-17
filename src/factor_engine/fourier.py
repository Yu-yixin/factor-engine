from __future__ import annotations

import cmath
import math
from collections.abc import Sequence

import polars as pl


def _coerce_complex_sequence(
    values: Sequence[complex | float],
    *,
    func_name: str,
) -> list[complex]:
    if len(values) == 0:
        raise ValueError(f"{func_name} requires at least one value")

    return [complex(value) for value in values]


def _is_power_of_two(size: int) -> bool:
    return size > 0 and (size & (size - 1)) == 0


def _fft_radix2(signal: list[complex]) -> list[complex]:
    size = len(signal)
    output = signal.copy()

    # Iterative bit-reversal keeps the fast path dependency-free while still
    # moving the heavy lifting out of the original O(n^2) Python DFT loops.
    swap_index = 0
    for index in range(1, size):
        bit = size >> 1
        while swap_index & bit:
            swap_index ^= bit
            bit >>= 1
        swap_index ^= bit
        if index < swap_index:
            output[index], output[swap_index] = output[swap_index], output[index]

    block_size = 2
    while block_size <= size:
        half_block = block_size // 2
        twiddle_step = cmath.exp((-2j * math.pi) / block_size)

        for block_start in range(0, size, block_size):
            twiddle = 1 + 0j
            for offset in range(half_block):
                left = output[block_start + offset]
                right = output[block_start + offset + half_block] * twiddle
                output[block_start + offset] = left + right
                output[block_start + offset + half_block] = left - right
                twiddle *= twiddle_step

        block_size *= 2

    return output


def _inverse_fft_radix2(coefficients: list[complex]) -> list[complex]:
    size = len(coefficients)
    conjugated = [value.conjugate() for value in coefficients]
    transformed = _fft_radix2(conjugated)
    return [value.conjugate() / size for value in transformed]


def fourier_transform(values: Sequence[complex | float]) -> list[complex]:
    """Compute the discrete Fourier transform for a 1D signal."""

    signal = _coerce_complex_sequence(values, func_name="fourier_transform")
    size = len(signal)

    # Keep the backend zero-dependency for now: power-of-two inputs use the
    # O(n log n) radix-2 path, while arbitrary lengths retain the exact DFT
    # semantics through the existing correctness-first fallback.
    if _is_power_of_two(size):
        return _fft_radix2(signal)

    return [
        sum(
            signal[index] * cmath.exp((-2j * math.pi * frequency * index) / size)
            for index in range(size)
        )
        for frequency in range(size)
    ]


def inverse_fourier_transform(coefficients: Sequence[complex | float]) -> list[complex]:
    """Reconstruct a 1D signal from its discrete Fourier coefficients."""

    spectrum = _coerce_complex_sequence(
        coefficients,
        func_name="inverse_fourier_transform",
    )
    size = len(spectrum)

    if _is_power_of_two(size):
        return _inverse_fft_radix2(spectrum)

    return [
        sum(
            spectrum[frequency] * cmath.exp((2j * math.pi * frequency * index) / size)
            for frequency in range(size)
        )
        / size
        for index in range(size)
    ]


def fourier_transform_frame(
    df: pl.DataFrame,
    *,
    value_col: str,
    time_col: str = "time",
    code_col: str = "code",
) -> pl.DataFrame:
    """Compute per-code discrete Fourier coefficients from a time-series DataFrame."""

    required_columns = [time_col, code_col, value_col]
    missing_columns = [name for name in required_columns if name not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    if df.is_empty():
        raise ValueError("fourier_transform_frame requires at least one row")

    # The table-expression backend expects a numeric source column before entering DFT math.
    if not df.schema[value_col].is_numeric():
        raise ValueError(f"Column '{value_col}' must be numeric for fourier_transform_frame")

    sorted_df = df.sort([code_col, time_col])
    grouped = sorted_df.group_by(code_col, maintain_order=True).agg(
        pl.col(value_col).alias("__values")
    )

    result_columns: dict[str, list[object]] = {
        code_col: [],
        "frequency": [],
        "sample_count": [],
        "real": [],
        "imag": [],
        "magnitude": [],
        "phase": [],
    }

    for code, values in zip(grouped[code_col].to_list(), grouped["__values"].to_list(), strict=True):
        coefficients = fourier_transform(values)
        sample_count = len(coefficients)

        result_columns[code_col].extend([code] * sample_count)
        result_columns["frequency"].extend(range(sample_count))
        result_columns["sample_count"].extend([sample_count] * sample_count)
        result_columns["real"].extend(coefficient.real for coefficient in coefficients)
        result_columns["imag"].extend(coefficient.imag for coefficient in coefficients)
        result_columns["magnitude"].extend(abs(coefficient) for coefficient in coefficients)
        result_columns["phase"].extend(cmath.phase(coefficient) for coefficient in coefficients)

    return pl.DataFrame(result_columns)
