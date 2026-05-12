# Factor Engine Performance & Memory Self-Audit

Date: 2026-05-12

Scope: read-only audit of current implementation, tests, docs, benchmark scripts, and existing benchmark/profiling artifacts. Production code and tests were not changed.

## Executive Summary

The current engine already has a mature ordered-batch execution shell: `evaluate_many()` buckets compiled no-time-order work separately from ordered work, builds one prepared `[code, time]` sorted frame per ordered executor instance, supports DAG/CSE materialization for shared expensive nodes, tracks lifecycle and memory events, and has a native Rust/PyO3 positional kernel for root `argmax` / `argmin`.

The strongest optimization evidence is for:

- prepared-frame reuse inside an ordered batch (`src/factor_engine/execution_ordering.py`, `src/factor_engine/executor.py`)
- executor-native DAG/CSE reuse for materialized shared nodes (`src/factor_engine/dag.py`, `src/factor_engine/execution_cse.py`, `src/factor_engine/execution_dag.py`)
- stage/helper column drop via frame projection/drop (`src/factor_engine/stage_registry.py`, `src/factor_engine/executor.py`)
- delayed output attach modes (`src/factor_engine/lifecycle.py`, `src/factor_engine/executor.py`)
- native/low-copy positional `argmax` / `argmin` (`src/factor_engine/native_positional.py`, `native/factor_engine_native/src/lib.rs`)

The largest likely bottleneck remains ordinary Polars rolling/window execution (`ts_mean`, `ts_std`, `ts_sum`, `ts_min`, `ts_max`, `ts_rank`, `corr`, `cov`, `skew`, `kurt`) and final ordered expression evaluation/restore on wide/deep batches. This is a HYPOTHESIS where no current per-operator rolling-time benchmark isolates each rolling family except positional `argmax` / `argmin`.

## A. Repository Map

| Area | Path | Current Role | Confidence |
| --- | --- | --- | --- |
| Parser / AST | `src/factor_engine/ast_nodes.py`, `src/factor_engine/lexer.py`, `src/factor_engine/parser.py`, `src/factor_engine/tokens.py` | Defines expression nodes, tokenization, and parsing used by `FactorEngine.parse()` and compile caches. | HIGH |
| Validator | `src/factor_engine/validator.py`, `src/factor_engine/runtime/validation.py`, `src/factor_engine/runtime/schemas.py` | Validates DSL expressions and runtime schemas; emits `ValidationResult` / `ExecutionProfile`. | HIGH |
| Execution planner | `src/factor_engine/planner.py`, `src/factor_engine/physical_properties.py` | Chooses routes: `compiled`, `segmented`, `staged`, `materialized_ordered`, `positional_ordered`, `table`; builds batch plans and DAGs. | HIGH |
| Executor | `src/factor_engine/executor.py`, `src/factor_engine/execution_*.py` | Public execution coordinator plus route-specific helpers for ordered, row-aligned, segmented, positional, materialized, output restore, lifecycle, profiling. | HIGH |
| Operator registry | `src/factor_engine/registry.py`, `expressions.yaml`, `docs/functions.md` | Declares function specs, execution kind, window kind, order/group needs, materialized-input support, aliases, and audit entries. | HIGH |
| Lifecycle | `src/factor_engine/lifecycle.py`, `src/factor_engine/stage_registry.py`, `docs/stage_lifecycle.md` | Normalizes lifecycle modes, classifies drop candidates, manages stage records, planned consumers, and physical stage-column sweeps. | HIGH |
| Profiling | `src/factor_engine/profiling.py`, `src/factor_engine/execution_profiling.py`, `docs/current/profiling_schema.md` | Defines run/batch/stage/output/native-buffer/positional-phase details and persists JSONL/CSV/Markdown reports. | HIGH |
| Benchmarks | `benchmarks/scripts/*.py`, `benchmarks/reports/*.md`, `benchmarks/archive/**`, `docs/benchmark/*.md` | Synthetic and real-data timing/profiling scripts plus generated benchmark reports and archives. | HIGH |
| Native Rust kernels | `native/factor_engine_native/src/lib.rs`, `src/factor_engine/native_positional.py`, `docs/native_positional_kernel.md` | Rust/PyO3 grouped positional extreme kernel and Python bridge/fallback for `argmax` / `argmin`. | HIGH |
| Tests | `tests/unit`, `tests/integration`, `tests/profiling`, `tests/perf`, `tests/native/.gitkeep` | Unit/integration/profiling/perf guardrails; native test is conditional on extension availability. | HIGH |

