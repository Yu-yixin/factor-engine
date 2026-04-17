# Future Operator Roadmap

This document lists operator families that are valuable for Factor Engine but
should not be added as ordinary functions under the current boundary. The
standard is not "does Alpha101 use it"; the standard is:

1. Can it land in a native or backend-vectorized execution layer?
2. Can it be represented by DAG/CSE identity without one-off hacks?
3. Can its intermediates, helpers, buffers, and materialization lifetime be
   audited?

If the answer is not yes to all three, the operator is a roadmap item.

## Acceptance Status Legend

| status | meaning |
| --- | --- |
| blocked | Do not implement in normal operator batches. |
| design-first | Needs an architecture/design phase before implementation. |
| native-framework | Requires a Rust/C++ or backend-native kernel framework. |
| lifecycle-gated | Requires helper/native-buffer/materialization lifecycle rules first. |
| future-candidate | Worth pursuing once the listed gates are met. |

## A. Weighted Rolling Family

Representative operators:

- `decay_linear(x, d)`
- `weighted_mean(x, w)`
- `ewm_mean`
- `ewm_std`
- `ewm_var`
- `weighted_rank`
- `weighted_corr`
- `weighted_cov`

Current status: `native-framework`, `lifecycle-gated`, `future-candidate`

Why not now:

- These are kernel/stateful rolling operators, not ordinary aggregations.
- A naive implementation tends to become executor special cases or Python window
  callbacks.
- Weight state, scratch buffers, and materialized children need planner-visible
  lifecycle semantics.

Future acceptance conditions:

- Native weighted rolling kernel family exists.
- Window weights and options are part of canonical identity.
- State layout and scratch buffer ownership are documented.
- Route and ordered audit are updated.
- Lifecycle report can explain state residency and helper residency.

Expected native shape:

```text
partition(code) -> ordered(time) -> weighted rolling kernel -> aligned output
```

## B. Positional Ordered Family

Representative operators:

- `ts_argmax(x, d)`
- `ts_argmin(x, d)`
- `argtopk(x, d, k)`
- `argbottomk(x, d, k)`
- `ts_first_arg`
- `ts_last_arg`

Current status: `design-first`, `native-framework`, `future-candidate`

Why not casually:

- Positional semantics require exact tie-break, null handling, and offset
  definition.
- Materialized child inputs must preserve ordered contracts.
- Native buffers and state reuse must be route-sensitive.

Future acceptance conditions:

- Positional semantics are locked in docs and tests.
- Native monotonic/deque or equivalent state structure exists where needed.
- `positional_ordered` route behavior remains auditable.
- Native buffer lifetime is visible in profiling.

Expected native shape:

```text
ordered partition -> positional state kernel -> offset/value result
```

## C. Native Rolling Reducer Family

Representative operators:

- `product(x, d)`
- `geometric_mean(x, d)`
- `rolling_compound_return(x, d)`
- native-only `rolling_reduce` subfamilies

Current status: `native-framework`, `blocked`

Why not now:

- `product` already exposed the problem: current Polars expression support does
  not provide a clean vectorized rolling product path in this environment.
- Python callback fallback is outside the accepted operator boundary.
- Adding one reducer by hand would create an unscalable executor exception.

Future acceptance conditions:

- A native rolling reducer framework exists.
- Reducer state is fixed-size or explicitly bounded.
- Null and prefix-window semantics are standardized.
- CSE/materialization behavior is defined for reducer nodes.
- Benchmark proves no callback/object fallback.

Expected native shape:

```text
rolling reducer registry:
  reducer_id -> state init -> update -> emit -> drop
```

## D. Group-Aware Cross-Sectional Family

Representative operators:

- `indneutralize(x, group)`
- `group_scale(x, group)`
- expanded `group_rank`
- expanded `group_zscore`
- style/industry neutralization variants

Current status: `design-first`, `future-candidate`

Why not casually:

- Group key sensitivity must become part of validator, contract, planner, and
  DAG identity.
- Grouped outputs create staged cross-sectional helpers that need lifecycle
  treatment.
- Neutralization may require regression-like internals rather than a simple
  demean.

Future acceptance conditions:

- Group-aware contract is explicit and audited.
- Group key identity is included in canonicalization.
- Stage/helper lifecycle can distinguish global cross-section and grouped
  cross-section outputs.
- Null group behavior and singleton group behavior are documented.

Expected execution shape:

```text
partition(time, group) -> grouped cross-sectional transform -> aligned output
```

## E. Generalized Window Statistics Family

Representative operators:

