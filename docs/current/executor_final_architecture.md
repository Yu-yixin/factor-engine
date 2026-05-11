# Executor Final Architecture

This document describes the Phase 3.15 executor boundary after the DAG/CSE and lifecycle split. It is a map of current ownership, not a runtime/API design.

## What `executor.py` Owns

- Public `Executor.evaluate`, `evaluate_compiled`, `evaluate_many`, and planned/batch handoff.
- Route dispatch from planner output to execution modules.
- Compatibility wrappers for private helpers that tests and existing scripts may still reference.
- The high-level ordered batch coordinator, including the sequencing of compiled, staged, positional, materialized, DAG/CSE, lifecycle, profiling, restore, and final append steps.
- Planner handoff and validation fallback for direct `Executor` use.

## Execution Modules

- `executor_utils.py`: pure naming and literal/window validation helpers.
- `execution_row_aligned.py`: no-order row-aligned compiled expression application.
- `execution_ordered.py`: ordered row-aligned compiled expression application.
- `execution_materialized.py`: staged/materialized ordered orchestration shells.
- `execution_materialization.py`: materialized consumer-count and recomputation guardrail summary helpers.
- `execution_segmented.py`: segmented view preparation and segmented output restore shell.
- `execution_positional.py`: positional ordered orchestration, native bridge shell, and Python fallback scan.
- `execution_dag.py`: DAG identity, materialized-node rewrite/count helpers, planned consumer counters, and DAG execution context initialization.
- `execution_cse.py`: shared DAG-node materialization shell and CSE read accounting.
- `execution_lifecycle.py`: executor lifecycle integration helpers for trace events, drop revalidation, nested-drop order checks, and step-model assertions.
- `execution_ordering.py`: prepared-frame construction, row-index naming, and order restore helpers.
- `execution_output.py`: final output restore, selection, append, and duplicate guard helpers.
- `execution_profiling.py`: profiling schema constants and event/detail builders.

## Boundaries That Must Not Be Crossed Casually

- Execution modules must not change planner route semantics.
- Lifecycle policy remains in `lifecycle.py`; `execution_lifecycle.py` only adapts executor state to that policy.
- Native fallback remains optional and must not become a hard dependency.
- Profiling and benchmark field names remain schema-compatible.
- Materialization boundaries must not be bypassed by convenience rewrites.
- DAG identity and planner canonicalization remain compatibility-sensitive.

## Future Runtime/API Guidance

Runtime/API integration should call the stable public API:

- `FactorEngine`
- documented workflow helpers
- future runtime facade once introduced

Trading-system integration should not call:

- private `Executor._*` methods
- `execution_*.py` helper modules directly
- planner internals
- lifecycle/drop internals
- profiling artifact writers as a control plane

The next API layer should wrap `FactorEngine` rather than reaching into execution modules.
