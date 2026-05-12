# Native corr/cov Shared-Moment Design

## Executive Summary

Phase-2 should focus on `corr` / `cov` shared rolling moments, not `argmax` / `argmin`.
The Phase-1.5 scale-up report shows `corr` as the clearest stable non-positional
large-scale bottleneck, and recommends "A. Start native/shared-moment design for
corr/cov". The same report explicitly shows `argmax` / `argmin` were measured on
`python_fallback`, with native available but not requested; that fallback result is
not evidence that the native positional path is slow.

Final decision: `READY_FOR_PROTOTYPE`, gated by golden tests that pin current
Polars semantics before any native route can be enabled by default.

## Current corr/cov Path

Files inspected:

- `src/factor_engine/ast_nodes.py`: `CallNode(name, args, kwargs)` represents
  parsed `corr(x, y, n)` / `cov(x, y, n)`.
- `src/factor_engine/parser.py`: `_parse_call()` canonicalizes function names via
  `canonical_function_name()`.
- `src/factor_engine/registry.py`: `corr` and `cov` are registered as three-arg
  numeric time-series functions requiring `$code` partition and `$time` order.
- `src/factor_engine/validator.py`: `_infer_value_type()` classifies both as
  numeric outputs.
- `src/factor_engine/planner.py`: `ExecutionPlanner.build_plan()`,
  `get_materialized_ordered_plan()`, and `_get_binary_materialized_ordered_plan()`
  keep plain `corr(open, close, 3)` on `compiled`, but route `corr(rank(...), ...)`
  and `cov(rank(...), ...)` to `materialized_ordered`.
- `src/factor_engine/executor.py`: `_compile_corr()` and `_compile_cov()` call
  Polars `pl.rolling_corr()` / `pl.rolling_cov()`; `_materialize_ordered_plan_on_sorted_df()`
  uses the same Polars functions over materialized child stage columns.
- `tests/unit/test_corr.py` and `tests/unit/test_cov.py`: direct correctness,
  minimum-window errors, and split-step equivalence for cross-sectional children.
- `tests/integration/test_planner.py` and `tests/integration/test_ordered_audit.py`:
  route coverage for plain and materialized ordered pair roots.
- `benchmarks/reports/performance_truth_scaleup.md`: Phase-1.5 evidence.
- `src/factor_engine/native_positional.py`, `src/factor_engine/execution_positional.py`,
  and `native/factor_engine_native/src/lib.rs`: reference native bridge and Rust
  kernel structure.

Current semantics:

- Syntax: `corr(x, y, n)` and `cov(x, y, n)` accept exactly three positional args
  and no kwargs.
- Window validation: `n >= 2`; violations raise `ExecutionError` containing
  `window >= 2`.
- Group boundary: calculation is `over(self.code_col)`, so windows do not cross
  `code` groups.
- Time order: ordered execution prepares a sorted frame by `[code, time]`; output
  restoration uses the row index to restore caller row order.
- Plain inputs: route is `compiled`.
- Cross-sectional or grouped children: route is `materialized_ordered`, materializes
  both child inputs, then applies the same rolling root over stage columns.
- Segmented children: current ordered boundary docs state these are isolated on the
  `segmented` route rather than audited materialized-ordered widening.
- Registry note: `corr` is currently tagged `window_kind="positional"` while `cov`
  is tagged `window_kind="rolling"`. This does not change current execution because
  plain `corr` still compiles to `pl.rolling_corr()` and materialized `corr` is
  handled by the binary materialized-ordered path. This asymmetry should be audited
  before adding a new native route.

Verified Polars behavior in the local venv (`polars 1.39.3`):

- Both `pl.rolling_corr` and `pl.rolling_cov` signatures include `ddof: int = 1`.
- Current engine does not pass `ddof`, so covariance/correlation use sample
  covariance/variance convention (`ddof=1`).
- Current engine passes `min_samples=2`.
- Null behavior is pairwise-valid: a row contributes only when both `x` and `y`
  are valid. Windows with fewer than two valid pairs return null.
- Constant `x` or `y`: `cov` returns `0.0` after minimum samples; `corr` returns
  `NaN` because variance denominator is zero.

## Mathematical Design

For each `(x, y, window)` on each `code` group, keep rolling state over valid pairs:

- `count`
- `sum_x`
- `sum_y`
- `sum_x2`
- `sum_y2`
- `sum_xy`

Pairwise validity is required: a row enters all six states only if both `x` and
`y` are non-null and finite-null semantics match Polars. Floating `NaN` is not
null in Polars; exact `NaN` behavior must be covered by golden tests before the
native path is considered production-safe.

