# Native corr/cov Bridge Review

## Gate Result

The corr/cov native prototype was rejected by the A/B gate and must not be enabled by default.

Evidence:

```text
benchmarks/reports/native_corr_cov_ab.md
benchmarks/artifacts/native_corr_cov_ab.json
```

Reduced matrix result:

| rows | codes | window | null_rate | mode | native_used | polars median ms | native median ms | speedup |
| ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: |
| 24000 | 40 | 5 | 0.0 | corr | true | 2.407 | 7.311 | 0.329 |
| 24000 | 40 | 20 | 0.01 | cov | true | 1.720 | 6.765 | 0.254 |
| 24000 | 250 | 60 | 0.1 | corr | true | 3.453 | 7.006 | 0.493 |

Decision: `REJECT`.

## Current Native Path Timing

Confirmed by benchmark:

- total wall time is measured for Polars and native callable paths
- native actually ran in all three reduced cases
- median native total wall time is slower than Polars
- CV is acceptable for the native path in the reduced matrix

Not currently isolated by the benchmark:

- native compute time
- bridge time
- output construction time
- Python object conversion cost
- RSS/peak memory

The Python bridge returns `native_corr_cov_time_ms`, `native_corr_cov_bridge_time_ms`, and `native_corr_cov_output_build_time_ms`, but `benchmarks/scripts/benchmark_native_corr_cov.py` does not record those fields in `benchmarks/artifacts/native_corr_cov_ab.json`. Any explanation based on bridge cost is therefore a hypothesis until instrumentation is added.

## Current corr/cov Bridge

`src/factor_engine/native_corr_cov.py` currently does this:

- casts `x` and `y` to `Float64`
- converts both input columns with `to_list()`
- computes `group_lengths` through a Polars group-by over code
- calls `factor_engine_native.grouped_corr_cov(...)`
- receives `Vec<Option<f64>>` through PyO3
- builds a `pl.Series(..., dtype=pl.Float64)` from Python values

`native/factor_engine_native/src/rolling_moments.rs` currently does this:

- accepts `Vec<Option<f64>>` for x and y
- scans each group independently
- uses rolling sums for `count`, `sum_x`, `sum_y`, `sum_x2`, `sum_y2`, and `sum_xy`
- releases the GIL during the Rust scan
- optionally uses Rayon over groups
- returns `Vec<Option<f64>>`, pair count, and Rust scan time

This is correct enough for the parity tests but not bridge-efficient.

## Comparison With Native Positional Path

The positional native path has two bridge modes:

- low-copy path: extracts Polars value and validity buffers through private Polars buffer APIs, passes raw pointers and offsets to Rust, returns bytes for data and validity, and constructs a nullable Polars series with `_from_buffer` / `_from_buffers`
- object fallback: converts values through Python objects

The low-copy positional path reuses:

- value buffer extraction with `_get_buffers()` and `_get_buffer_info()`
- validity bitmap pointer/offset handling
- group metadata via ordered code group lengths
- GIL release around Rust scanning
- Rayon group-level parallelism
- direct output data and validity buffer construction

Current corr/cov does not use the equivalent low-copy input path. It uses Python lists for both input columns and Python-value output construction. It also returns only one output per native call.

Reusable pieces for corr/cov:

- buffer extraction pattern from `_evaluate_low_copy_native`
- validity bitmap pointer and offset handling
- `_bytes_pointer` and Polars buffer-owner pattern
- group length construction, possibly shared per batch
- GIL release pattern
- Rayon per-group scan pattern
- output validity bitmap construction

Corr/cov-specific additions needed:

- two input f64 buffers
- two validity bitmaps
- pairwise validity logic
- nullable f64 output buffers, not nullable i64
- optional multi-output return for corr and cov together

## Why Polars Wins

`CONFIRMED`: Native total wall time is slower on the reduced matrix.

`CONFIRMED`: The current benchmark does not isolate bridge, scan, output, or RSS fields.

`CONFIRMED`: Current corr/cov input bridge uses `to_list()` for both input columns.

`CONFIRMED`: Current corr/cov output path returns Python/PyO3 `Vec<Option<f64>>` and constructs a Polars series from Python values.

`CONFIRMED`: The reduced benchmark tests isolated corr or cov cases, not a shared same `(x, y, window)` corr+cov case.

`HYPOTHESIS`: Python object bridge overhead dominates the native path.

Reason: two `to_list()` conversions plus `Vec<Option<f64>>` output are visible in code, but the benchmark does not record bridge/output timings.

`HYPOTHESIS`: Per-expression native call overhead erases any scan benefit.

Reason: the benchmark calls native once per expression and does not batch shared moments.

`HYPOTHESIS`: Polars rolling corr/cov is already highly optimized at 24k-row reduced scale.

Reason: Polars median times are 1.7-3.5 ms in the reduced cases. Larger/full matrix was not run.

`HYPOTHESIS`: Native parallel overhead may hurt small cases.

Reason: corr/cov parallel flag defaults off in the benchmark environment, so this is not proven for the current run. It remains relevant for future experiments.

`UNKNOWN`: Moment state memory pressure.

Reason: no peak RSS or allocation telemetry is present in the native corr/cov A/B artifact.

`UNKNOWN`: Whether native wins at 120k or 1m rows.

Reason: full matrix is `NOT_RUN`.

## Redesign Options

### Option 1: Low-Copy corr/cov Bridge

