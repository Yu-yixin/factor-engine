import polars as pl
import pytest

from factor_engine.engine import FactorEngine
from factor_engine.errors import ExecutionError


def test_engine_evaluate_kurt():
    df = pl.DataFrame(
        {
            "time": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
            "code": ["A", "B", "A", "B", "A", "B", "A", "B", "A", "B"],
            "close": [1.0, 101.0, 2.0, 102.0, 3.0, 103.0, 4.0, 104.0, 5.0, 105.0],
        }
    )

    result = FactorEngine().evaluate("kurt(close, 4)", df)
    values = result["result"].to_list()
    expected = [None, None, None, None, None, None, -1.36, -1.36, -1.36, -1.36]

    for actual, target in zip(values, expected, strict=True):
        if target is None:
            assert actual is None
        else:
            assert actual == pytest.approx(target)


def test_kurt_requires_window_at_least_four():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 4],
            "code": ["A", "A", "A", "A"],
            "close": [1.0, 2.0, 3.0, 4.0],
        }
    )

    with pytest.raises(ExecutionError, match="window >= 4"):
        FactorEngine().evaluate("kurt(close, 3)", df)
