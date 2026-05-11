from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketTick:
    symbol: str
    time: int
    open: float
    high: float
    low: float
    close: float
    volume: float
