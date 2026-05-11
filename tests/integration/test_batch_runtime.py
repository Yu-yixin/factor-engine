from __future__ import annotations

import polars as pl

from factor_engine.runtime import BatchFactorRuntime, RuntimeConfig


def test_batch_factor_runtime_calls_factor_engine_evaluate_many():
    frame = pl.DataFrame(
        {
            "symbol": ["BTCUSDT", "BTCUSDT"],
            "time": [1, 2],
            "open": [10.0, 11.0],
            "high": [12.0, 13.0],
            "low": [9.0, 10.0],
            "close": [11.0, 12.5],
            "volume": [100.0, 120.0],
        }
    )
    runtime = BatchFactorRuntime(RuntimeConfig(window_size=10))

    result = runtime.compute(frame, [("spread", "close - open")], latest_only=True)

    assert result.frame.get_column("spread").to_list() == [1.0, 1.5]
    assert result.latest["spread"] == 1.5
