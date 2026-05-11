# Execution Attribution

P4 separates executor-native reuse timing from final output assembly so R4 can be
used as lifecycle input without mixing unrelated costs.

## Timing Fields

- `node_store_compute_time_ms`: compute time for DAG-owned shared intermediates.
- `compiled_output_eval_time_ms`: time spent evaluating final ordered output
  expressions before row-order restoration. In CSE-off baselines this can include
  repeated heavy compiled work.
- `restore_assemble_time_ms`: lightweight row-order restoration after output
  expressions have already been evaluated.
- `append_time_ms`: time spent appending restored output columns to the user
  frame.
- `finalize_time_ms`: `restore_assemble_time_ms + append_time_ms`.

The important boundary is:

```text
heavy compiled output eval != finalize
```

This fixes the earlier misleading profile shape where CSE-off workloads showed
large `finalize_time_ms` because restore was also executing heavy expressions.

## Compute Fields

- `estimated_unshared_compute_calls`: planner-side estimate of how many repeated
  expensive DAG-node occurrences would execute without materialization.
- `node_store_compute_calls`: actual compute count through the node-aware result
  store.
- `compiled_output_heavy_occurrence_count`: heavy materialization-candidate
  occurrences still left inside final compiled output evaluation.
- `compiled_fallback_eval_count`: final output expressions that still evaluate at
  least one heavy materialization candidate.
- `total_compute_calls`: attributed compute calls,
  `node_store_compute_calls + compiled_output_heavy_occurrence_count`.

This makes CSE-off and CSE-on comparable: CSE-off now has non-zero attributed
compute when final compiled output eval is doing repeated heavy work.

## Store Read Fields

- `node_store_read_count`: number of rewritten helper-column reads.
- `reuse_consumer_count`: number of independent consumers that depend on a
  materialized node.
- `total_store_hits`: compatibility alias for `node_store_read_count`.

Read frequency and consumer multiplicity are deliberately separate. Lifecycle
planning should use consumer multiplicity for ref/last-use shape and treat read
frequency as an execution economics signal.

## Lifecycle Boundary

These fields are observational only. P4 does not add ref-count drops, store
eviction, GC hooks, or native buffer lifecycle changes.
