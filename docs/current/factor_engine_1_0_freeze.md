# Factor Engine 1.0 Freeze

## Status

Factor Engine 1.0 Core Architecture is frozen.

## Completed Capabilities

- DSL parser/validator
- `evaluate`/`evaluate_many`
- row-aligned execution
- ordered execution
- materialized ordered execution
- segmented execution
- positional/native execution shell
- DAG/CSE reuse support
- lifecycle/drop integration
- profiling/accounting
- execution coordinator architecture
- runtime package
- batch runtime
- realtime runtime
- market buffer
- normalized market schema
- read-only Binance market adapter
- realtime market factor demo

## Stable Public Entry Points

- `FactorEngine.parse`
- `FactorEngine.validate`
- `FactorEngine.evaluate`
- `FactorEngine.evaluate_many`
- `BatchFactorRuntime.compute`
- `RealtimeFactorRuntime.ingest_tick`
- `RealtimeFactorRuntime.compute_latest`

Note: the current runtime implementation exposes `BatchFactorRuntime.compute`.
`BatchFactorRuntime.compute_factors` is not present in the codebase at this
freeze point and should not be treated as a stable entry point unless a later
proposal adds it explicitly.

## Internal Boundaries

External systems should not call:

- `executor.py` internals
- planner internals
- lifecycle internals
- `execution_*.py` internals
- native bridge internals

## Runtime Market Capabilities

Factor Engine 1.0 can receive normalized market data, maintain an in-memory
rolling market window, compute batch factors, and compute latest realtime
factor results from that rolling window.

The runtime market path is:

```text
exchange market data
-> market adapter
-> normalized market frame
-> runtime window
-> Factor Engine
-> latest factor result
```

## What Factor Engine Does

- receives normalized data
- validates requests
- computes batch factors
- computes latest realtime factors from rolling windows
- returns factor results

## What Factor Engine Does Not Do

- order execution
- risk control
- account state
- position management
- API key storage
- trading-system orchestration
- strategy approval
- pending order creation

## Allowed Future Changes

Only these are allowed without reopening architecture refactor:

- bugfix
- test hardening
- docs update
- new operator
- performance benchmark
- native kernel optimization
- runtime adapter improvement

## Changes Requiring New Design Proposal

- changing public runtime API
- changing `evaluate`/`evaluate_many` behavior
- changing planner route semantics
- changing lifecycle/drop semantics
- changing DAG/CSE materialization semantics
- changing profiling schema
- adding direct order/trading functionality
- making Factor Engine depend on trading-system

## Next Phase

Move to trading-system:

Phase TS-1 Trading-System Factor Runtime Adapter

Goal:

trading-system calls Factor Engine Runtime API and receives latest factor
results.
