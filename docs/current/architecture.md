# Current Architecture Map

This document is a code-reading map for the current repository. It is not a refactoring proposal.

## Public Entry

The core public entry point is `FactorEngine` in `src/factor_engine/engine.py`.

The main public flow is:

1. `parse(expression)`
2. `validate(expression, df)`
3. `evaluate(expression, df, output_name="result")`
4. `evaluate_many(expressions, df, ...)`

## Main Modules

- `engine.py`: public API, cache ownership, expression compilation, batch orchestration, and handoff to planner/executor.
- `parser.py`: parser for the factor expression DSL.
- `lexer.py` and `tokens.py`: lexical tokenization support for the DSL.
- `validator.py`: semantic validation and execution profile inference.
- `planner.py`: route selection and batch planning for compiled, segmented, staged, materialized ordered, positional ordered, and table paths.
- `executor.py`: execution implementation for the routes planned by `planner.py`, including batch execution, staged/materialized paths, segmented handling, profiling hooks, DAG/CSE execution, lifecycle sweep behavior, and native positional integration points.
- `execution_row_aligned.py`: no-order row-aligned compiled expression application and simple batch `with_columns` helpers.
- `execution_ordered.py`: ordered row-aligned compiled expression application using prepared frames and original-order restoration.
- `executor_utils.py`: low-risk executor utility helpers for internal names and literal validation. This module must stay free of DataFrame execution, route decisions, lifecycle policy, profiling accounting, and native bridge behavior.
- `execution_ordering.py`: prepared-frame construction, row-index naming, ordering-column validation, and original-order restore helpers. This module owns the input ordering shell but not ordered expression evaluation.
- `execution_output.py`: output-column restore, final selection, append, and duplicate-name guard helpers. This module owns output assembly shell helpers but not expression evaluation, dispatch, lifecycle, or profiling accounting.
- `execution_profiling.py`: profiling schema constants and small event/detail builders used by executor profiling hooks. This module must not perform DataFrame execution, lifecycle decisions, route dispatch, or benchmark report changes.
- `registry.py`: function registry and operator/function metadata.
- `dag.py`: expression DAG identity, DAG building, shared-node handling, and node result store support.
- `lifecycle.py`: lifecycle mode normalization and candidate classification rules.
- `profiling.py`: profiling artifact types and writers, including stage lifecycle profiling.
- `stage_registry.py`: runtime registry for stage lifecycle tracking.
- `native_positional.py`: optional native positional kernel bridge and Python fallback integration.
- `workflow.py`: file-oriented research workflow helpers around `FactorEngine`.

## Current Boundary Notes

`executor.py` is large and carries multiple responsibilities today. That is an observed fact, not an instruction to rewrite it in one pass.

Phase 3 refactoring must remain incremental. The current extractions include pure helpers in `executor_utils.py`, row-aligned compiled helpers in `execution_row_aligned.py`, ordered compiled helpers in `execution_ordered.py`, profiling event/detail builders in `execution_profiling.py`, prepared-frame/order helpers in `execution_ordering.py`, and output assembly shell helpers in `execution_output.py`; public execution behavior still belongs to `executor.py`. Future refactoring must start from stable tests and the invariants in [invariants.md](invariants.md).

The next execution-path split readiness gate is tracked in [execution_path_split_readiness.md](execution_path_split_readiness.md).
