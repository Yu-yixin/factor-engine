# L3B.2 Helper Lifecycle Implementation Design

L3B.2 is an implementation-design stage. It does not delete DataFrame columns, does not change executor order, does not add a new active helper-drop mode, and does not include native-heavy helpers.

The purpose of this stage is to define how a future helper active-drop implementation can be made safe, narrow, observable, and reversible.

## Starting Point

L2 already supports active lifecycle for node-store entries:

```text
DAG node value -> node-store entry -> active drop after planned last use
```

L3B.1 showed that this is not enough for real frame residency. After the node-store entry is dropped, the corresponding working-frame helper column can still remain alive until batch end.

Full-data L3B.1 evidence:

| workload | helper columns | helper bytes retained | structural lag |
| --- | ---: | ---: | ---: |
| repeated_heavy | 1 | 232,389,432 | 4 |
| multi_shared_nodes | 2 | 464,778,864 | 4 |
| nested_dag | 2 | 464,778,864 | 5 |
| partial_reuse | 1 | 232,389,432 | 4 |

L3B.1 conclusion:

```text
Conclusion A: shared non-native DAG helper columns form a stable future candidate subgroup.
```

L3B.2 does not turn that conclusion into code. It defines the safe implementation shape for a future L3B.3.

## Hard Boundary

L3B.2 does not:

- delete helper columns
- change final output assembly
- change executor ordering
- add active helper drop to lifecycle_mode
- include native-heavy helpers
- include blocker-bearing helpers
- include unknown helper shapes

The only allowed outputs are design rules, scope boundaries, revalidation rules, trace fields, benchmark gates, and rollback requirements.

## Recommended Design: Batch-Safe Helper Drop

The first helper active-drop implementation should use batch-safe drop, not per-column eager drop.

Core idea:

```text
collect logically dead helper columns
revalidate them at a safe boundary
drop them as a batch by rebuilding the working-frame projection
```

This deliberately trades a small amount of delayed release for lower execution risk.

## Drop Unit

First implementation unit:

```text
helper_drop_batch
```

A `helper_drop_batch` is a set of helper columns that are all known to be:

- logically dead
- blocker-free
- not referenced by final outputs
- not referenced by future rewritten expressions
- still present in the working frame at the safe boundary

Per-column immediate drop is out of scope for the first implementation because it increases schema churn and makes timing bugs harder to diagnose.

## Step Model

Current helper observability already records created step, last use, batch end, lag, bytes, state, and blockers. Future active helper drop needs one additional safe boundary.

Required ordering:

```text
producer
-> consumer
-> helper_logical_death
-> helper_drop_safe_step
-> restore_assemble
-> append
-> finalize
-> batch_end
```

Required invariants:

```text
helper_logical_death_step >= helper_last_use_step
helper_drop_safe_step >= helper_logical_death_step
helper_dropped_at_step >= helper_drop_safe_step
```

For the first implementation, the recommended safe boundary is the output/consumer batch tail: after planned helper consumers have completed and before later restore/append/finalize logic can accidentally mix with expression evaluation.

## Safety Condition

A helper can enter a future drop batch only if all conditions hold:

```text
helper_is_drop_candidate =
    helper_lifecycle_state == "logically_dead"
    AND helper_drop_blocker_reason == ""
    AND helper_structural_lag_steps > 0
    AND helper_column_name still exists in working frame
    AND final_output_dependency_recheck == false
    AND rewrite_alias_recheck == false
    AND execution_order_recheck == stable
```

Planner observability is only the first filter. Executor revalidation is the final gate.

## Revalidation Rules

Before a future implementation removes any helper column, the executor must re-check three things.

### Final Output Dependency

The helper column must not be part of the final output projection, output source mapping, or append payload.

If the helper appears in any final output path, it must not be dropped.

### Rewrite Alias Dependency

No remaining rewritten expression may reference the helper column name.

This check protects against cases where the DAG value is logically dead but a later physical expression still reads the helper alias.

### Execution Order Certainty

The executor must be at a known safe boundary.

If the current frame can still be consumed by route-local restore, late select, append, or fallback logic that was not included in the helper last-use model, the helper must not be dropped.

## Future First-Wave Allowlist

The first implementation wave should be narrower than the L3B.1 candidate set.

