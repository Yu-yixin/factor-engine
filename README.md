# Factor Engine

Factor Engine is a correctness-first factor expression engine built on Python and Polars. It parses a factor DSL, validates expression semantics before execution, plans execution routes, and evaluates factors on DataFrames with explicit behavior around ordering, grouping, materialization, and lifecycle.

This repository is optimized for research and engine evolution, not for packaging polish or benchmark marketing. DSL semantics, planner contracts, lifecycle boundaries, and materialization behavior are treated as stability-sensitive.

## What This Repository Provides

- A parser and validator for a factor DSL.
- A `FactorEngine` API for single-expression and batch evaluation.
- Execution paths covering pointwise, cross-sectional, time-series, segmented, and table-style expressions.
- Planner and executor internals with correctness-oriented docs and tests.
- Workflow scripts for batch factor evaluation from YAML or JSON inputs.
- Benchmarks and profiling reports with archived evidence.

## Core Principles

- Correctness first over speed claims or convenience.
- No silent DSL semantic changes.
- No silent lifecycle or planner contract changes.
- Materialization semantics must be explicit.
- Performance claims must be backed by reproducible artifacts.

## Expression Families

- Pointwise: `close - open`
- Cross-sectional: `demean(close)`, `rank(close, pct=true)`
- Grouped cross-sectional: `group_rank(close, industry, pct=true)`
- Time-series: `delta(close, 1)`, `ts_rank(close, 20, pct=true)`
- Segmented: `seg_mean(close, 3)`, `seglen_sum(close, [3, 5, 2])`
- Table/output-expanding: `fft(...)`

Example composed expression:

```text
where(not is_null(close), clip(ts_mean(close, 5), 0, 100), 0)
```

## Quick Start

Factor Engine currently runs as a source-tree project. The simplest workflow is to install dependencies locally and run with `PYTHONPATH=src`.

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install polars pytest ruff
$env:PYTHONPATH="src"
py -m pytest -q
```

### Bash

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install polars pytest ruff
PYTHONPATH=src python3 -m pytest -q
```

If your shell or WSL environment has trouble with pytest output capture, retry with:

```bash
PYTHONPATH=src python3 -m pytest -q -s
```

## Minimal Example

```python
import polars as pl

from factor_engine.engine import FactorEngine

df = pl.DataFrame(
    {
        "time": [1, 2, 3],
        "code": ["A", "A", "A"],
        "close": [10.0, 20.0, 30.0],
        "open": [9.0, 18.0, 29.0],
    }
)

engine = FactorEngine()

single = engine.evaluate("delta(close, 1)", df)
batch = engine.evaluate_many(
    [
        ("spread", "close - open"),
        ("ts_rank_3", "ts_rank(close, 3, pct=true)"),
    ],
    df,
)

print(single)
print(batch)
```

## Batch Workflow Example

```powershell
$env:PYTHONPATH="src"
py scripts/workflow/file_batch_workflow.py input.parquet expressions.yaml --output result.parquet
```

The workflow layer also supports JSON/YAML expression batches, strict mode, `continue-on-error`, and run-summary outputs. See [docs/workflow.md](docs/workflow.md).

## Public API

`FactorEngine` is the main user-facing entry point.

- `parse(expression)`
- `validate(expression, df)`
- `evaluate(expression, df, output_name="result")`
- `evaluate_many(expressions, df)`

## Testing And Validation

Default test command:

```bash
PYTHONPATH=src python3 -m pytest -q
```

Representative checks:

- Full test suite: `PYTHONPATH=src python3 -m pytest -q`
- Ruff: `.venv/Scripts/python -m ruff check` or `python3 -m ruff check`
- Example smoke: `PYTHONPATH=src python3 examples/demo.py`

Benchmark and profiling work should be treated separately from correctness validation. See [docs/current/test_policy.md](docs/current/test_policy.md) and [docs/current/benchmark_policy.md](docs/current/benchmark_policy.md).

## Data And Artifact Boundaries

This repository intentionally does not track large runtime data, parquet outputs, temporary profiling traces, or local benchmark dumps.

- `data/` is a boundary marker, not a checked-in dataset.
- `outputs/` is for local runtime outputs only.
- `artifacts/` is for local benchmark/profiling storage.
- Real, private, or large benchmark datasets should live outside the repository root.

If you need local benchmark data, keep it in an external directory and pass the path explicitly to benchmark or workflow scripts.

## Repository Map

- `src/factor_engine/`: engine, parser, validator, planner, executor, runtime modules.
- `tests/`: unit, integration, workflow, perf, and profiling tests.
- `examples/`: small usage examples.
- `scripts/`: workflow and maintenance entry points.
- `benchmarks/`: benchmark scripts, reports, and archived evidence.
- `docs/`: current behavior, language rules, design notes, benchmark policy, and historical context.
- `data/`, `outputs/`, `artifacts/`: local-only boundaries for datasets and generated outputs.

## Recommended Reading

Start here if you are changing engine behavior:

1. [docs/current/README.md](docs/current/README.md)
2. [docs/current/architecture.md](docs/current/architecture.md)
3. [docs/current/invariants.md](docs/current/invariants.md)
4. [docs/current/repository_rules.md](docs/current/repository_rules.md)
5. [docs/current/test_policy.md](docs/current/test_policy.md)

Language and execution references:

- [docs/language.md](docs/language.md)
- [docs/functions.md](docs/functions.md)
- [docs/errors.md](docs/errors.md)
- [docs/workflow.md](docs/workflow.md)
- [docs/execution_planning_optimization.md](docs/execution_planning_optimization.md)
- [docs/stage_lifecycle.md](docs/stage_lifecycle.md)
- [docs/dag_cse.md](docs/dag_cse.md)

## Current Boundaries

- String literals are not supported.
- `evaluate_many()` accepts column-level expressions only.
- Workflow file input uses a fixed YAML/JSON schema.
- Caching and reuse semantics are explicit and documented, not “best effort”.
- Signals intended for trading decisions usually need explicit lagging, for example `delay(signal, 1)`.

## Repository Status

The repository contains both current truth documents and historical design/benchmark records. Historical material is useful context, but current behavior is governed by `docs/current/`.
