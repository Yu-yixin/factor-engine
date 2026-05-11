# Runtime Contract

## Runtime Config

The runtime uses:

```python
RuntimeConfig(
    code_column="symbol",
    time_column="time",
    window_size=500,
    strict=True,
)
```

## Batch Semantics

`BatchFactorRuntime` accepts a Polars dataframe and a sequence of named expressions. It delegates calculation to `FactorEngine.evaluate_many` and returns a `FactorResult`.

## Realtime Semantics

- Input is a rolling market window.
- `compute_latest()` returns the last row of factor results by default.
- Runtime does not persist historical data.
- Runtime does not own a database.
- Runtime does not directly depend on websocket clients.

## Boundaries

Runtime must not change:

- `FactorEngine.evaluate`
- `FactorEngine.evaluate_many`
- planner route semantics
- lifecycle semantics
- native fallback behavior
- profiling schema
- benchmark fields
