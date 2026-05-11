# Phase 3 Refactor Plan

Phase 3 reduces `src/factor_engine/executor.py` complexity without changing public behavior. The rule is: audit first, then extract one small reversible slice at a time.

## Current Hotspots

PowerShell line counts at Phase 3.0:

| File | Lines | Notes |
| --- | ---: | --- |
| `src/factor_engine/executor.py` | 4623 | Main complexity hotspot; owns execution orchestration, ordered paths, segmented paths, DAG/CSE, lifecycle hooks, profiling hooks, and many compile helpers. |
| `src/factor_engine/planner.py` | 744 | Route and staged/materialized planning. Important, but smaller and clearer than executor. |
| `src/factor_engine/lifecycle.py` | 301 | Lifecycle policy normalization and classification. Mostly policy helpers and enums. |
| `src/factor_engine/profiling.py` | 1330 | Profiling data models, writer, and report rendering. Large but already separated from executor. |

## Executor Responsibility Map

| Bucket | Current executor surface | First-move risk | Guardrails | Recommended phase |
| --- | --- | --- | --- | --- |
| A. Public orchestration | `evaluate`, `evaluate_many`, `evaluate_many_planned`, `evaluate_many_compiled`, route dispatch | High | Full test suite, public API compatibility, engine tests | Later; do not start here |
| B. Row-aligned compiled path | no-order compiled expressions, ordered row-aligned path, prepared frame reuse | High | ordered tests, `evaluate_many`, row restore tests | Phase 3.3+ |
| C. Staged/materialized ordered path | staged evaluation, materialized boundaries, nested ordered handling | High | planner, lifecycle, ordered audit, DAG/CSE tests | Later |
| D. Segmented path | segment views, segment specs, segmented operator execution | Medium/High | segmented integration tests and real benchmark smoke | Later; maybe after pure helpers |
| E. Positional ordered path | `argmax`/`argmin` distance, native bridge calls, Python fallback | High | native fallback smoke, profiling tests, ordered tests | Later |
| F. DAG/CSE/batch reuse | node store, materialization candidates, consumer counts, executor-native reuse | High | DAG/CSE tests, lifecycle tests, benchmark reports | Later |
| G. Lifecycle/drop | producer/consumer trace, first-wave/helper drop, drop miss, lifecycle summary | High | profiling and lifecycle tests | Later |
| H. Profiling/accounting | stage timing, memory events, native buffer details, output details | Medium | profiling tests, JSON field stability | Phase 3.2 candidate |
| I. Output assembly/finalization | restore order, append/select output columns, final frame construction | High | evaluate/evaluate_many integration tests | Later |
| J. Pure utility helpers | temporary helper names, literal validation, small naming/spec helpers | Low | unit tests plus full suite | Phase 3.1 first safe extraction |

## Dependency Map

`executor.py` imports:

- AST nodes from `ast_nodes.py`.
- DAG storage/building from `dag.py`.
- execution errors from `errors.py`.
- FFT table execution from `fourier.py`.
- lifecycle enums and policy helpers from `lifecycle.py`.
- plans from `planner.py`.
- profiling models/writer from `profiling.py`.
- optional native bridge from `native_positional.py`.
- registry metadata from `registry.py`.
- stage tracking from `stage_registry.py`.
- validation result/profile types from `validator.py`.
- `polars`, `time`, `deque`, `Sequence`, `dataclass`, and typing primitives.

Known direct dependents of `Executor`:

- `src/factor_engine/engine.py`
- `tests/integration/test_engine.py`
- `tests/integration/test_executor.py`
- `tests/integration/test_executor_new_functions.py`
- `tests/integration/test_dag_cse.py`
- `tests/integration/test_engine_new_functions.py`
- `tests/profiling/test_stage_lifecycle.py` imports `factor_engine.executor` for monkeypatching native/profile behavior.
- Benchmark scripts under `benchmarks/scripts/` directly instantiate `Executor`.

Known private-helper dependency:

- `tests/integration/test_executor_new_functions.py` directly calls `Executor._expect_positive_numeric_literal`. If literal helpers move, keep thin compatibility methods on `Executor`.

## Safe Extraction Candidates

Best first candidates are helpers that do not touch DataFrames, route selection, lifecycle state, profiling state, or native execution:

- `temporary_helper_name(base_name, existing_names, reserved=None)` extracted from `Executor._temporary_helper_name`.
- `expect_numeric_literal(expr, func_name)`.
- `expect_scalar_number(expr, func_name)`.
- `expect_positive_numeric_literal(expr, func_name)`.
- `expect_positive_integer_list_literal(expr, func_name)`.
- `expect_window_at_least(expr, func_name, minimum)`.

