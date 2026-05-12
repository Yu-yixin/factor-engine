# Native Resource Lifecycle

## Lifecycle Events

Native resource work must be explainable with these event names:

- `native_buffer_created`
- `native_buffer_attached`
- `native_buffer_released`
- `native_fallback`
- `native_bridge_failed`

The normal lifecycle is:

1. native buffer created
2. native buffer attached to a result owner
3. native result converted to a Polars series or frame column
4. Polars series attached to the working frame or final output
5. temporary stage column dropped when its logical lifetime ends
6. native buffer logically released when no owner needs it

## Alignment With Existing Runtime

- `StageRegistry` records helper and materialized stage creation/consumption/drop intent.
- `NodeResultStore` owns reusable node results and must expose whether native-heavy values are retained for reuse.
- `OutputAttachMode` controls when final outputs attach to the working frame.

Native resources must not bypass these concepts. A native buffer that becomes a Polars series still has to be represented in profiling as attached or released.

## Required Profile Fields

Native corr/cov profile fields:

- `native_corr_cov_used`
- `native_corr_cov_time_ms`
- `native_corr_cov_bridge_time_ms`
- `native_corr_cov_output_build_time_ms`
- `native_corr_cov_fallback_reason`
- `native_corr_cov_pair_count`
- `native_corr_cov_window`
- `native_corr_cov_null_mode`

Native lifecycle event fields:

- `buffer_id`
- `related_output_name`
- `bytes_estimate`
- `native_parallel_used`
- `parallel_worker_count`
- `rss_mb`

## RSS Rule

Logical release is not the same thing as RSS reduction. Allocators, Polars buffer ownership, Python reference cycles, and OS memory policy can keep process RSS flat after a buffer is logically dead. Reports may say a buffer was released from the engine lifecycle; they must not claim that RSS fell unless measured RSS actually fell.
