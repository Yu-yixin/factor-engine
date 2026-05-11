from __future__ import annotations

import time
from collections.abc import Iterator

from factor_engine.runtime.adapters.binance_adapter import BinanceMarketAdapter
from factor_engine.runtime.adapters.market_schema import MarketTick


class PollingMarketClient:
    def __init__(self, adapter: BinanceMarketAdapter | None = None) -> None:
        self.adapter = adapter or BinanceMarketAdapter()

    def poll_klines(
        self,
        *,
        symbol: str,
        interval: str = "1m",
        limit: int = 1,
        poll_interval_seconds: float = 1.0,
    ) -> Iterator[MarketTick]:
        while True:
            for tick in self.adapter.fetch_klines(symbol=symbol, interval=interval, limit=limit):
                yield tick
            time.sleep(poll_interval_seconds)
