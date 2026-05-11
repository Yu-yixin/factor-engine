# L3B.3 Helper First-Wave Active Drop

L3B.3 implements the first active lifecycle drop for working-frame helper columns.

This is not full helper lifecycle. It is a narrow, batch-safe, allowlist-only implementation.

## Scope

Allowed helper class:

```text
shared non-native helper
helper_lifecycle_state = logically_dead
helper_drop_blocker_reason = ""
helper_structural_lag_steps > 0
materialization_eligibility = materialize_for_both
workload in repeated_heavy, multi_shared_nodes, partial_reuse
```

Explicitly denied:

- `nested_dag`
- native-heavy helpers
- final-output-source columns
- non-shared helpers
- blocker-bearing helpers
- `execution_order_uncertain`
- `rewrite_alias_dependency`
- unknown workload shapes

## API Gate

Helper drop has its own mode:

```text
helper_lifecycle_mode = off | first_wave
```

This is separate from node-store lifecycle:

```text
lifecycle_mode = off | first_wave
```

The split is intentional. L2 drops node-store entries. L3B.3 drops working-frame helper columns.

## Candidate Function

All helper active-drop eligibility flows through one function:

```text
is_first_wave_helper_candidate(...)
```

The function requires:

- recognized first-wave workload
- logically-dead helper state
- empty helper blocker
- positive structural lag
- positive helper bytes
- shared-intermediate materialization
- non-native node class
- no nested materialized helper dependency

## Execution Strategy

L3B.3 uses Batch-Safe Helper Drop:

```text
collect logically-dead helpers
-> executor revalidation
-> batch projection drop
-> trace and summarize
```

The drop action is an explicit projection:

```text
working_frame = working_frame.select(columns_to_keep)
```

No allocator tricks, GC hooks, native buffer release, or opaque column mutation are used.

## Safe Step

For the first wave:

```text
helper_logical_death_step = helper_last_use_step
helper_drop_safe_step = restore_assemble_step
helper_dropped_at_step = helper_drop_safe_step
```

Required invariants:

```text
helper_drop_safe_step >= helper_last_use_step
helper_dropped_at_step >= helper_drop_safe_step
```

## Executor Revalidation

Planner/observability metadata is only a first filter. The executor revalidates before dropping:

- helper column still exists in frame
- helper is not a final output source
- helper blocker remains empty
- helper is still a first-wave candidate
- helper has a safe step

Failed revalidation creates a helper miss trace instead of silently skipping.

## Trace Fields

Per-node helper trace now includes:

```text
helper_drop_candidate
helper_logical_death_step
helper_drop_safe_step
helper_drop_revalidated
helper_dropped_at_step
helper_drop_delay_steps
helper_drop_reason
helper_drop_missed
helper_drop_miss_reason
```

Summary fields now include:

```text
helper_lifecycle_mode
helper_dropped_count
helper_drop_miss_count
helper_peak_live_bytes_before_drop
helper_peak_live_bytes_after_drop
helper_frame_width_before_drop
helper_frame_width_after_drop
helper_drop_delay_steps_avg
helper_drop_delay_steps_max
helper_lifecycle_effective
```

`helper_lifecycle_effective` is true when:

```text
helper_dropped_count > 0
AND helper_peak_live_bytes_after_drop < helper_peak_live_bytes_before_drop
AND helper_drop_miss_count = 0
AND helper_drop_delay_steps_max = 0
```

## Validation

Locked tests:

- repeated helper active drop is batch-safe
- multiple shared helpers drop as one batch
- partial reuse waits until safe step
- nested DAG remains denied from helper first wave
- single-source helper candidate function allowlist/denylist

Smoke benchmark:

```text
benchmarks/scripts/benchmark_r4_executor_reuse.py
  --rows 1000
  --consumer-counts 2
  --workloads repeated_heavy,multi_shared_nodes,partial_reuse,nested_dag
  --lifecycle-mode first_wave
  --helper-lifecycle-mode first_wave
```

Observed smoke result:

- `repeated_heavy` CSE-on: helper dropped, bytes after drop = 0
- `multi_shared_nodes` CSE-on: helpers dropped, bytes after drop = 0
- `partial_reuse` CSE-on: helper dropped, bytes after drop = 0
- `nested_dag` CSE-on: helper dropped count = 0

1M acceptance comparison with `cse=True` and node-store `lifecycle_mode=first_wave`:

| workload | helper mode | dropped | miss | before bytes | after bytes | frame before | frame after | delay avg |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| repeated_heavy | off | 0 | 0 | 8,000,000 | 8,000,000 | 11 | 11 | 0.000 |
| repeated_heavy | first_wave | 1 | 0 | 8,000,000 | 0 | 11 | 10 | 0.000 |
| multi_shared_nodes | off | 0 | 0 | 16,000,000 | 16,000,000 | 12 | 12 | 0.000 |
| multi_shared_nodes | first_wave | 2 | 0 | 16,000,000 | 0 | 12 | 10 | 0.000 |
| partial_reuse | off | 0 | 0 | 8,000,000 | 8,000,000 | 12 | 12 | 0.000 |
| partial_reuse | first_wave | 1 | 0 | 8,000,000 | 0 | 12 | 11 | 0.000 |
| nested_dag | off | 0 | 0 | 16,000,000 | 16,000,000 | 12 | 12 | 0.000 |
| nested_dag | first_wave | 0 | 0 | 16,000,000 | 16,000,000 | 12 | 12 | 0.000 |

Artifacts:

- `benchmarks/l3b3_helper_1m_off`
- `benchmarks/l3b3_helper_1m_first_wave`

## Current Boundary

L3B.3 is the first real helper active drop. It is still not:

- native-heavy lifecycle
- nested helper active drop
- full working-frame lifecycle
- native buffer lifecycle
- allocator-level memory lifecycle

Next expansion must keep the same pattern: one new complexity dimension at a time, with explicit denylist and benchmark gates.