Possible later utility extraction, after tests prove the first extraction is stable:

- segmented spec-key collection helpers, if they can remain planner/registry-aware without pulling DataFrame logic.
- output-name selection helpers, if clearly isolated from final assembly.

## Unsafe To Touch First

Do not start Phase 3 with:

- `evaluate` / `evaluate_many`.
- ordered prepared-frame sorting and restore semantics.
- materialized ordered paths.
- lifecycle drop behavior.
- native bridge and fallback paths.
- DAG/CSE node store and materialization candidate logic.
- profiling JSON/report field names.
- segmented execution and segment-id construction.

These areas cross many invariants and need narrower tests before extraction.

## Proposed Refactor Sequence

1. Phase 3.1: create `src/factor_engine/executor_utils.py` and move pure utility helpers only. Keep `Executor` compatibility wrappers for any private helper already touched by tests. Completed first extraction: temporary helper naming and literal/window validation helpers.
2. Phase 3.2: isolate profiling/accounting helpers into `execution_profiling.py`, keeping field names and report structures unchanged. Completed first profiling boundary: schema constants plus memory/output/native-buffer/positional detail builders.
3. Phase 3.3: isolate prepared-frame/order helpers into `execution_ordering.py`, preserving row restoration semantics. Completed ordering boundary: row-index naming, ordering-column validation, prepared-frame construction, and restore helpers.
4. Phase 3.3B: isolate output assembly shell helpers into `execution_output.py`, preserving final column order, output names, and helper-column filtering. Completed output boundary: restore/select helpers and ordered-output append helpers.
5. Phase 3.4: isolate no-order row-aligned compiled helpers into `execution_row_aligned.py`, preserving simple `with_columns` behavior and output order.
6. Phase 3.5: isolate ordered row-aligned compiled helpers into `execution_ordered.py`, preserving prepared-frame usage and original-order restoration.
7. Phase 3.6: isolate staged/materialized ordered orchestration shells into `execution_materialized.py`, while leaving nested materialization internals in executor-owned callbacks.
8. Phase 3.7: isolate segmented view preparation and segmented execution shell helpers into `execution_segmented.py`, preserving segment semantics and output restoration.
9. Phase 3.8: isolate positional ordered orchestration and native bridge shell helpers into `execution_positional.py`, preserving Python fallback and native availability behavior.
10. Later: consider lifecycle and DAG/CSE modules only after targeted tests are stable.

## Test Guardrails

Every extraction must run:

```powershell
.venv\Scripts\Activate.ps1
$env:PYTHONPATH="src"
python -m pytest -q
python -m pytest tests/unit -q
python -m pytest tests/integration -q
```

Additional guardrails by area:

- Profiling extraction: `python -m pytest tests/profiling -q`.
- Native-adjacent changes: native fallback smoke plus profiling tests.
- Ordered changes: `python -m pytest -k "ordered or delay or ts_" -q`.
- Segmented changes: segmented integration tests plus benchmark script compile/start checks.

## Rollback Strategy

Each Phase 3 commit must be single-purpose and reversible with one commit revert.

- Do not mix behavior fixes with extraction.
- Do not rename public APIs during extraction.
- Keep compatibility wrappers when tests or scripts touch private helpers.
- If a test failure is not clearly a path/import issue, stop and revert the extraction instead of changing semantics.

## Execution Path Split Readiness

The current readiness gate for the next phase is tracked in [execution_path_split_readiness.md](execution_path_split_readiness.md). It lists the completed boundary extractions, remaining core paths, preconditions, and recommended split order.

## Pre-DAG Closure

The pre-DAG execution path split is closed in [pre_dag_refactor_closure.md](pre_dag_refactor_closure.md). DAG/CSE batch reuse, lifecycle deep drop, materialization candidate planning, node store / consumer count, and executor-native reuse remain intentionally unsplit.

## DAG/CSE Core Split

Phase 3.10 mapped the DAG/CSE refactor plan in [dag_cse_refactor_plan.md](dag_cse_refactor_plan.md). Phase 3.11 begins the core split with `execution_dag.py` for DAG identity, materialized-node rewrite/count helpers, planned consumer counters, and DAG execution context initialization.

Phase 3.12 isolates the shared-node CSE materialization shell in `execution_cse.py`, while keeping expression compilation, lifecycle classification, and stage registration behind executor callbacks.

Phase 3.13 isolates materialization boundary helpers in `execution_materialization.py`, including materialized consumer-count policy and recomputation guardrail runtime summaries. Planner route and materialized ordered semantics remain unchanged.

Phase 3.14 isolates executor lifecycle integration helpers in `execution_lifecycle.py`, while keeping lifecycle policy in `lifecycle.py` and preserving drop semantics.
