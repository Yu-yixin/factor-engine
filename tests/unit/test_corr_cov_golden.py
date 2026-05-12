import math

import polars as pl
import pytest

from factor_engine.engine import FactorEngine


def _frame(x, y, *, code=None, time=None):
    row_count = len(x)
    return pl.DataFrame(
        {
            "time": time or list(range(1, row_count + 1)),
            "code": code or ["A"] * row_count,
            "x": pl.Series(x, dtype=pl.Float64),
            "y": pl.Series(y, dtype=pl.Float64),
        }
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


def _evaluate(expr, df):
    return FactorEngine().evaluate(expr, df)["result"].to_list()


@pytest.mark.parametrize(
    ("name", "x", "y", "corr", "cov"),
    [
        (
            "no_null",
            [1.0, 2.0, 3.0, 4.0],
            [2.0, 4.0, 6.0, 8.0],
            [None, 1.0, 1.0, 1.0],
            [None, 1.0, 2.0, 2.0],
        ),
        (
            "x_null",
            [1.0, None, 3.0, 4.0],
            [2.0, 4.0, 6.0, 8.0],
            [None, None, 1.0, 1.0],
            [None, None, 4.0, 1.0],
        ),
        (
            "y_null",
            [1.0, 2.0, 3.0, 4.0],
            [2.0, None, 6.0, 8.0],
            [None, None, 1.0, 1.0],
            [None, None, 4.0, 1.0],
        ),
        (
            "both_null",
            [1.0, None, 3.0, None, 5.0],
            [2.0, 4.0, None, None, 10.0],
            [None, None, None, None, None],
            [None, None, None, None, None],
        ),
        (
            "all_null_window",
            [None, None, None],
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ),
        (
            "zero_one_two_valid_pairs",
            [1.0, None, 3.0],
            [2.0, None, 6.0],
            [None, None, 1.0],
            [None, None, 4.0],
        ),
        (
            "window_gt_history",
            [1.0, 2.0],
            [2.0, 4.0],
            [None, 1.0],
            [None, 1.0],
        ),
        (
            "zero_variance",
            [1.0, 1.0, 1.0, 1.0],
            [2.0, 3.0, 4.0, 5.0],
            [None, math.nan, math.nan, math.nan],
            [None, 0.0, 0.0, 0.0],
        ),
        (
            "nan_is_not_null",
            [1.0, math.nan, 3.0, 4.0],
            [2.0, 4.0, 6.0, 8.0],
            [None, math.nan, math.nan, math.nan],
            [None, math.nan, math.nan, math.nan],
        ),
    ],
)
def test_corr_cov_golden_semantics(name, x, y, corr, cov):
    df = _frame(x, y)
    _assert_same_values(_evaluate("corr(x, y, 3)", df), corr)
    _assert_same_values(_evaluate("cov(x, y, 3)", df), cov)


def test_corr_cov_symmetry_and_group_boundary_with_row_restore():
    df = _frame(
        [3.0, 10.0, 1.0, 2.0, 20.0, 4.0, 30.0, 40.0],
        [6.0, 8.0, 2.0, 4.0, 6.0, 8.0, 4.0, 2.0],
        code=["A", "B", "A", "A", "B", "A", "B", "B"],
        time=[3, 1, 1, 2, 2, 4, 3, 4],
    )

    corr_xy = _evaluate("corr(x, y, 3)", df)
    corr_yx = _evaluate("corr(y, x, 3)", df)
    cov_xy = _evaluate("cov(x, y, 3)", df)
    cov_yx = _evaluate("cov(y, x, 3)", df)

    _assert_same_values(corr_xy, corr_yx)
    _assert_same_values(cov_xy, cov_yx)
    _assert_same_values(
        corr_xy,
        [1.0000000000000004, None, None, 1.0, -1.0, 0.9999999999999991, -0.9999999999999997, -0.9999999999999997],
    )
    _assert_same_values(
        cov_xy,
        [2.000000000000001, None, None, 1.0, -10.0, 1.9999999999999982, -19.999999999999993, -19.999999999999993],
    )


def test_evaluate_many_repeated_corr_cov_preserves_masks():
    df = _frame(
        [1.0, None, 3.0, 4.0, 5.0],
        [2.0, 4.0, 6.0, 8.0, None],
    )
    result = FactorEngine().evaluate_many(
        [
            ("corr_a", "corr(x, y, 3)"),
            ("cov_a", "cov(x, y, 3)"),
            ("corr_b", "corr(y, x, 3)"),
            ("cov_b", "cov(y, x, 3)"),
        ],
        df,
    )

    _assert_same_values(result["corr_a"].to_list(), result["corr_b"].to_list())
    _assert_same_values(result["cov_a"].to_list(), result["cov_b"].to_list())
    _assert_same_values(result["corr_a"].to_list(), [None, None, 1.0, 1.0, 1.0])
    _assert_same_values(result["cov_a"].to_list(), [None, None, 4.0, 1.0, 1.0])
