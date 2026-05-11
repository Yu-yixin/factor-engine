from __future__ import annotations

from collections import deque
from dataclasses import asdict, is_dataclass
from typing import Any

import polars as pl

from factor_engine.runtime.adapters.market_schema import MarketTick


class MarketBuffer:
    def __init__(self, window_size: int) -> None:
        if window_size <= 0:
            raise ValueError("window_size must be a positive integer")
        self.window_size = window_size
        self._rows_by_symbol: dict[str, deque[dict[str, Any]]] = {}

    def add_tick(self, symbol: str, tick: MarketTick | dict[str, Any]) -> None:
        row = self._normalize_tick(symbol, tick)
        rows = self._rows_by_symbol.setdefault(symbol, deque(maxlen=self.window_size))
        rows.append(row)

    def get_window(self, symbol: str) -> pl.DataFrame:
        rows = list(self._rows_by_symbol.get(symbol, ()))
        return pl.DataFrame(rows) if rows else pl.DataFrame()

    def latest(self, symbol: str) -> dict[str, Any] | None:
        rows = self._rows_by_symbol.get(symbol)
        if not rows:
            return None
        return dict(rows[-1])

    def _normalize_tick(self, symbol: str, tick: MarketTick | dict[str, Any]) -> dict[str, Any]:
        if isinstance(tick, MarketTick):
            row = asdict(tick)
        elif is_dataclass(tick):
            row = asdict(tick)
        else:
            row = dict(tick)
        row.setdefault("symbol", symbol)
        if row["symbol"] != symbol:
            raise ValueError("tick symbol does not match buffer symbol")
        return row
