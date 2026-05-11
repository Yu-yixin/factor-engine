from __future__ import annotations

import argparse
import time

from factor_engine.runtime import RealtimeFactorRuntime, RuntimeConfig
from factor_engine.runtime.adapters.binance_adapter import BinanceMarketAdapter
from factor_engine.runtime.adapters.market_schema import MarketTick


def sample_tick(symbol: str) -> MarketTick:
    now_ms = int(time.time() * 1000)
    return MarketTick(
        symbol=symbol,
        time=now_ms,
        open=100.0,
        high=101.0,
        low=99.5,
        close=100.5,
        volume=10.0,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Realtime Factor Engine runtime demo")
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--interval", default="1m")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    config = RuntimeConfig(window_size=32)
    runtime = RealtimeFactorRuntime(config)

    tick: MarketTick
    if args.offline:
        tick = sample_tick(args.symbol)
        print("using offline sample market tick")
    else:
        try:
            adapter = BinanceMarketAdapter(timeout=5.0)
            ticks = adapter.fetch_klines(symbol=args.symbol, interval=args.interval, limit=1)
            tick = ticks[-1]
            print(f"received public market tick: {tick.symbol} {tick.time}")
        except Exception as exc:
            print(f"public market fetch failed, using offline sample tick: {exc}")
            tick = sample_tick(args.symbol)

    runtime.ingest_tick(tick)
    result = runtime.compute_latest(
        symbol=tick.symbol,
        expressions=[
            ("spread", "close - open"),
            ("range", "high - low"),
        ],
    )
    print(result.latest)


if __name__ == "__main__":
    main()