## B. Runtime Route Audit

| Route | Entry Function | Supported Operator Families | Row Order | Sorting | Execution Style | Known Bottlenecks |
| --- | --- | --- | --- | --- | --- | --- |
| `compiled` / row-aligned no-time-order | `Executor.evaluate_many_compiled()` -> `_evaluate_many_row_aligned_no_time_order()` | Pointwise, cross-sectional/grouped operators that do not require `[code,time]` ordering. | Preserved by direct `with_columns`. | No. | Polars expressions. | UNKNOWN; no recent dedicated no-time-order microprofile found. |
| `compiled` / row-aligned time-ordered | `Executor.evaluate_many_compiled()` -> `_evaluate_many_row_aligned_time_ordered()` | Time-series expressions that can compile directly to Polars exprs. | Restored through row index. | Yes, via prepared frame. | Polars expressions over sorted frame. | HYPOTHESIS: repeated Polars rolling expr evaluation and final restore sort can dominate large batches. |
| `segmented` | `_evaluate_many_segmented_columns()` | `seg_*`, `seglen_*` families. | Restored through row index. | Yes, shares prepared frame; per segment spec view cached in `PreparedFrame.segmented_views`. | Polars expressions over segment-id helper columns. | Existing segmented benchmarks measure sort, segment prep, aggregation, restore; cross-spec reuse is intentionally limited. |
| `staged` | `_evaluate_many_ordered_batch_plan()` and `_materialize_staged_chain_on_sorted_df()` | Cross-sectional chains such as ordered source -> rank/demean/zscore/scale steps. | Restored through row index. | Yes. | Staged materialization into helper columns. | Helper-column width and stage lifecycle complexity; mitigated by sweep/drop modes. |
| `materialized_ordered` | `_materialize_ordered_plan_on_sorted_df()` | Ordered roots with materialized child inputs: `ts_*`, `corr`, `cov`, `skew`, `kurt`, and `argmax`/`argmin` when child materialization is needed. | Restored through row index. | Yes. | Child stages plus Polars rolling root or positional kernel for argmax/argmin. | Ordinary rolling roots rely on Polars; no native acceleration found outside argmax/argmin. |
| `positional_ordered` | `_materialize_positional_call_on_sorted_df()` -> `_attach_positional_kernel_from_stage()` | Root `argmax(x,n)` and `argmin(x,n)`. | Restored through row index. | Yes. | Native Rust/PyO3 kernel if env/extension available, else Python deque fallback. | Python fallback converts series to lists and scans in Python; native path still builds group metadata and output buffers. |
| `table` | `_evaluate_table()` | `fft` backend only from observed code. | Table output, not row-aligned column output. | Depends on backend. | Dedicated backend (`fourier_transform_frame`). | Not batchable by `evaluate_many()`; outside main ordered batch path. |

## C. Sorting / Prepared Frame Audit

- Sorting happens in `build_prepared_frame()`: `df.with_row_index(row_index_name).sort([code_col, time_col])`.
- `Executor._get_prepared_frame()` caches a `PreparedFrame` on the executor instance, so a single ordered-batch executor sorts once and reuses that sorted frame.
- `evaluate_many()` may create more than one executor: one for compiled no-time-order items, one for planned ordered items, and nested executor instances in `evaluate_many_planned()`. The ordered planned batch itself uses one prepared frame.
- Row-order restore is shared through `restore_selected_columns()`, `restore_output_columns()`, and `restore_mapped_output_columns()`, each sorting by `row_index_name` and then dropping it.
- `[code, time]` ordering assumptions are explicit in registry contracts (`requires_partition_by=("$code",)`, `requires_order_by=("$time",)`) and in `docs/functions.md` / `docs/execution_planning_optimization.md`.
- Possible redundant sorting points:
  - Single `evaluate()` calls each create their own executor and prepared frame.
  - Mixed `evaluate_many()` with segmented plus ordered items can run segmented first, then ordered batch on the result frame; each executor has its own prepared-frame cache.
  - Restore does a `sort(row_index_name)` per ordered output assembly.

## D. DAG / CSE Audit