- `quantile(x, d, q)`
- `median_abs_deviation(x, d)`
- `percentile_rank(x, d)`
- `entropy(x, d)`
- native `rolling_skew`
- native `rolling_kurt`
- `winsorize(x, d)`
- `clip_by_quantile(x, d)`

Current status: `native-framework`, `future-candidate`

Why not casually:

- Order statistics need partial sorting, selection, histograms, sketches, or
  equivalent state.
- Scratch buffers can dominate memory if not lifecycle-aware.
- Approximate vs exact semantics must be declared up front.

Future acceptance conditions:

- Exact or approximate semantics are locked.
- Native state model and scratch memory model are documented.
- Window parameters are identity-sensitive.
- Profiling reports scratch/native residency.

Expected native shape:

```text
ordered partition -> order-stat state -> statistic output
```

## F. Regression And Rolling Model Family

Representative operators:

- `rolling_beta(x, y, d)`
- `rolling_resid(y, x, d)`
- `rolling_ols(y, x1, x2, ..., d)`
- `rolling_slope(x, d)`
- `rolling_r2(...)`

Current status: `design-first`, `native-framework`, `lifecycle-gated`

Why not casually:

- These are model kernels, not column functions.
- They introduce multi-input window state, numeric stability concerns, and
  possible multi-output results.
- Internal matrix/cache lifetimes must be explicit.

Future acceptance conditions:

- A rolling model contract exists.
- Input arity and output schema rules are defined.
- Native linear algebra backend and state ownership are defined.
- CSE can identify shared model state when multiple outputs consume it.

Expected native shape:

```text
multi-input window -> model state update -> one or more aligned outputs
```

## G. Multi-Output Operator Family

Representative operators:

- expanded `fft`
- `rolling_ols` returning multiple statistics
- `decompose(...) -> trend, seasonal, resid`
- `topk(x, k)` returning values and positions

Current status: `design-first`, `lifecycle-gated`

Why not casually:

- The engine is still primarily single-column-result oriented.
- Multi-output nodes affect schema contracts, output assembly, materialization
  policy, and lifecycle granularity.

Future acceptance conditions:

- Multi-output schema contract exists.
- Node identity can represent output fields.
- Store/helper lifecycle can drop individual fields or whole result bundles.
- `evaluate` and `evaluate_many` output contracts are explicit.

## H. Generalized Pairwise And Matrix Family

Representative operators:

- `pairwise_corr(...)`
- `cross_corr(x, y, lag_set)`
- `distance(x, y, d)`
- `similarity(x, y, d)`

Current status: `design-first`, `native-framework`, `lifecycle-gated`

Why not casually:

- These operators may expand output width dramatically.
- They can create large intermediate matrices.
- They require strict native buffer ownership and materialization discipline.

Future acceptance conditions:

- Output dimensionality contract exists.
- Native buffer layout and release model exist.
- Frame width and result-store impact can be profiled before active execution.

## I. Advanced Segmented Kernel Family

Representative operators:

- `seg_product`
- `seg_std`
- `seg_rank`
- `seg_decay`
- `seg_corr`
- `seg_cov`
- `seg_quantile`

Current status: `native-framework`, `lifecycle-gated`

Why not casually:

- Complex segmented operators can explode segment precompute and helper columns.
- Segment spec sensitivity must be represented in DAG identity and CSE.
- Precompute cache lifetime must be explicit.

Future acceptance conditions:

- Segment state model exists.
- Segment precompute cache has lifecycle rules.
- Segment spec identity is canonicalized and audited.
- Native segmented kernels exist for the accepted family.

## J. Custom Native Kernel / UDF Family

Representative capabilities:

- custom rolling reducer
- custom segmented reducer
- custom pairwise kernel
- user-defined factor operator

Current status: `blocked`, `design-first`

Why not now:

- Uncontrolled UDFs break planner inference, DAG/CSE, lifecycle, and performance
  guarantees.
- This is not an operator; it is a kernel ABI and safety model.

Future acceptance conditions:

- Fixed native ABI.
- Kernel registry with declared contracts.
- State lifecycle protocol.
- Sandbox/error model.
- Benchmark and audit hooks.

## Priority Backlog

First tier: high value, strong architecture meaning.

- `decay_linear`
- `ts_argmax`
- `ts_argmin`
- `indneutralize`
- expanded `group_rank`
- expanded `group_zscore`

Second tier: native rolling family expansion.

- `product`
- `quantile`
- `winsorize`
- `rolling_beta`

Third tier: after deeper system upgrades.

- `ewm_mean`
- `rolling_ols`
- multi-output model/statistics operators

