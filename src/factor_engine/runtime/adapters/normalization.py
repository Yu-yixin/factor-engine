from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from factor_engine.runtime.adapters.market_schema import MarketTick


def normalize_generic_ohlcv(payload: Mapping[str, Any]) -> MarketTick:
    return MarketTick(
        symbol=str(payload["symbol"]),
        time=int(payload["time"]),
        open=float(payload["open"]),
        high=float(payload["high"]),
        low=float(payload["low"]),
        close=float(payload["close"]),
        volume=float(payload["volume"]),
    )


def normalize_binance_kline(payload: Mapping[str, Any] | Sequence[Any]) -> MarketTick:
    if isinstance(payload, Mapping) and "k" in payload:
        kline = payload["k"]
        return MarketTick(
            symbol=str(payload.get("s") or kline["s"]),
            time=int(kline["t"]),
            open=float(kline["o"]),
            high=float(kline["h"]),
            low=float(kline["l"]),
            close=float(kline["c"]),
            volume=float(kline["v"]),
        )

    if isinstance(payload, Mapping):
        return MarketTick(
            symbol=str(payload["symbol"]),
            time=int(payload["openTime"]),
            open=float(payload["open"]),
            high=float(payload["high"]),
            low=float(payload["low"]),
            close=float(payload["close"]),
            volume=float(payload["volume"]),
        )

    return MarketTick(
        symbol="",
        time=int(payload[0]),
        open=float(payload[1]),
        high=float(payload[2]),
        low=float(payload[3]),
        close=float(payload[4]),
        volume=float(payload[5]),
    )
