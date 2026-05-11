from __future__ import annotations

import polars as pl
import pytest

from factor_engine.runtime.config import RuntimeConfig
from factor_engine.runtime.schemas import FactorResult


def test_runtime_config_defaults_match_market_contract():
    config = RuntimeConfig()

    assert config.code_column == "symbol"
    assert config.time_column == "time"
    assert config.window_size == 500
    assert config.strict is True


def test_runtime_config_rejects_invalid_window_size():
    with pytest.raises(ValueError, match="window_size"):
        RuntimeConfig(window_size=0)


def test_factor_result_latest_uses_last_row():
    frame = pl.DataFrame({"symbol": ["BTCUSDT", "BTCUSDT"], "alpha": [1.0, 2.0]})

    result = FactorResult.from_frame(frame, (("alpha", "close - open"),), latest_only=True)

    assert result.latest == {"symbol": "BTCUSDT", "alpha": 2.0}
    assert result.expressions == (("alpha", "close - open"),)
