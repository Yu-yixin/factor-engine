# L3A Native-Heavy Lifecycle Design

L3A is design and observability only. It does not enable native-heavy active drop, does not change executor paths, does not remove helper columns, and does not add a lifecycle mode.

## Boundary

Native-heavy currently means DAG nodes classified as `native_heavy`, covering positional `argmax` / `argmin` materialization candidates.

Allowed in L3A:

- lifecycle feasibility modeling
- blocker classification
- compute / path / storage attribution fields
- benchmark/report observability

Forbidden in L3A:

- native-heavy active drop
- working-frame helper column deletion
- native buffer release
- allocator or GC-level lifecycle
- new `lifecycle_mode` branches

## Layer Model

Native-heavy lifecycle is modeled as three separate layers:

| Layer | Object | L3A status |
| --- | --- | --- |
| compute | native kernel / heavy evaluation | observable |
| normalized expression | rewritten helper-column usage | observable |
| storage | node-store entry residency | observable only |

The storage layer is not enough by itself. Future native-heavy drop must be tied to the normalized-expression layer, because native-heavy often appears as single logical consumer with multiple helper reads.

## Eligibility

Each native-heavy node receives:

```text
native_heavy_lifecycle_eligibility:
  forbidden
  observable_only
  candidate_future
```

Current stage behavior:

- CSE/fallback unresolved native-heavy nodes are `forbidden`.
- Materialized and rewritten native-heavy nodes are `observable_only`.
- `candidate_future` is reserved for a later phase after consumer semantics are proven stable.

## Blockers

The blocker taxonomy is:

```text
unresolved_fallback_path
unstable_consumer_semantics
helper_alias_still_referenced
compiled_dependency_uncertain
```

Every native-heavy node profile explains why it cannot be active-dropped yet.

## Profiling Fields

Per-node fields:

- `native_heavy_lifecycle_eligibility`
- `native_heavy_blocker_reason`
- `native_compute_time_ms`
- `native_path_normalization_time_ms`
- `native_storage_residency_bytes`
- `native_node_store_read_count`
- `native_logical_consumer_count`
- `native_effective_use_count`
- `native_fallback_eval_count`
- `native_rewrite_applied`
- `native_helper_usage_pattern`

Run/batch fields:

- `native_heavy_node_count`
- `native_heavy_forbidden_count`
- `native_heavy_observable_only_count`
- `native_heavy_candidate_future_count`
- `native_compute_time_ms`
- `native_path_normalization_time_ms`
- `native_storage_residency_bytes`
- `native_node_store_read_count`
- `native_logical_consumer_count`
- `native_effective_use_count`
- `native_fallback_eval_count`
- `native_rewrite_applied_count`
- `native_helper_usage_patterns`

## Consumer Model

L3A keeps planner consumer count separate from runtime read behavior:

- `native_logical_consumer_count` tracks logical store consumers.
- `native_node_store_read_count` / `native_effective_use_count` track helper reads.

This avoids reusing L2 ref-count semantics for native-heavy nodes before the consumer model is stable.

## Benchmark Workloads

The benchmark harness includes:

- `native_heavy_probe`
- `native_heavy_nested`
- `native_heavy_multi_read`

These should be run as:

```text
cse=False vs cse=True
lifecycle_mode=off
```

The goal is attribution and blocker distribution, not active drop.

## Entry Gate For Later Implementation

L3A.2 implementation is only allowed after:

- native-heavy consumer semantics are stable
- compute / path / storage gains are separable
- blocker taxonomy explains all observed native-heavy nodes
- profiling can identify at least one `candidate_future` class

Until then, native-heavy remains outside L2 first-wave active lifecycle.