For `count >= 2`:

- sample covariance numerator: `sum_xy - (sum_x * sum_y / count)`
- sample covariance: numerator / `(count - 1)`
- sample variance x: `(sum_x2 - (sum_x * sum_x / count)) / (count - 1)`
- sample variance y: `(sum_y2 - (sum_y * sum_y / count)) / (count - 1)`
- correlation: covariance / `sqrt(var_x * var_y)`

For `count < 2`, output null. If `var_x == 0` or `var_y == 0`, current Polars
behavior is `NaN` for `corr`; the prototype must reproduce that, including any
negative-zero or tiny-negative roundoff handling after subtraction. HYPOTHESIS:
clamping tiny negative variances to zero may improve numerical stability, but it
could also diverge from Polars and must not be done without golden-test approval.

## Native Kernel Feasibility

The native positional kernel is a useful reference but should not be copied blindly:

- Input bridge: positional supports a low-copy path using Polars private buffer
  APIs (`_get_buffers`, `_get_buffer_info`, `_from_buffer`, `_from_buffers`) plus a
  Python-object fallback. A corr/cov bridge would need two `Float64` value buffers
  plus two validity bitmaps.
- Grouped scan: positional passes `group_lengths` from ordered code runs. corr/cov
  can use the same assumption: input already sorted by `[code, time]`, scan each
  group independently, never carry state across groups.
- Time order: native kernel should be called only after the existing prepared-frame
  sort, never on unsorted caller input.
- Null bitmaps: unlike positional extremes, corr/cov validity is pairwise over two
  inputs. The scan must check both validity bitmaps and decrement old pair
  contributions as they leave the window.
- Output construction: cov/corr output is nullable `Float64`, not nullable `Int64`.
  The low-copy result path must own output bytes long enough for Polars buffers.
- GIL release: Rust scan should use `py.detach()` as positional does.
- Rayon parallelism: group-level parallelism is feasible because groups are
  independent. Start serial or env-gated parallel to reduce debugging surface.
- Fallback path: existing Polars implementation remains authoritative fallback.
- Feature/env gating: use a new opt-in flag such as
  `FACTOR_ENGINE_NATIVE_CORR_COV=1`, plus optional
  `FACTOR_ENGINE_NATIVE_CORR_COV_PARALLEL=1`. Do not reuse positional env flags.
- Memory ownership: if using `_from_buffer` / `_from_buffers`, keep Python byte
  owners attached exactly as positional does. This is private Polars API risk.
- Precision risk: rolling add/remove moments can accumulate cancellation error.
  Golden tests need tolerances and adversarial values; implementation should use
  `f64` and consider compensated sums only if Polars comparison requires it.

## Shared Computation Opportunity

| Case | Can share moment state? | Design |
| --- | --- | --- |
| `corr(x, y, w)` only | Partially | Compute all moments once; return corr only. No cross-output sharing, but one-pass state still replaces Polars root. |
| `cov(x, y, w)` only | Partially | Compute pair moments once; return cov only. |
| `corr(x, y, w) + cov(x, y, w)` | Yes | One scan can emit both outputs from identical `(x_key, y_key, w)`. |
| `corr(x, y, w1) + corr(x, y, w2)` | Limited | Different windows need different rolling queues/state. Input bridge and group metadata can share; state cannot be one set. |
| `corr(x, y, w) + corr(y, x, w)` | Yes | Correlation is symmetric. Canonicalize pair key for corr. For cov, covariance is also symmetric under current sample convention; confirm with golden tests. |
| Repeated corr/cov in `evaluate_many` | Yes | Planner can group equivalent moment specs and executor can attach multiple requested outputs from one native result bundle. |

Canonical moment key should include:

- normalized operator family: `moment_pair`
- expression identity for `x`
- expression identity for `y`
- `window`
- `ddof=1`
- `min_samples=2`
- input stage column names after materialization

For symmetric operators, the planner may canonicalize `(x, y)` order if and only
if output semantics are proven identical for nulls, NaNs, and signed zeros.

## Integration Design

Minimal integration points:

- Registry/operator contract: no user-facing language change. Before implementation,
  audit the `corr` `window_kind="positional"` asymmetry and either document it as
  legacy naming or align it with `cov` if tests prove no route change.
- Planner detection: add a non-semantic grouping pass over ordered batch items to
  detect shared corr/cov moment specs. This should not replace current `compiled`
  or `materialized_ordered` route by default.
- Executor route: keep Polars as default. Add optional native moment evaluation
  inside the ordered batch shell behind `FACTOR_ENGINE_MOMENT_KERNEL`. If native
  is unavailable, disabled, receives unsupported dtype, or hits an unsupported
  expression shape, fall back to current Polars expressions.
