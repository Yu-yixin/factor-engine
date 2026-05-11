# Pre-DAG Refactor Closure

## Completed Execution Modules

- `execution_row_aligned.py`
- `execution_ordered.py`
- `execution_materialized.py`
- `execution_segmented.py`
- `execution_positional.py`
- `execution_ordering.py`
- `execution_output.py`
- `execution_profiling.py`
- `executor_utils.py`

## Executor Role After Split

`executor.py` now acts as coordinator/facade for:

- public `evaluate` / `evaluate_many`
- route dispatch
- high-level batch orchestration
- DAG/CSE and lifecycle integration not yet split
- compatibility wrappers used by tests and existing scripts

## Still Not Split

- DAG/CSE batch reuse
- lifecycle deep drop
- materialization candidate planning
- node store / consumer count
- executor-native reuse

## Ready For Next Stage

Next stage may start:

- Phase 4 Runtime/API
- Phase 3.10 DAG/CSE refactor

Recommended:

Start Runtime/API first if trading-system integration is the priority.