Allowed in L3B.3 first wave:

- `repeated_heavy`
- `multi_shared_nodes`
- `partial_reuse`
- shared non-native helper columns
- `helper_lifecycle_state = logically_dead`
- `helper_drop_blocker_reason = ""`
- `helper_structural_lag_steps > 0`

Reason:

These shapes validate the important helper-drop cases without introducing nested frame-ordering risk.

## Future First-Wave Denylist

The first implementation wave must exclude:

- `nested_dag`
- native-heavy helpers
- final-output-source columns
- blocker-bearing helpers
- non-shared helpers
- helper columns with `execution_order_uncertain`
- helper columns with `rewrite_alias_dependency`
- helper columns whose final-output dependency cannot be revalidated

`nested_dag` remains a future candidate, but it should not be included in the first active helper-drop wave. It passed L3B.1 acceptance, but nested frame-level order is more sensitive than node-store order.

## Drop Action

Future helper drop should remove columns through an explicit projection operation:

```text
working_frame = working_frame.select(columns_to_keep)
```

It should not rely on opaque side effects, nulling columns, allocator tricks, or GC behavior.

This keeps the behavior explainable:

```text
before schema -> drop projection -> after schema
```

## Required Future Trace Fields

Per-helper trace:

```text
helper_drop_candidate
helper_logical_death_step
helper_drop_safe_step
helper_drop_revalidated
helper_dropped_at_step
helper_drop_delay_steps
helper_drop_missed
helper_drop_miss_reason
```

Every dropped helper must have a complete trace. Every not-dropped candidate must explain why it missed.

## Required Future Summary Metrics

Summary fields:

```text
helper_dropped_count
helper_drop_miss_count
helper_peak_live_bytes_before_drop
helper_peak_live_bytes_after_drop
helper_frame_width_before_drop
helper_frame_width_after_drop
helper_drop_delay_steps_avg
helper_drop_delay_steps_max
```

The implementation should prove both memory-shape improvement and low execution overhead:

```text
helper bytes before > helper bytes after
frame width before > frame width after
total sec has no structural regression
```

## Benchmark Gate For L3B.3

First active implementation must run only:

```text
repeated_heavy
multi_shared_nodes
partial_reuse
```

Each workload must compare helper-drop disabled vs enabled and report:

| workload | helper drop | dropped | miss | bytes before | bytes after | frame width before | frame width after | delay avg | sec |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |

Pass criteria:

- dropped helper count is greater than zero
- helper drop miss count is zero
- drop delay is near zero at the safe boundary
- helper live bytes decrease
- frame width decreases
- final outputs are identical
- total time has no structural regression

## Rollback And Feature Gate

L3B.2 does not introduce a new runtime mode.

Before L3B.3 implementation starts, active helper drop must have an explicit, default-off gate. The gate must be separate enough that existing `lifecycle_mode=first_wave` node-store behavior remains stable and comparable.

Rollback requirement:

```text
helper active drop disabled -> current L2/L3B behavior exactly preserved
```

## Risk Register

### Early Drop

Risk: a helper is removed before a late rewritten expression or output assemble path reads it.

Mitigation: executor-side final output and rewrite alias revalidation.

### Schema Churn

Risk: repeated per-column drop causes DataFrame projection overhead and noisy timing.

Mitigation: first implementation uses batch-safe drop only.

### Planner And Executor Drift

Risk: planner marks a helper as logically dead, but executor still has a physical dependency.

Mitigation: planner candidate filtering plus executor revalidation. Planner metadata is not sufficient to authorize deletion.

### Low Net Value

Risk: projection cost exceeds memory residency gain.

Mitigation: benchmark must report bytes, frame width, and time deltas together.

## Design Conclusion

Batch-safe helper drop is the correct first implementation design.

The future implementation should not be global. It should start with a small allowlist:

```text
repeated_heavy
multi_shared_nodes
partial_reuse
```

It should exclude `nested_dag` in the first wave despite L3B.1 acceptance, and it should continue excluding native-heavy helpers entirely.

Next stage:

```text
L3B.3 helper first-wave active drop
```

L3B.3 should still be narrow: store-entry lifecycle remains L2, helper active drop remains frame-level and default-off, and no native-heavy active drop is allowed.
