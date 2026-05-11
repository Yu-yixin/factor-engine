import polars as pl
import pytest

from factor_engine.engine import FactorEngine
from factor_engine.errors import ExecutionError


def test_engine_evaluate_corr():
    df = pl.DataFrame(
        {
            "time": [1, 1, 2, 2, 3, 3, 4, 4],
            "code": ["A", "B", "A", "B", "A", "B", "A", "B"],
            "close": [1.0, 10.0, 2.0, 20.0, 3.0, 30.0, 4.0, 40.0],
            "volume": [2.0, 8.0, 4.0, 6.0, 6.0, 4.0, 8.0, 2.0],
        }
    )

    result = FactorEngine().evaluate("corr(close, volume, 3)", df)
    values = result["result"].to_list()
    expected = [None, None, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0]

    for actual, target in zip(values, expected, strict=True):
        if target is None:
            assert actual is None
        else:
            assert actual == pytest.approx(target)


def test_corr_requires_window_at_least_two():
    df = pl.DataFrame(
        {
            "time": [1, 2],
            "code": ["A", "A"],
            "close": [1.0, 2.0],
            "volume": [2.0, 4.0],
        }
    )

    with pytest.raises(ExecutionError, match="window >= 2"):
        FactorEngine().evaluate("corr(close, volume, 1)", df)


def test_engine_evaluate_corr_with_cross_sectional_inputs_matches_split_steps():
    df = pl.DataFrame(
        {
            "time": [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4],
            "code": ["A", "B", "C"] * 4,
            "open": [1.0, 3.0, 2.0, 2.0, 5.0, 1.0, 4.0, 6.0, 3.0, 3.0, 1.0, 2.0],
            "volume": [10.0, 20.0, 15.0, 11.0, 30.0, 12.0, 9.0, 18.0, 14.0, 13.0, 16.0, 17.0],
        }
    )

    engine = FactorEngine()
    step = engine.evaluate_many(
        [
            ("rank_open", "rank(open)"),
            ("rank_volume", "rank(volume)"),
        ],
        df,
    )
    split = engine.evaluate("corr(rank_open, rank_volume, 3)", step)
    nested = engine.evaluate("corr(rank(open), rank(volume), 3)", df)

    nested_values = nested["result"].to_list()
    split_values = split["result"].to_list()
    for actual, target in zip(nested_values, split_values, strict=True):
        if actual is None or target is None:
            assert actual is None and target is None
        elif isinstance(actual, float) and isinstance(target, float):
            if actual != actual or target != target:
                assert actual != actual and target != target
            else:
                assert actual == pytest.approx(target)
        else:
            assert actual == pytest.approx(target)
