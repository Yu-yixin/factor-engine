# Execution Path Split Readiness

This document records the readiness state before splitting core executor paths. It is not permission to rewrite execution semantics.

## Completed Before Path Split

- `executor_utils.py` extracted for temporary naming and literal/window validation helpers.
- `execution_profiling.py` extracted for profiling schema constants and event/detail builders.
- `execution_ordering.py` extracted for prepared-frame construction, ordering column validation, row-index naming, and restore helpers.
- `execution_output.py` extracted for output-column restore, final selection, ordered-output append, and duplicate-name guard helpers.

## Remaining Core Paths

- `row_aligned`
- `ordered`
- `materialized_ordered`
- `segmented`
- `positional/native`
- `dag_batch`
- lifecycle drop
- CSE/materialization

## Path Split Preconditions

Before entering execution-path split work, the repository must have:

- full pytest pass
- profiling tests pass
- ordered/time-series targeted tests pass
- `evaluate_many` targeted tests pass
- no public API change
- docs updated

## Recommended Path Split Order

1. row_aligned compiled path
2. ordered prepared path
3. output finalization integration
4. segmented path
5. positional/native path
6. DAG/CSE batch path
7. lifecycle/drop deeper split

## Do Not Touch First

- lifecycle drop
- DAG/CSE reuse
- materialized ordered nested path
- native fallback internals
