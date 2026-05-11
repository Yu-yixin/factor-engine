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
- `registry.py`: function registry and operator/function metadata.
- `dag.py`: expression DAG identity, DAG building, shared-node handling, and node result store support.
- `lifecycle.py`: lifecycle mode normalization and candidate classification rules.
- `profiling.py`: profiling artifact types and writers, including stage lifecycle profiling.
- `stage_registry.py`: runtime registry for stage lifecycle tracking.
- `native_positional.py`: optional native positional kernel bridge and Python fallback integration.
- `workflow.py`: file-oriented research workflow helpers around `FactorEngine`.

## Current Boundary Notes

`executor.py` is large and carries multiple responsibilities today. That is an observed fact, not an instruction to split it during Phase 1.

Phase 1 does not refactor `executor.py`, does not move core source files, and does not change public behavior. Future refactoring must start from stable tests and the invariants in [invariants.md](invariants.md).

