import math
import os

import polars as pl
import pytest

from factor_engine.native_corr_cov import (
    evaluate_native_corr_cov_kernel,
    native_corr_cov_available,
)


def _assert_same_values(actual, expected):
    assert len(actual) == len(expected)
    for left, right in zip(actual, expected, strict=True):
        if right is None:
            assert left is None
        elif isinstance(right, float) and math.isnan(right):
            assert isinstance(left, float)
            assert math.isnan(left)
        else:
            assert left == pytest.approx(right, abs=1e-12)


@pytest.mark.skipif(
    os.environ.get("FACTOR_ENGINE_NATIVE_CORR_COV", "0") not in {"1", "true", "yes", "on"},
    reason="native corr/cov prototype is opt-in",
)
@pytest.mark.skipif(
    not native_corr_cov_available(),
    reason="factor_engine_native extension is not installed",
)
@pytest.mark.parametrize("mode", ["corr", "cov"])
def test_native_corr_cov_kernel_matches_polars_on_sorted_groups(mode):
    df = pl.DataFrame(
        {
            "code": ["A", "A", "A", "A", "B", "B", "B", "B"],
            "time": [1, 2, 3, 4, 1, 2, 3, 4],
            "x": [1.0, None, 3.0, math.nan, 10.0, 20.0, 30.0, 40.0],
            "y": [2.0, 4.0, 6.0, 8.0, 8.0, 6.0, 4.0, 2.0],
        }
    )
    native = evaluate_native_corr_cov_kernel(
        df["x"],
        df["y"],
        df["code"],
        3,
        mode=mode,
    )
    assert native is not None
    polars_expr = (
        pl.rolling_corr(pl.col("x"), pl.col("y"), window_size=3, min_samples=2)
        if mode == "corr"
        else pl.rolling_cov(pl.col("x"), pl.col("y"), window_size=3, min_samples=2)
    )
    expected = df.with_columns(polars_expr.over("code").alias("expected"))["expected"].to_list()
    _assert_same_values(native.series.to_list(), expected)
    assert native.native_corr_cov_used is True
    assert native.native_corr_cov_window == 3
    assert native.native_corr_cov_null_mode == "pairwise_valid_min_samples_2"
