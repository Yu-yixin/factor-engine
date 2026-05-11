from __future__ import annotations

from factor_engine.runtime.adapters.market_schema import MarketTick
from factor_engine.runtime.market_buffer import MarketBuffer


def _tick(symbol: str, time: int, close: float) -> MarketTick:
    return MarketTick(
        symbol=symbol,
        time=time,
        open=close - 1,
        high=close + 1,
        low=close - 2,
        close=close,
        volume=10.0,
    )


def test_market_buffer_truncates_to_window_size():
    buffer = MarketBuffer(window_size=2)

    buffer.add_tick("BTCUSDT", _tick("BTCUSDT", 1, 10.0))
    buffer.add_tick("BTCUSDT", _tick("BTCUSDT", 2, 11.0))
    buffer.add_tick("BTCUSDT", _tick("BTCUSDT", 3, 12.0))

    assert buffer.get_window("BTCUSDT").get_column("time").to_list() == [2, 3]


def test_market_buffer_keeps_symbols_separate():
    buffer = MarketBuffer(window_size=3)

    buffer.add_tick("BTCUSDT", _tick("BTCUSDT", 1, 10.0))
    buffer.add_tick("ETHUSDT", _tick("ETHUSDT", 1, 20.0))

    assert buffer.latest("BTCUSDT")["close"] == 10.0
    assert buffer.latest("ETHUSDT")["close"] == 20.0


def test_market_buffer_empty_window_returns_empty_frame_and_no_latest():
    buffer = MarketBuffer(window_size=3)

    assert buffer.get_window("BTCUSDT").height == 0
    assert buffer.latest("BTCUSDT") is None
