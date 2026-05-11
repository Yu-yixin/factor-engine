from __future__ import annotations

import json

from factor_engine.runtime.adapters.binance_adapter import BinanceMarketAdapter
from factor_engine.runtime.adapters.normalization import (
    normalize_binance_kline,
    normalize_generic_ohlcv,
)


def test_normalize_generic_ohlcv():
    tick = normalize_generic_ohlcv(
        {
            "symbol": "BTCUSDT",
            "time": 1,
            "open": "10",
            "high": "12",
            "low": "9",
            "close": "11",
            "volume": "5",
        }
    )

    assert tick.symbol == "BTCUSDT"
    assert tick.close == 11.0


def test_normalize_binance_rest_kline_with_adapter_symbol():
    payload = [1000, "10", "12", "9", "11", "5"]

    tick = BinanceMarketAdapter.normalize_rest_kline("BTCUSDT", payload)

    assert tick.symbol == "BTCUSDT"
    assert tick.time == 1000
    assert tick.close == 11.0


def test_normalize_binance_websocket_kline_payload():
    payload = {
        "s": "BTCUSDT",
        "k": {
            "t": 1000,
            "s": "BTCUSDT",
            "o": "10",
            "h": "12",
            "l": "9",
            "c": "11",
            "v": "5",
        },
    }

    tick = BinanceMarketAdapter.normalize_websocket_kline(json.dumps(payload))

    assert tick.symbol == "BTCUSDT"
    assert tick.high == 12.0
    assert normalize_binance_kline(payload).volume == 5.0
