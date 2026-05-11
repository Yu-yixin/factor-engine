import polars as pl
import pytest

from factor_engine.engine import FactorEngine
from factor_engine.errors import ExecutionError


def test_engine_evaluate_skew():
    df = pl.DataFrame(
        {
            "time": [1, 1, 2, 2, 3, 3, 4, 4],
            "code": ["A", "B", "A", "B", "A", "B", "A", "B"],
            "close": [1.0, 101.0, 4.0, 104.0, 2.0, 102.0, 9.0, 109.0],
        }
    )

    result = FactorEngine().evaluate("skew(close, 3)", df)
    values = result["result"].to_list()
    expected = [
        None,
        None,
        None,
        None,
        0.38180177416060584,
        0.38180177416060584,
        0.47033046033698594,
        0.47033046033698594,
    ]

    for actual, target in zip(values, expected, strict=True):
        if target is None:
            assert actual is None
        else:
            assert actual == pytest.approx(target)


def test_skew_requires_window_at_least_three():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [1.0, 2.0, 3.0],
        }
    )

    with pytest.raises(ExecutionError, match="window >= 3"):
        FactorEngine().evaluate("skew(close, 2)", df)
