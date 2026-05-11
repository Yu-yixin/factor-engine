# L1.5 Residency Distance Closure

L1.5 keeps lifecycle read-only. It does not drop, evict, shrink, or rewrite
native buffer lifetime. Its only purpose is to turn "this node is theoretically
releasable" into "this much residency distance and bytes-step waste could be
saved by a future drop policy."

## Step Model

Lifecycle steps now cover the whole ordered batch shape:

```text
producer steps
-> consumer steps
-> restore_assemble_step
-> append_step
-> finalize_step
-> batch_end_step
```

The ordering is stable and comparable across planner, executor, and profiling:

```text
finalize_step >= append_step >= restore_assemble_step >= last_use_step
batch_end_step > finalize_step
```

`last_use_step` remains the planner's theoretical last consumer. `batch_end_step`
is the observed residency boundary for L1.5, because node-store entries are still
retained until the batch completes.

## Lag Metrics

The old `release_lag_steps` field is kept for compatibility, but is superseded
by `structural_release_lag_steps`.

Current fields:

- `structural_release_lag_steps = batch_end_step - theoretical_release_step`
- `finalize_retention_lag_steps = finalize_step - theoretical_release_step`
- `retained_past_last_read`
- `release_lag_steps`, deprecated compatibility alias for structural lag

These fields distinguish "last read happened" from "the node stopped being
resident." A node can have `last_read_step == last_use_step` and still have
positive structural lag.

## Potential Savings

L1.5 uses a deliberately simple ranking model:

```text
potential_live_bytes_step_savings =
    bytes_estimate * structural_release_lag_steps
```

This is not an allocator-level memory model. It is a lifecycle-priority score
that lets L2 rank which nodes are worth trying first.

Profiling reports:

- `potential_live_bytes_step_savings`
- `top_releasable_nodes_by_bytes_step_savings`
- `l2_first_wave_candidate_count`

## L2 First-Wave Allowlist

The first active-drop wave may only consider nodes matching all of:

- `materialization_eligibility = materialize_for_both`
- `drop_candidate = true`
- `drop_blocker_reason = ""`
- `structural_release_lag_steps > 0`
- `bytes_estimate >= L2 first-wave threshold`

The current threshold is intentionally minimal in code so tests and small smoke
runs can exercise the path. Real benchmark decisions should raise it to a
full-data-relevant byte floor before enabling any active drop.

## L2 Denylist

Do not active-drop these in the first wave:

- final output retention nodes
- nodes with non-empty blocker reason
- native-heavy complex shapes beyond the repeated-root probe
- nodes whose planner consumer count and runtime reads do not match
- cheap repeated nodes that never entered materialization

## Workload Boundary

L2 first-wave validation is limited to:

- `repeated_heavy`
- `multi_consumer_dag`

`native_heavy` remains a probe. It can inform future danger-zone design, but it
does not enter the first active-drop wave.

The first active-drop validation is documented in
[L2.1 Active Lifecycle First Wave](l2_1_active_lifecycle_first_wave.md).