- Materialized ordered: native path can operate on materialized stage columns after
  child stages are created, preserving split-step correctness.
- Plain compiled: HYPOTHESIS: easiest prototype is an ordered-batch native route
  for root corr/cov in `evaluate_many`; single `evaluate()` or plain compiled
  expression can stay Polars until the route proves valuable.
- Profiling fields to add when implemented:
  - `native_corr_cov_used`
  - `native_corr_cov_time_ms`
  - `native_corr_cov_bridge_time_ms`
  - `native_corr_cov_output_build_time_ms`
  - `native_corr_cov_fallback_reason`
  - `native_corr_cov_pair_count`
  - `native_corr_cov_window`
  - `native_corr_cov_null_mode`
- Benchmark additions: extend performance truth scripts with native-disabled vs
  native-enabled moment cases and same-window corr+cov sharing cases.

## Correctness Tests Required

Golden tests must compare native outputs against current Polars engine outputs:

- no nulls
- `x` nulls
- `y` nulls
- both nulls
- all-null windows
- insufficient valid-pair count
- `min_samples=2` behavior
- code group boundaries
- row order restore after shuffled input
- `corr(x, y, w)` vs `corr(y, x, w)`
- `cov(x, y, w)` vs `cov(y, x, w)`
- constant `x` or `y` causing zero variance
- `NaN` input behavior, separate from null input behavior
- materialized ordered cases: `corr(rank(x), rank(y), w)` and `cov(rank(x), rank(y), w)`
- comparison against current Polars output for multiple windows and null rates

## Golden Semantics Test Coverage

Frozen in `tests/unit/test_corr_cov_golden.py`:

- no-null rolling windows
- `x` nulls, `y` nulls, both-null windows, and all-null windows
- zero, one, and two valid-pair windows with `min_samples=2`
- `window > history`
- zero variance: `cov` returns `0.0`; `corr` returns `NaN` after two valid pairs
- `NaN` remains a floating value and is not converted to null
- `corr(x, y, w)` symmetry with `corr(y, x, w)`
- `cov(x, y, w)` symmetry with `cov(y, x, w)`
- multi-code group boundaries
- unsorted caller input row restoration
- repeated `corr` / `cov` through `evaluate_many`

Comparison contract:

- null masks must match exactly
- `NaN` masks must match exactly
- numeric drift tolerance is `<= 1e-12`
- no implementation may silently convert null to `NaN` or `NaN` to null

## Performance Benchmarks Required

Benchmark matrix:

- native disabled vs enabled
- `corr` only
- `cov` only
- `corr + cov` same `x/y/window`
- multiple windows
- `corr(x, y, w) + corr(y, x, w)`
- repeated `corr/cov` in `evaluate_many`
- null rates: `0.0`, `0.01`, `0.10`
- row counts: `24k`, `120k`, `1m` if affordable
- code counts: `40`, `250`, `1000` if affordable
- bridge timing separated from scan timing
- serial vs parallel native mode

The benchmark must report whether native was actually used. If native is not used,
results must be classified as fallback, not native.

## Risk Ranking

| Rank | Risk | Severity | Notes |
| ---: | --- | --- | --- |
| 1 | Semantic mismatch with Polars | High | `ddof=1`, `min_samples=2`, `NaN`, zero variance, and pairwise null validity must match exactly. |
| 2 | Null handling mismatch | High | Two-input validity is more complex than positional one-input validity. |
| 3 | Numerical precision drift | High | Rolling add/remove moment formulas can cancel badly on large values. |
| 4 | Copy/bridge overhead dominates | Medium | Two input columns plus validity bitmaps may erase scan savings on smaller frames. |
| 5 | Group boundary bugs | Medium | Native scan must reset all six states per group. |
| 6 | Memory increase due to moment buffers | Medium | Multi-output sharing helps compute but may allocate extra output buffers. |
| 7 | Fallback complexity | Medium | Env/native availability/unsupported dtype paths must remain invisible semantically. |
| 8 | Planner over-specialization | Low-Medium | Keep grouping as an optional optimization pass, not a semantic route dependency. |

## Final Decision

`READY_FOR_PROTOTYPE`.

Reason: current corr/cov semantics are sufficiently understood to design a prototype:
sample covariance/correlation with `ddof=1`, `min_samples=2`, pairwise null
validity, code-group isolation, ordered-frame execution, and row-order restoration
are all testable against the existing Polars path. The prototype must remain
opt-in and must ship with golden tests before any default-path change.
