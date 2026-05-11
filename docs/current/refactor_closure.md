# Refactor Closure

## Scope

Phase 3 refactor line is closed.

## Completed

- `executor_utils.py`
- `execution_profiling.py`
- `execution_ordering.py`
- `execution_output.py`
- `execution_row_aligned.py`
- `execution_ordered.py`
- `execution_materialized.py`
- `execution_segmented.py`
- `execution_positional.py`
- `execution_dag.py`
- `execution_cse.py`
- `execution_materialization.py`
- `execution_lifecycle.py`

## Executor Role

`executor.py` is now the execution coordinator/facade.

It owns:

- public `evaluate` / `evaluate_many`
- route dispatch
- high-level orchestration
- compatibility wrappers
- planner handoff

It should not regain:

- profiling detail construction
- ordering shell helpers
- output assembly helpers
- row-aligned execution internals
- ordered execution internals
- segmented execution internals
- positional/native shell internals
- DAG/CSE helper internals
- lifecycle integration helper internals

## Public API Stability

Public API remains:

- `FactorEngine.parse`
- `FactorEngine.validate`
- `FactorEngine.evaluate`
- `FactorEngine.evaluate_many`

## Not Claimed

This does not claim:

- performance optimality
- final DAG/CSE optimization
- final runtime/API design
- trading-system integration
- real-time market-data support

## Next Phase

Next phase:

Phase 4.0 Runtime API

Goal:

Create a stable external calling layer so trading-system can call Factor Engine without touching executor/planner internals.
