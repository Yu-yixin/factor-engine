# Low-Copy corr/cov Experiment Plan

## Scope

This document designs the next corr/cov experiment only.

It does not authorize:

- low-copy implementation
- shared-moment planner work
- full native rolling implementation
- default native enablement

The current Python-object corr/cov prototype remains experimental only and stays rejected until a new experiment earns fresh evidence.

## Goal

Measure whether a positional-style low-copy bridge can make native corr/cov competitive on total wall time without changing corr/cov semantics.

Success here means "worth another review," not "ready to enable by default."

## Exact Timing Fields To Add

Keep the current compatibility fields:

- `native_corr_cov_used`
- `native_corr_cov_time_ms`
- `native_corr_cov_bridge_time_ms`
- `native_corr_cov_output_build_time_ms`
- `native_corr_cov_fallback_reason`
- `native_corr_cov_pair_count`
- `native_corr_cov_window`
- `native_corr_cov_null_mode`

Add these exact fields for the next experiment:

- `native_corr_cov_total_wall_time_ms`
- `native_corr_cov_group_lengths_time_ms`
- `native_corr_cov_input_cast_rechunk_time_ms`
- `native_corr_cov_input_buffer_extract_time_ms`
- `native_corr_cov_native_input_ingest_time_ms`
- `native_corr_cov_native_scan_time_ms`
- `native_corr_cov_output_buffer_build_time_ms`
- `native_corr_cov_series_construct_time_ms`
- `native_corr_cov_low_copy_bridge_used`
- `native_corr_cov_python_object_bridge_used`
- `native_corr_cov_parallel_used`
- `native_corr_cov_group_parallelism_level`
- `native_corr_cov_output_buffer_bytes_estimate`

Compatibility note:

- `native_corr_cov_time_ms` should remain populated for old consumers, but the experiment report should treat `native_corr_cov_native_scan_time_ms` as the true kernel-only field.
- `native_corr_cov_bridge_time_ms` should become the sum of group-length build, cast/rechunk, buffer extract, and native-ingest work.
- `native_corr_cov_output_build_time_ms` should become the sum of output-buffer build and final series construction.

## Low-Copy Input Bridge Design

### Python-side boundary

The experiment should mirror the accepted positional bridge shape:

1. cast `x` and `y` to `Float64`
2. `rechunk()` both series
3. read `values` and `validity` buffers through `_get_buffers()`
4. read pointer and offset metadata through `_get_buffer_info()`
5. compute `group_lengths` once per call from ordered `code`
6. call a new low-copy native entrypoint with:
   - `x_values_ptr`, `x_values_offset`, `x_validity_ptr`, `x_validity_offset`
   - `y_values_ptr`, `y_values_offset`, `y_validity_ptr`, `y_validity_offset`
   - shared `length`
   - `group_lengths`
   - `window`
   - `mode`
   - `parallel`

### Rust-side boundary

The low-copy experiment should:

- consume Arrow-style f64 buffers directly
- consume nullable validity bitmaps directly
- compute pairwise validity in Rust
- keep `NaN` in the data path and use validity only for nulls
- release the GIL during scan work
- keep group-parallel execution optional and measurable

Out of scope for this experiment:

- planner batching
- corr+cov multi-output sharing
- cross-expression shared moments
- any fallback to default native mode

## Nullable f64 Output Buffer Design

The experiment should return nullable f64 buffers, not Python values.

Planned shape:

- output data buffer: contiguous f64 bytes for all rows
- output validity buffer: one bitmap for nullability
- Python keeps the returned bytes as buffer owners
- Python reconstructs the result with:
  - `pl.Series._from_buffer(pl.Float64, ...)`
  - `pl.Series._from_buffers(pl.Float64, data, validity)`

Rules:

- `NaN` must remain a data value, not a null marker
- null means "insufficient valid pairs" or "pairwise-valid sample count < 2"
- output row count must exactly match input row count
- the first experiment returns one output per call only

Deferred on purpose:

- dual corr+cov output in one call
- shared output allocation across sibling expressions
- planner-visible shared-moment state

## Parity Tests To Reuse

Required reuse without semantic weakening:

- `tests/unit/test_corr.py`
- `tests/unit/test_cov.py`
- `tests/unit/test_corr_cov_golden.py`
- `tests/unit/test_native_corr_cov_parity.py`

Why these matter:

- they already lock null-vs-`NaN` behavior
- they cover zero variance, insufficient samples, row restoration, repeated `evaluate_many`, and symmetry
- they prove the current DSL semantics independently of the bridge shape

Additional parity additions should be planned before coding, but not implemented in this freeze:

- sliced-series validity-offset coverage
- no-validity-buffer fast path
- all-null group and mixed-null bitmap coverage
- explicit output-buffer reconstruction smoke checks

## Benchmark Gate

Reuse `benchmarks/scripts/benchmark_native_corr_cov.py` as the gate entrypoint, but extend the case artifact to record the new timing fields and bridge mode.

Required benchmark artifact additions per native case:

- `bridge_mode`
- `parallel_used`
- `group_parallelism_level`
- all timing fields listed above
- `output_buffer_bytes_estimate`
- `peak_rss_mb` or a clearly named isolated-process RSS proxy

Run order:

1. reduced matrix with detailed timings
2. reduced matrix serial vs parallel
3. only if reduced results are stable, the larger matrix

The benchmark must keep using total wall time as the acceptance surface.

## Reject And Accept Thresholds

### Immediate reject

Reject the experiment if any of these occur:

- any reused correctness/parity test fails
- any case silently falls back without a recorded `fallback_reason`
- any required timing field is missing from the artifact
- the bridge still relies on `to_list()` or Python-value `Vec<Option<f64>>` output construction
- median total speedup on the reduced matrix is below `1.00x`
- worst native CV exceeds `0.15`
- peak RSS regresses materially without offsetting wall-time gain

### Accept for the next review stage

Accept the experiment as a candidate for a follow-up design review only if:

- all reused parity tests pass
- native runs complete in all reduced cases
- median total wall-time speedup is at least `1.25x`
- worst native CV is at most `0.15`
- peak RSS is not materially worse than Polars
- the detailed timing split shows the low-copy bridge removed most of the prior Python-object overhead

This acceptance does not permit default enablement.

## Fallback Behavior

Fallback stays conservative:

- Polars remains the default path
- env-off means Polars
- import failure means Polars
- unsupported dtype or buffer-layout extraction failure means Polars
- native exception means Polars
- output-buffer reconstruction failure means Polars

Important boundary:

- do not silently chain low-copy failure into the rejected Python-object corr/cov bridge during the experiment gate
- if low-copy fails, record the fallback and use Polars so the experiment result stays interpretable

## Readiness Statement

NEEDS_DIRTY_TREE_CLEANUP_FIRST
