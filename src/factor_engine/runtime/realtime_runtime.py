from __future__ import annotations

from collections.abc import Sequence

from factor_engine.runtime.adapters.market_schema import MarketTick
from factor_engine.runtime.batch_runtime import BatchFactorRuntime
from factor_engine.runtime.config import RuntimeConfig
from factor_engine.runtime.errors import RuntimeDataError
from factor_engine.runtime.market_buffer import MarketBuffer
from factor_engine.runtime.schemas import FactorResult


class RealtimeFactorRuntime:
    def __init__(
        self,
        config: RuntimeConfig | None = None,
        *,
        batch_runtime: BatchFactorRuntime | None = None,
        buffer: MarketBuffer | None = None,
    ) -> None:
        self.config = config or RuntimeConfig()
        self.buffer = buffer or MarketBuffer(self.config.window_size)
        self.batch_runtime = batch_runtime or BatchFactorRuntime(self.config)

    def ingest_tick(self, tick: MarketTick) -> None:
        self.buffer.add_tick(tick.symbol, tick)

    def compute_latest(
        self,
        *,
        symbol: str,
        expressions: Sequence[tuple[str, str]],
    ) -> FactorResult:
        window = self.buffer.get_window(symbol)
        if window.height == 0:
            raise RuntimeDataError(f"no market data for symbol: {symbol}")
        return self.batch_runtime.compute(window, expressions, latest_only=True)
