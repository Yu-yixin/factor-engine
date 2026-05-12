from __future__ import annotations

from dataclasses import dataclass
import os
import time
from typing import Literal

import polars as pl


NativeCorrCovMode = Literal["corr", "cov"]


@dataclass(frozen=True)
class NativeCorrCovResult:
    series: pl.Series
    native_corr_cov_used: bool
    native_corr_cov_time_ms: float
    native_corr_cov_bridge_time_ms: float
    native_corr_cov_output_build_time_ms: float
    native_corr_cov_fallback_reason: str
    native_corr_cov_pair_count: int
    native_corr_cov_window: int
    native_corr_cov_null_mode: str


def native_corr_cov_requested() -> bool:
    return os.environ.get("FACTOR_ENGINE_NATIVE_CORR_COV", "0").lower() in {
        "1",
        "true",
        "yes",
        "on",
        "native",
    }


def native_corr_cov_parallel_requested() -> bool:
    return os.environ.get("FACTOR_ENGINE_NATIVE_CORR_COV_PARALLEL", "0").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def native_corr_cov_available() -> bool:
    try:
        import factor_engine_native  # noqa: F401
    except Exception:
        return False
    return True


def _group_lengths(group_codes: pl.Series) -> list[int]:
    return (
        group_codes.to_frame("__code")
        .group_by("__code", maintain_order=True)
        .agg(pl.len().alias("__len"))
        .get_column("__len")
        .to_list()
    )


def evaluate_native_corr_cov_kernel(
    x_series: pl.Series,
    y_series: pl.Series,
    group_codes: pl.Series,
    window: int,
    *,
    mode: NativeCorrCovMode,
) -> NativeCorrCovResult | None:
    """Opt-in prototype bridge for the Rust shared-moment corr/cov kernel.

    The production executor does not call this module by default. It is used by
    parity tests and the A/B benchmark so the native path can be rejected without
    changing public DSL semantics.
    """

    if not native_corr_cov_requested():
        return None

    bridge_started_at = time.perf_counter()
    try:
        import factor_engine_native
    except Exception:
        return None

    try:
        x_values = x_series.cast(pl.Float64).to_list()
        y_values = y_series.cast(pl.Float64).to_list()
        lengths = _group_lengths(group_codes)
        bridge_time_ms = (time.perf_counter() - bridge_started_at) * 1000

        native_started_at = time.perf_counter()
        result_values, pair_count, scan_time_ms = factor_engine_native.grouped_corr_cov(
            x_values,
            y_values,
            lengths,
            window,
            mode,
            native_corr_cov_parallel_requested(),
        )
        native_time_ms = (time.perf_counter() - native_started_at) * 1000

        build_started_at = time.perf_counter()
        result = pl.Series(x_series.name, result_values, dtype=pl.Float64)
        output_build_time_ms = (time.perf_counter() - build_started_at) * 1000
    except Exception:
        return None

    return NativeCorrCovResult(
        series=result,
        native_corr_cov_used=True,
        native_corr_cov_time_ms=float(scan_time_ms or native_time_ms),
        native_corr_cov_bridge_time_ms=bridge_time_ms,
        native_corr_cov_output_build_time_ms=output_build_time_ms,
        native_corr_cov_fallback_reason="",
        native_corr_cov_pair_count=int(pair_count),
        native_corr_cov_window=window,
        native_corr_cov_null_mode="pairwise_valid_min_samples_2",
    )


def fallback_profile(reason: str, *, window: int) -> dict[str, float | int | bool | str]:
    return {
        "native_corr_cov_used": False,
        "native_corr_cov_time_ms": 0.0,
        "native_corr_cov_bridge_time_ms": 0.0,
        "native_corr_cov_output_build_time_ms": 0.0,
        "native_corr_cov_fallback_reason": reason,
        "native_corr_cov_pair_count": 0,
        "native_corr_cov_window": window,
        "native_corr_cov_null_mode": "pairwise_valid_min_samples_2",
    }
