from __future__ import annotations

import polars as pl
import pytest

from factor_engine.runtime.config import RuntimeConfig
from factor_engine.runtime.errors import RuntimeValidationError
from factor_engine.runtime.validation import validate_expressions, validate_market_frame


def test_validate_market_frame_accepts_standard_schema():
    frame = pl.DataFrame(
        {
            "symbol": ["BTCUSDT"],
            "time": [1],
            "open": [1.0],
            "high": [2.0],
            "low": [0.5],
            "close": [1.5],
            "volume": [10.0],
        }
    )

    validate_market_frame(frame, RuntimeConfig())


def test_validate_market_frame_rejects_missing_required_columns():
    with pytest.raises(RuntimeValidationError, match="missing required columns"):
        validate_market_frame(pl.DataFrame({"symbol": ["BTCUSDT"]}), RuntimeConfig())


def test_validate_expressions_rejects_empty_input():
    with pytest.raises(RuntimeValidationError, match="must not be empty"):
        validate_expressions([])