- Canonical node identity exists in `ExpressionDagBuilder._visit()`: identities include node type, canonicalized literals, canonical function name/kwargs behavior in planner keys, and route-sensitive function context for DAG calls.
- Repeated subexpressions are detected by `_node_ids_by_identity`; repeated visits increment `occurrence_count`.
- Planner CSE defaults to `baseline`; `expanded_repeated_family` exists for selected repeated-family identities (`ts_rank`, `ts_mean`) and records an audit structure.
- Executor reuse exists, not just structural inspection:
  - `materialize_shared_dag_nodes_on_sorted_df()` materializes selected DAG nodes into helper columns.
  - `rewrite_expr_with_materialized_nodes()` rewrites downstream ASTs to `VariableNode(materialized_column)`.
  - `NodeResultStore` tracks compute/write/read/reuse/drop stats.
- Compiled/native outputs can be reused when represented as materialized helper columns. Native-heavy nodes are classified separately; active drop remains guarded/observable.
- Tests: `tests/integration/test_dag_cse.py`, `tests/unit/test_execution_dag.py`, `tests/unit/test_execution_cse.py`, `tests/profiling/test_stage_lifecycle.py`.
- Missing/limited cases:
  - Expanded CSE is explicitly narrow.
  - Fusion mode exists (`unary_chain_fusion`) but is not a broad optimizer.
  - Some compiled fallback heavy occurrences are counted rather than fully eliminated.

## E. Lifecycle and Memory Audit

The report distinguishes four different things:

| Concept | Current Evidence | Status |
| --- | --- | --- |
| Logical node-store drop | `NodeResultStore.record_planned_consumption()` pops entries when ref count reaches zero and records `dropped_at_step`. | EXISTS |
| Polars frame column removal | `StageRegistry.sweep_drop_candidates()` returns `frame.drop(drop_columns)`; helper lifecycle uses `frame.select(remaining_columns)`. | EXISTS |
| Native buffer release | `attach_positional_kernel_from_stage()` registers native buffer creation/attach, deletes `result`, and marks release immediately after attach. | EXISTS as logical/profiling event; actual allocator release is not guaranteed. |
| Observed process RSS decrease | `current_rss_mb()` is recorded and peak RSS is persisted. Existing reports show RSS can increase even when frame width drops. | PARTIAL; process RSS decrease is not guaranteed or proven. |

Findings:

- `last_use` / consumer counts exist in both `StageRegistry` and DAG lifecycle plans. Stage registry tracks planned and actual consumer counts; DAG lifecycle plans include producer/consumer/last-use/ref-count/drop-candidate fields.
- What gets dropped:
  - stage cache entries are removed when stage columns are swept
  - registry records are marked dead/dropped
  - Polars frame columns are physically absent from the returned projected/dropped frame
  - node-store entries can be popped independently of frame columns
- Output columns can be delayed. `OutputAttachMode` supports `materialize`, `finalize_select`, and `last_use_select`; finalize/last-use select builds `ordered_outputs_with_row` instead of growing the working frame with user outputs.
- Peak frame width tracking exists (`peak_frame_col_count`, `peak_stage_col_count`, `peak_output_col_count`).
- RSS tracking exists (`rss_before_mb`, `rss_after_mb`, `peak_rss_mb`, memory events), but RSS is observational and allocator-dependent.

Existing benchmark evidence:

- `benchmarks/reports/stage_lifecycle.md` shows V2 lower peak columns and zero alive stages at end for synthetic workloads, but V2 RSS is higher in the listed synthetic run.
- `benchmarks/archive/m1_verify_data_parquet_20260417_030844/comparison.md` shows frame-width reductions in some workloads, but mixed RSS deltas, including increases.

## F. Rolling / Window Bottleneck Audit

