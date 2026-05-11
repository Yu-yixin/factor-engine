# Runtime Market Closure

## Completed

- runtime package
- batch runtime
- realtime runtime
- market buffer
- normalized market schema
- Binance market adapter
- websocket/polling shell
- realtime factor computation

## Guarantees

- Factor Engine does not directly place orders.
- Runtime does not perform risk management.
- Runtime does not manage account state.
- Runtime does not own reconnect orchestration.
- Runtime does not own trading-system orchestration.
- Runtime accepts normalized market data and computes factor results.

## Next Phase

Phase 4.1 Trading-System Adapter

Goal:

The trading-system should call Runtime API instead of directly calling executor or planner internals.