Design:

- reuse positional buffer bridge pattern
- pass x/y f64 buffers, offsets, lengths, and validity bitmap pointers to Rust
- compute pairwise validity in Rust from bitmaps
- return nullable f64 data bytes and validity bytes
- construct output through Polars buffer APIs
- record bridge, scan, output, total, and RSS fields in the benchmark artifact

Expected speed impact:

- likely positive if Python object conversion is a major cost
- not proven until instrumentation and A/B rerun

Expected memory impact:

- lower Python object allocation pressure
- still allocates output data and validity buffers
- may require rechunking/casting inputs

Implementation risk:

- medium-high because it uses private Polars buffer APIs
- pointer/offset correctness matters

Correctness risk:

- high around null bitmap offsets, `NaN` preservation, signed zeros, zero variance, and row alignment

Required tests:

- existing golden/parity tests
- null bitmap offset/sliced-series tests
- no-null fast path tests
- all-null and mixed-null pairwise validity tests
- `NaN` distinct from null

Required benchmark:

- same reduced matrix plus full matrix when affordable
- record total, bridge, native scan, output build, CV, and peak RSS
- compare serial and parallel

Prerequisite for full native rolling engine:

- yes, if corr/cov is kept as a native candidate
- no, if full native rolling starts with other operators

### Option 2: Batch Shared-Moment Native Call

Design:

- one native call computes corr and cov together for identical `(x, y, window)`
- optionally return both nullable f64 outputs from one rolling moment scan
- later extend to `corr(x, y, w)` plus `corr(y, x, w)` sharing

Expected speed impact:

- likely positive for workloads with corr+cov or symmetric duplicates
- limited for isolated corr-only or cov-only cases

Expected memory impact:

- may allocate multiple output buffers at once
- reduces repeated input conversion and repeated scans

Implementation risk:

- medium
- requires API design for multiple outputs and ownership

Correctness risk:

- medium-high because two outputs must share one state without changing individual Polars semantics

Required tests:

- `evaluate_many` repeated corr/cov parity
- same x/y/window corr+cov parity
- symmetric corr/cov duplicates
- mixed windows should not incorrectly share state

Required benchmark:

- include corr only, cov only, corr+cov same pair/window, symmetric corr, and multiple windows
- record per-output total cost, not only per-call cost

Prerequisite for full native rolling engine:

- useful but not universal
- prerequisite only if shared moments are a first-class engine goal

### Option 3: Planner-Level Shared Moments

Design:

- detect compatible corr/cov specs in `evaluate_many`
- canonicalize safe symmetric pairs only after golden proof
- plan one shared moment computation and attach requested outputs
- keep Polars default unless native gate accepts

Expected speed impact:

- positive when repeated/shared corr/cov expressions exist
- no benefit for isolated single-expression benchmark cases

Expected memory impact:

- can reduce repeated stage/output pressure
- may retain shared intermediate state longer

Implementation risk:

- high if introduced before bridge evidence
- risks planner complexity before the kernel path is proven

Correctness risk:

- high around expression identity, materialized ordered children, row restoration, and mixed windows

Required tests:

- planner detection tests
- `evaluate_many` repeated corr/cov tests
- materialized ordered children such as `corr(rank(x), rank(y), w)`
- fallback equivalence when native disabled or unavailable

Required benchmark:

- shared-workload matrix, not only isolated corr/cov
- include native disabled, native enabled, and Polars baseline

Prerequisite for full native rolling engine:

- not before low-copy measurement
- should follow bridge/kernel evidence

### Option 4: Do Nothing For corr/cov Now

Design:

- keep corr/cov Polars-backed
- retain golden semantics and A/B report
- reject native corr/cov prototype as currently implemented
- focus native rolling design on operators with clearer standalone wins or lower bridge complexity

Expected speed impact:

- no corr/cov speedup
- avoids making production slower

Expected memory impact:

- no new native memory pressure

Implementation risk:

- low

Correctness risk:

- low because current Polars semantics stay authoritative

Required tests:

- keep golden tests in CI
- keep native parity opt-in if experiment remains

Required benchmark:

- none immediately beyond preserving the rejected A/B record
- rerun only when bridge/kernel changes

Prerequisite for full native rolling engine:

- yes as a decision boundary: full native rolling should not inherit this rejected bridge design

## Instrumentation Gaps

Before another corr/cov redesign is judged, add benchmark fields:

- `native_corr_cov_total_time_ms`
- `native_corr_cov_bridge_time_ms`
- `native_corr_cov_time_ms`
- `native_corr_cov_output_build_time_ms`
- `native_corr_cov_pair_count`
- `native_corr_cov_parallel_used`
- `peak_rss_mb`
- `fallback_reason`

The current Python result object already contains some of these fields; the benchmark needs to persist them.

## Final Recommendation

Recommendation: `REDESIGN_LOW_COPY_FIRST`.

Rationale:

- the current prototype was rejected and must remain opt-in
- the most obvious confirmed structural gap versus native positional is the lack of a low-copy bridge
- planner-level sharing before low-copy evidence would add complexity without proving the base native path can beat total wall time
- batch shared moments are valuable, but they should be evaluated after bridge timing is visible, or together with low-copy as a second benchmark phase

Implementation is not allowed now. The next allowed step is design/instrumentation: add timing/RSS attribution to the benchmark, then prototype a low-copy corr/cov bridge behind the same disabled-by-default flag.
