# L2.1 Active Lifecycle First Wave

L2.1 is a narrow active-drop validation pass. It only verifies that first-wave
allowlist nodes can be removed from the node result store after planned
ref-count reaches zero.

## Scope

Active drop is enabled only when `evaluate_many(..., lifecycle_mode="first_wave")` is used.
`lifecycle=True` remains a compatibility alias for that mode.

First-wave eligible nodes must satisfy:

- `l2_first_wave_candidate = true`
- `materialization_eligibility = materialize_for_both`
- `drop_candidate = true`
- `drop_blocker_reason = ""`
- non-native heavy node class

The first active workloads are:

- `repeated_heavy`
- `multi_consumer_dag`

`native_heavy` remains a probe and is not active-dropped in this wave.

## Drop Semantics

The executor decrements lifecycle ref-count from planner consumer multiplicity,
not from runtime read frequency.

For same-step repeated use such as:

```text
consumer_steps = [5, 5]
```

both planned consumers are settled at step `5`. For multi-consumer DAGs, each
output consumer settles its own planned step.

When all conditions hold:

```text
ref_count_remaining == 0
current_step >= last_use_step
active_drop_eligible = true
```

the node-store entry is removed and the trace records:

- `dropped_at_step`
- `drop_expected_step`
- `drop_delay_steps`
- `drop_reason = ref_count_zero`
- `ref_count_remaining_final`
- `drop_missed`
- `drop_miss_reason`

Only the node-store entry is dropped. L2.1 does not remove helper columns from
the working frame, does not force GC, and does not touch native buffers.

## Summary Metrics

Profiling adds:

- `dropped_node_count`
- `drop_hit_count`
- `drop_miss_count`
- `peak_live_node_count_after_drop`
- `peak_live_bytes_est_before_drop`
- `peak_live_bytes_est_after_drop`
- `drop_delay_steps_avg`
- `drop_delay_steps_max`

The pass is considered healthy only if repeated-heavy preserves results, drops
at the expected step, and reduces after-drop live bytes before multi-consumer DAG
is trusted.

The controlled expansion after this pass is documented in
[L2.2 Active Lifecycle Controlled Expansion](l2_2_active_lifecycle_controlled_expansion.md).
