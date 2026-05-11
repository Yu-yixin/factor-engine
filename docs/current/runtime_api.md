# Runtime API

Phase 4 introduces a runtime layer above `FactorEngine`. The runtime is an external calling layer for applications that need stable factor computation without touching executor or planner internals.

## Responsibility

Runtime owns:

- validating runtime inputs
- buffering normalized market data
- maintaining rolling windows
- calling `FactorEngine.evaluate_many`
- returning latest factor results

Runtime does not own:

- order execution
- account state
- risk management
- API key management
- reconnect orchestration
- trading-system workflow control

## Public Runtime Entry Points

- `BatchFactorRuntime`: compute factor results for a provided dataframe.
- `RealtimeFactorRuntime`: ingest normalized market ticks, maintain rolling windows, and compute the latest factor row.
- `MarketBuffer`: in-memory rolling market window by symbol.

## Stable Lower-Level API

Runtime should call `FactorEngine`, not `Executor`, planner internals, lifecycle internals, or `execution_*.py` helper modules.