| Operator | Implementation Path | Backend | Likely Complexity | Null Handling | Benchmark Coverage | Priority |
| --- | --- | --- | --- | --- | --- | --- |
| `ts_mean` | `_compile_ts_mean()` / `_build_materialized_single_input_ordered_expr()` | Polars `rolling_mean(...).over(code)` | Polars-dependent, likely O(n) per group/window implementation | `min_samples=1`; Polars semantics | Covered by tests and CSE/lifecycle workloads, not isolated per-op benchmark | HIGH |
| `ts_std` | `_compile_ts_std()` | Polars `rolling_std` | Polars-dependent | `min_samples=2` | Tests/ordered audit; no isolated speed profile found | HIGH |
| `ts_sum` | `_compile_ts_sum()` | Polars `rolling_sum` | Polars-dependent | `min_samples=1` | Tests/benchmarks indirectly | MEDIUM |
| `ts_min` | `_compile_ts_min()` | Polars `rolling_min` | Polars-dependent | `min_samples=1` | Tests/ordered audit | MEDIUM |
| `ts_max` | `_compile_ts_max()` | Polars `rolling_max` | Polars-dependent | `min_samples=1` | Tests/ordered audit | MEDIUM |
| `ts_rank` | `_compile_ts_rank()` | Polars `rolling_rank`; pct divides by rolling non-null count | HYPOTHESIS: heavier than simple reducers | `min_samples=1`, pct count excludes nulls | CSE/lifecycle workloads, tests | HIGH |
| `argmax` | Root route uses native/Python grouped deque; compiled fallback uses short-window shifts or list fallback | Native/Python/Polars fallback | Dedicated deque O(n); list fallback O(n*w) style | Ignores nulls; all-null windows -> null; nearest tie wins | Strong dedicated positional benchmarks | LOWER for root; HIGH for composed fallback risk |
| `argmin` | Same as `argmax` | Native/Python/Polars fallback | Same | Same | Strong dedicated positional benchmarks | LOWER for root; HIGH for composed fallback risk |
| `corr` | `_compile_corr()` / materialized ordered root | Polars `rolling_corr(...).over(code)` | Polars-dependent, pairwise rolling | `min_samples=2` | Unit tests and split-step correctness | HIGH |
| `cov` | `_compile_cov()` / materialized ordered root | Polars `rolling_cov(...).over(code)` | Polars-dependent, pairwise rolling | `min_samples=2` | Unit tests and split-step correctness | HIGH |
| `skew` | `_compile_skew()` | Polars `rolling_skew` | HYPOTHESIS: expensive | `min_samples=3` | Unit tests | MEDIUM |
| `kurt` | `_compile_kurt()` | Polars `rolling_kurtosis` | HYPOTHESIS: expensive | `min_samples=4`, fisher/bias set | Unit tests | MEDIUM |

## G. Native Kernel Audit

- Native module path: `native/factor_engine_native/src/lib.rs`.
- Python bridge: `src/factor_engine/native_positional.py`.
- Exported functions:
  - `grouped_positional_extreme`
  - `grouped_positional_extreme_buffers`
- Operators accelerated: `argmax`, `argmin` only.
- Copy/zero-copy/low-copy behavior:
  - Low-copy bridge reads Polars private buffers (`_get_buffers`, `_get_buffer_info`) and passes pointers to Rust.
  - Rust returns `PyBytes` for data/validity; Python creates a Polars nullable `Int64` series from buffers.
  - This is low-copy for input metadata and native output construction, but output bytes are still produced by Rust and wrapped for Polars.
- GIL behavior: Rust scan uses `py.detach(...)`, so the CPU scan runs outside the GIL.
- Parallelism: low-copy buffer path supports Rayon group-level parallelism controlled by `FACTOR_ENGINE_POSITIONAL_PARALLEL`.
- Fallback behavior:
  - If native env flag is not set, import fails, or native execution fails, Python falls back to grouped deque scan.
  - If low-copy path fails, it tries object bridge before Python fallback.
- Benchmark evidence:
  - `benchmarks/reports/positional_rolling.md`: dedicated kernel beats list fallback by 2.78x to 31.92x on 60k rows.
  - `benchmarks/archive/positional_phases_native_lowcopy_parallel_500k/summary.json`: native low-copy parallel path used for 500k-row runs; positional group scan totals are recorded.

## H. Materialization Strategy Audit

- Current materialization rules are DAG-driven:
  - cost classes and materialization fields live in `DagNode`
  - default policy is `reuse_ge_2`
  - guarded mode `reuse_ge_3_guarded` exists
  - `materialized_consumer_count()` uses `max(occurrence_count, len(consumers) + len(output_names))`
- Cheap vs expensive nodes are separated via `NodeCostClass` and `is_expensive`. Time-series/window nodes are generally treated as expensive/shared-heavy by lifecycle class.
- `consumer_count` and occurrence count are used by planner/runtime policies.
- Memory penalty is partially considered via bytes estimates and lifecycle/profiling savings, not by a full cost model during materialization selection. Mark as PARTIAL.
- Rejected materialization candidates are observable through guardrail counters (`recomputation_guardrail_blocked_count`, `recomputation_expansion_actual_delta`) and DAG inspection fields. No general "all rejected candidates" log was found. Mark as PARTIAL.
- Risk of over-materialization:
  - `reuse_ge_2` can materialize repeated expensive nodes even when the helper column increases frame width.
  - Frame projection and lifecycle drop mitigate this after materialization, but do not prevent initial peak.
  - UNKNOWN whether current policy is globally optimal for mixed cheap/expensive workloads.

