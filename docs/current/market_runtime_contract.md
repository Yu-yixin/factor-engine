# Market Runtime Contract

## Standardized Tick Schema

Runtime accepts normalized market ticks with this shape:

```python
{
    "symbol": "BTCUSDT",
    "time": 1710000000000,
    "open": 68000.0,
    "high": 68100.0,
    "low": 67950.0,
    "close": 68050.0,
    "volume": 12.5,
}
```

## Runtime Responsibility

Runtime:

- buffers market data
- maintains rolling windows
- computes latest factors

Runtime does not:

- understand Binance raw payload fields
- reconnect websocket sessions
- execute orders
- manage account state
- perform risk management
- persist market history

## Adapter Responsibility

Adapters translate exchange-specific payloads into normalized ticks.

The Binance adapter may parse public market data, but it must not:

- place orders
- read private account streams
- store API keys
- call `FactorEngine`
- manage runtime buffers

## Realtime Contract

The flow is:

```text
exchange market payload
-> adapter normalization
-> MarketTick
-> MarketBuffer
-> rolling Polars DataFrame
-> RealtimeFactorRuntime
-> latest FactorResult
```

Runtime is a computation layer, not a trading system.
