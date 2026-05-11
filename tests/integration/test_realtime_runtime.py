from __future__ import annotations

from factor_engine.runtime import RealtimeFactorRuntime, RuntimeConfig
from factor_engine.runtime.adapters.market_schema import MarketTick


def test_realtime_runtime_ingests_ticks_and_computes_latest_factor():
    runtime = RealtimeFactorRuntime(RuntimeConfig(window_size=2))
    runtime.ingest_tick(MarketTick("BTCUSDT", 1, 10.0, 12.0, 9.0, 11.0, 100.0))
    runtime.ingest_tick(MarketTick("BTCUSDT", 2, 11.0, 13.0, 10.0, 12.5, 120.0))
    runtime.ingest_tick(MarketTick("BTCUSDT", 3, 12.0, 14.0, 11.0, 13.0, 130.0))

    result = runtime.compute_latest(
        symbol="BTCUSDT",
        expressions=[("spread", "close - open")],
    )

    assert result.frame.height == 2
    assert result.latest["time"] == 3
    assert result.latest["spread"] == 1.0