## I. Profiling and Benchmark Audit

| Script / Report | Measures | Time | Memory | Route Breakdown | Sorting | Rolling | Native | Attach | A/B | Reproducibility |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `benchmarks/scripts/benchmark.py` | Basic synthetic expressions | Yes | No | No | No | Indirect | No | No | No | Simple, limited |
| `benchmark_real_workload.py` | Real-ish workload, evaluate vs evaluate_many, workflow/report, stage timers | Yes | Limited | Yes | Yes via monkeypatch timer | Yes bucket | No | IO only | Some | Good script, not persisted as profiling schema |
| `benchmark_positional_rolling.py` / `benchmarks/reports/positional_rolling.md` | list fallback vs dedicated positional kernel | Yes | No | Positional only | Included in helper path | Positional only | No Rust env split in report | No | Yes | Good for positional |
| `benchmark_positional_phases.py` | Positional phase details on real/synthetic data | Yes | Peak RSS/native bytes | Ordered batch | prepare_sort recorded | Positional only | Yes | Yes | Expr-count matrix | Good |
| `benchmark_stage_lifecycle.py` / report | Stage lifecycle V1 vs V2 | Yes | Peak RSS, peak cols | Ordered batch | prepare_sort in artifacts | Indirect | Indirect | Output retention | Yes | Good synthetic |
| `benchmark_stage_lifecycle_real_smoke.py` | Real-data V1/V2 lifecycle smoke | Yes | Peak RSS/cols | Ordered batch | In artifacts | Indirect | Indirect | Indirect | Yes | Good if data present |
| `benchmark_m1_memory_model.py` | Output retention, frame pressure, native buffer pressure | Yes | RSS/cols/native bytes | DAG/stage fields | In artifacts | Indirect | Yes | Yes | lifecycle flag | Good |
| `benchmark_r4_executor_reuse.py` | DAG/CSE executor reuse, native-heavy probes | Yes | RSS/bytes estimates | Strong DAG/CSE breakdown | In artifacts | Heavy expressions | Native-heavy observability | Finalize/append | CSE on/off | Good |
| `benchmark_m2_5_lifecycle_freeze.py` | lifecycle freeze/value/rejection cases | Yes | lifecycle/helper memory fields | Lifecycle-specific | In artifacts | Indirect | Native pinned cases | Indirect | Mode comparisons | Good |
| `benchmark_m3_auto_pipeline.py` | candidate optimization pipeline | Yes | aggregate memory metrics | Candidate/baseline | In artifacts | workload-dependent | workload-dependent | output_attach modes | Yes | Good but complex |

Missing benchmark cases:

- Per-operator rolling benchmarks for `ts_mean`, `ts_std`, `ts_sum`, `ts_min`, `ts_max`, `ts_rank`, `corr`, `cov`, `skew`, `kurt`.
- A/B for output attach modes across all ordered route families in a single reproducible matrix.
- Cold-cache vs warm-cache planning/compile benchmark.
- Explicit prepared-frame reuse benchmark for mixed segmented + ordered batches.
- RSS interpretation benchmark that separates Polars allocation, Python allocator, and OS RSS retention. Current RSS is useful but not sufficient to claim released memory returned to OS.

## J. Correctness Guardrails

| Guardrail | Evidence |
| --- | --- |
| Row order preservation | `tests/unit/test_execution_ordering.py`, `tests/unit/test_execution_ordered.py`, `tests/unit/test_execution_row_aligned.py`, `tests/unit/test_execution_materialized.py`, `tests/unit/test_execution_segmented.py` |
| Null semantics | `tests/unit/test_execution_row_aligned.py`, `tests/unit/test_corr.py`, `tests/unit/test_cov.py`, `tests/unit/test_skew.py`, `tests/unit/test_kurt.py`, operator-specific tests |
| Rolling window boundaries | `tests/unit/test_corr.py`, `tests/unit/test_cov.py`, `tests/unit/test_skew.py`, `tests/unit/test_kurt.py`, `tests/integration/test_ordered_audit.py`, `tests/integration/test_engine_new_functions.py` |
| Group boundaries | `tests/unit/test_execution_ordered.py`, `tests/integration/test_planner.py`, `tests/integration/test_engine.py` |
| Segmented boundaries | `tests/unit/test_execution_segmented.py`, `tests/integration/test_ordered_audit.py`, segmented benchmark spec-gate scripts |
| DAG/CSE correctness | `tests/integration/test_dag_cse.py`, `tests/unit/test_execution_dag.py`, `tests/unit/test_execution_cse.py` |
| Lifecycle correctness | `tests/profiling/test_stage_lifecycle.py`, `tests/unit/test_execution_lifecycle.py`, `tests/unit/test_execution_profiling.py` |
| Native fallback equivalence | Conditional `tests/profiling/test_stage_lifecycle.py::test_native_positional_kernel_matches_python_fallback`; skipped if native extension unavailable |

