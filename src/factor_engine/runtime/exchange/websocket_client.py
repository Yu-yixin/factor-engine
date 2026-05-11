from __future__ import annotations

from collections.abc import AsyncIterator

from factor_engine.runtime.adapters.binance_adapter import BinanceMarketAdapter
from factor_engine.runtime.adapters.market_schema import MarketTick
from factor_engine.runtime.errors import RuntimeDependencyError


class WebsocketMarketClient:
    def __init__(self, adapter: BinanceMarketAdapter | None = None) -> None:
        self.adapter = adapter or BinanceMarketAdapter()

    async def stream_binance_klines(
        self,
        *,
        symbol: str,
        interval: str = "1m",
    ) -> AsyncIterator[MarketTick]:
        try:
            import websockets  # type: ignore[import-not-found]
        except Exception as exc:
            raise RuntimeDependencyError(
                "websockets is required for websocket streaming"
            ) from exc

        stream = f"{symbol.lower()}@kline_{interval}"
        url = f"wss://stream.binance.com:9443/ws/{stream}"
        async with websockets.connect(url) as websocket:
            async for message in websocket:
                yield self.adapter.normalize_websocket_kline(message)
