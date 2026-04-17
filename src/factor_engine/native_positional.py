from __future__ import annotations

from dataclasses import dataclass
import ctypes
import os
import time
from typing import Literal

import polars as pl


NativeMode = Literal["argmax", "argmin"]


@dataclass(frozen=True)
class NativePositionalResult:
    series: pl.Series
    to_list_time_ms: float
    group_scan_time_ms: float
    series_construct_time_ms: float
    native_kernel_used: bool
    low_copy_bridge_used: bool
    python_object_bridge_used: bool
    native_parallel_used: bool
    group_parallelism_level: int
    output_buffer_bytes_estimate: int


def _nullable_i64_buffer_bytes(length: int) -> int:
    return length * 8 + ((length + 7) // 8)


def native_requested() -> bool:
    return os.environ.get("FACTOR_ENGINE_POSITIONAL_KERNEL", "").lower() in {
        "native",
        "auto",
    }


def native_available() -> bool:
    try:
        import factor_engine_native  # noqa: F401
    except Exception:
        return False
    return True


def native_parallel_requested() -> bool:
    return os.environ.get("FACTOR_ENGINE_POSITIONAL_PARALLEL", "1").lower() not in {
        "0",
        "false",
        "no",
        "off",
    }


ctypes.pythonapi.PyBytes_AsString.argtypes = [ctypes.py_object]
ctypes.pythonapi.PyBytes_AsString.restype = ctypes.c_void_p


def _bytes_pointer(owner: bytes) -> int:
    return int(ctypes.pythonapi.PyBytes_AsString(owner))


def _series_from_native_buffers(
    name: str,
    data_bytes: bytes,
    validity_bytes: bytes,
    length: int,
) -> pl.Series:
    # Keep the bytes alive by using them as Polars buffer owners.
    data_info = (_bytes_pointer(data_bytes), 0, length)
    data = pl.Series._from_buffer(pl.Int64, data_info, data_bytes)
    validity_info = (_bytes_pointer(validity_bytes), 0, length)
    validity = pl.Series._from_buffer(pl.Boolean, validity_info, validity_bytes)
    result = pl.Series._from_buffers(pl.Int64, data, validity)
    return result.rename(name)


def _evaluate_low_copy_native(
    factor_engine_native,
    value_series: pl.Series,
    group_lengths: list[int],
    window: int,
    *,
    mode: NativeMode,
    parallel: bool,
) -> tuple[pl.Series, float, float, float] | None:
    try:
        buffer_started_at = time.perf_counter()
        value_series = value_series.cast(pl.Float64).rechunk()
        value_buffers = value_series._get_buffers()
        values = value_buffers["values"]
        values_ptr, values_offset, length = values._get_buffer_info()
        validity = value_buffers["validity"]
        if validity is None:
            validity_ptr = 0
            validity_offset = 0
        else:
            validity_ptr, validity_offset, _validity_len = validity._get_buffer_info()
        buffer_metadata_time_ms = (time.perf_counter() - buffer_started_at) * 1000

        native_started_at = time.perf_counter()
        data_bytes, validity_bytes, native_ingest_time_ms, native_scan_time_ms = (
            factor_engine_native.grouped_positional_extreme_buffers(
                values_ptr,
                values_offset,
                length,
                validity_ptr,
                validity_offset,
                group_lengths,
                window,
                mode,
                parallel,
            )
        )
        _native_total_time_ms = (time.perf_counter() - native_started_at) * 1000

        construct_started_at = time.perf_counter()
        result = _series_from_native_buffers(
            value_series.name,
            data_bytes,
            validity_bytes,
            length,
        )
        series_construct_time_ms = (time.perf_counter() - construct_started_at) * 1000
        return (
            result,
            buffer_metadata_time_ms + float(native_ingest_time_ms),
            float(native_scan_time_ms),
            series_construct_time_ms,
        )
    except Exception:
        return None


def evaluate_native_positional_kernel(
    value_series: pl.Series,
    group_codes: pl.Series,
    window: int,
    *,
    mode: NativeMode,
) -> NativePositionalResult | None:
    if not native_requested():
        return None

    try:
        import factor_engine_native
    except Exception:
        return None

    # The native module contract is intentionally narrow: it receives Arrow-backed
    # Polars series and returns a nullable Int64 distance series. The current
    # repository does not ship a built extension yet, so this branch is exercised
    # only when the optional Rust module is installed.
    try:
        group_started_at = time.perf_counter()
        group_lengths = (
            group_codes.to_frame("__code")
            .group_by("__code", maintain_order=True)
            .agg(pl.len().alias("__len"))
            .get_column("__len")
            .to_list()
        )
        group_metadata_time_ms = (time.perf_counter() - group_started_at) * 1000
        parallel = native_parallel_requested()
        low_copy_result = _evaluate_low_copy_native(
            factor_engine_native,
            value_series,
            group_lengths,
            window,
            mode=mode,
            parallel=parallel,
        )
        if low_copy_result is not None:
            result, bridge_time_ms, native_scan_time_ms, series_construct_time_ms = low_copy_result
            return NativePositionalResult(
                series=result,
                to_list_time_ms=group_metadata_time_ms + bridge_time_ms,
                group_scan_time_ms=float(native_scan_time_ms),
                series_construct_time_ms=series_construct_time_ms,
                native_kernel_used=True,
                low_copy_bridge_used=True,
                python_object_bridge_used=False,
                native_parallel_used=parallel,
                group_parallelism_level=(os.cpu_count() or 1) if parallel else 1,
                output_buffer_bytes_estimate=_nullable_i64_buffer_bytes(result.len()),
            )

        native_started_at = time.perf_counter()
        result, native_ingest_time_ms, native_scan_time_ms = factor_engine_native.grouped_positional_extreme(
            value_series,
            group_lengths,
            window,
            mode,
        )
        _native_total_time_ms = (time.perf_counter() - native_started_at) * 1000
    except Exception:
        return None
    if not isinstance(result, pl.Series):
        result = pl.Series(value_series.name, result, dtype=pl.Int64)
    return NativePositionalResult(
        series=result,
        to_list_time_ms=group_metadata_time_ms + float(native_ingest_time_ms),
        group_scan_time_ms=float(native_scan_time_ms),
        series_construct_time_ms=0.0,
        native_kernel_used=True,
        low_copy_bridge_used=False,
        python_object_bridge_used=True,
        native_parallel_used=False,
        group_parallelism_level=1,
        output_buffer_bytes_estimate=_nullable_i64_buffer_bytes(result.len()),
    )