## K. Optimization Opportunity Ranking

| Rank | Opportunity | Speed Impact | Memory Impact | Risk | Evidence | Next Action |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Add isolated rolling operator benchmarks before changing rolling internals | HIGH expected decision value | MEDIUM | LOW | Ordinary rolling ops lack isolated timing; positional has strong benchmark evidence | Create `benchmark_rolling_operators.py` covering listed ops, windows, nulls, groups |
| 2 | Optimize `ts_rank`, `corr`, `cov` only if benchmark proves them dominant | HIGH HYPOTHESIS | MEDIUM | HIGH correctness risk | Current code uses Polars rolling; tests exist but no timing split | Benchmark first; then design native/proven-library path only for hottest op |
| 3 | Reduce redundant restore/sort cost in ordered batch finalization | MEDIUM | LOW | MEDIUM | Restore sorts by row index; profiling records restore/finalize times | Add benchmark column for restore sort time; only then evaluate alternatives |
| 4 | Strengthen prepared-frame reuse across segmented + ordered phases | MEDIUM | MEDIUM | MEDIUM | Multiple executor instances may sort separately in mixed plans | Add benchmark/profiling for mixed segmented+ordered batches; inspect repeated prepare_sort |
| 5 | Expand output attach/projection mode benchmark matrix | MEDIUM | HIGH | LOW-MEDIUM | Modes exist; M1/M3 reports show frame-width effects | Run matrix on real workloads with `materialize` vs `finalize_select` vs `last_use_select` |
| 6 | Improve RSS observability with allocator-aware metrics | LOW speed | HIGH insight | LOW | Existing RSS can increase despite column drops | Add optional memory profiler/allocator metrics; keep RSS claims conservative |
| 7 | Consider broader native kernels beyond positional | HIGH possible | UNKNOWN | HIGH | Native positional has evidence; ordinary rolling does not | Do not implement until per-op benchmark identifies one hot family |
| 8 | Broaden CSE beyond current expanded families | MEDIUM | MEDIUM | MEDIUM-HIGH | `expanded_repeated_family` is narrow by design | Use DAG inspection to find repeated misses before changing identity rules |
| 9 | Native-heavy active drop | LOW-MEDIUM | MEDIUM | HIGH | Native-heavy lifecycle is classified observable/candidate_future, not fully active | Do not touch until consumer semantics and buffer lifetime tests are stronger |

## L. Final Recommendation

1. What is already solid:
   - execution route separation and batch planning
   - prepared sorted frame reuse within an ordered batch
   - row-order restoration
   - DAG identity, repeated-subexpression detection, and executor-native reuse for selected materialized nodes
   - lifecycle/profiling observability
   - physical helper/stage column removal
   - native positional kernel path and Python fallback equivalence guardrails

2. What is probably a bottleneck:
   - HYPOTHESIS: ordinary Polars rolling/window operators, especially `ts_rank`, `corr`, `cov`, `ts_std`, `skew`, and `kurt`
   - HYPOTHESIS: final ordered expression evaluation and row-index restore sorting on large, wide batches
   - Python fallback for composed `argmax` / `argmin` cases that cannot use the root positional kernel

3. What is unknown due to missing measurement:
   - per-operator rolling cost ranking
   - whether process RSS drops after frame-column removal under realistic long-running workloads
   - whether mixed segmented + ordered batches repeat sorting enough to matter
   - cold-cache vs hot-cache planning/compile cost
   - full A/B matrix for output attach and projection modes

4. What should be optimized first:
   - Do not optimize code first. Add isolated benchmark coverage for rolling/window operators and restore/finalize timing. The first implementation target should be whichever operator is empirically hottest on real workloads.

5. What should not be touched yet:
   - native-heavy lifecycle active drop
   - broad CSE identity expansion
   - new Rust kernels for non-positional operators
   - allocator/RSS claims beyond observed metrics
   - production route refactors without benchmark evidence
