# L1 Lifecycle Observability

L1 lifecycle observability started:

- planner-level last-use and ref-count metadata first
- executor trace second
- lifecycle summary metrics last
- no active drop in this phase

This phase only answers who could be released and when. It does not release,
evict, shrink, sweep, or change node-store residency.

## Planner Plan

The planner emits lifecycle metadata for every DAG node, with materialized nodes
carrying the useful release plan:

- `producer_step`
- `consumer_steps`
- `last_use_step`
- `ref_count_initial`
- `drop_candidate`
- `drop_blocker_reason`

`consumer_steps` is planner semantics, not runtime read frequency. It preserves
dependency multiplicity. For a repeated-heavy expression like:

```text
ts_rank(close, 10) + ts_rank(close, 10)
```

the shared `ts_rank` node has two planned consumers. If both reads occur inside
the same compiled output expression, the two consumer entries may share the same
step:

```text
consumer_steps = [5, 5]
ref_count_initial = 2
last_use_step = 5
```

For a multi-output DAG such as four outputs depending on the same `ts_rank`
node, the planned consumers are separate output-evaluation steps:

```text
consumer_steps = [11, 12, 13, 14]
ref_count_initial = 4
last_use_step = 14
```

Final output retention is not treated as an ordinary intermediate consumer. If a
materialized node is itself a final output, it is blocked with
`drop_blocker_reason = "final_output_retention"` until a later lifecycle phase
defines final-output-safe release behavior.

## Executor Trace

The executor records runtime evidence against the planner plan:

- `materialized_at_step`
- `first_read_step`
- `last_read_step`
- `retained_until_end`
- `theoretical_release_step`
- `release_lag_steps`
- `bytes_estimate`

Runtime reads and planner consumers remain separate:

- `node_store_read_count` counts helper-column reads.
- `reuse_consumer_count` counts independent output consumers that reused the
  materialized node.
- `planner_ref_count_initial` comes from the DAG lifecycle plan.

## Summary Metrics

Profiling summarizes release potential with:

- `lifecycle_candidate_count`
- `lifecycle_releasable_node_count`
- `lifecycle_peak_live_node_count`
- `lifecycle_peak_live_bytes_est`
- `avg_release_lag_steps`
- `max_release_lag_steps`

For L1, release lag is deliberately simple:

```text
release_lag_steps = end_step - theoretical_release_step
```

The current store keeps materialized nodes until the end of the batch, so these
metrics are observational only. They are the input to a later L2 active-drop
design, not an eviction policy.

L1.5 supersedes this early lag definition with explicit residency distance:

- `structural_release_lag_steps = batch_end_step - theoretical_release_step`
- `finalize_retention_lag_steps = finalize_step - theoretical_release_step`
- `release_lag_steps` remains as a compatibility alias for structural lag

See [L1.5 Residency Distance Closure](l1_5_residency_distance_closure.md).
