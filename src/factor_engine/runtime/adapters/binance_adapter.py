from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import urlopen

from factor_engine.runtime.adapters.market_schema import MarketTick
from factor_engine.runtime.adapters.normalization import normalize_binance_kline


BINANCE_PUBLIC_REST_BASE_URL = "https://api.binance.com"


class BinanceMarketAdapter:
    def __init__(self, base_url: str = BINANCE_PUBLIC_REST_BASE_URL, timeout: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def fetch_klines(
        self,
        *,
        symbol: str,
        interval: str = "1m",
        limit: int = 1,
    ) -> list[MarketTick]:
        query = urlencode({"symbol": symbol.upper(), "interval": interval, "limit": limit})
        url = f"{self.base_url}/api/v3/klines?{query}"
        with urlopen(url, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return [self.normalize_rest_kline(symbol.upper(), item) for item in payload]

    @staticmethod
    def normalize_rest_kline(symbol: str, payload) -> MarketTick:
        tick = normalize_binance_kline(payload)
        if tick.symbol:
            return tick
        return MarketTick(
            symbol=symbol,
            time=tick.time,
            open=tick.open,
            high=tick.high,
            low=tick.low,
            close=tick.close,
            volume=tick.volume,
        )

    @staticmethod
    def normalize_websocket_kline(payload) -> MarketTick:
        if isinstance(payload, str):
            payload = json.loads(payload)
        return normalize_binance_kline(payload)
