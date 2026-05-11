# L2.3 Lifecycle Capability Hardening

L2.3 does not expand lifecycle coverage. It locks the existing active-drop capability into a stable, explicit module boundary.

## Supported Mode

Lifecycle is controlled by one mode value:

```text
lifecycle_mode = off | first_wave
```

`lifecycle=True` is kept only as a compatibility alias for `lifecycle_mode="first_wave"`. Internal executor, profiling, and benchmark behavior use the normalized mode.

## Single Source Of Truth

First-wave active drop eligibility is decided by `factor_engine.lifecycle.is_first_wave_candidate()`.

The predicate is intentionally narrow:

- `materialization_eligibility == "materialize_for_both"`
- planner `drop_candidate == true`
- planner `drop_blocker_reason == ""`
- `structural_release_lag_steps > 0`
- node lifecycle class is not `native_heavy`
- `bytes_estimate` is above the first-wave threshold

Executor active drop must not bypass this function.

## Fixed Step Model

The lifecycle step order is locked as:

```text
producer
-> consumer
-> restore_assemble
-> append
-> finalize
-> batch_end
```

Runtime assertions enforce:

- `drop_expected_step == theoretical_release_step`
- `dropped_at_step >= drop_expected_step`
- nested active-drop order remains valid

## Trace Contract

Every active drop keeps the locked fields:

- `node_id`
- `ref_count_initial`
- `ref_count_remaining_final`
- `drop_expected_step`
- `dropped_at_step`
- `drop_delay_steps`
- `drop_reason`
- `drop_missed`
- `drop_miss_reason`

Profiling also emits `lifecycle_mode` and `lifecycle_effective`.

`lifecycle_effective` is true only when:

```text
dropped_node_count > 0
AND peak_live_bytes_est_after_drop < peak_live_bytes_est_before_drop
AND drop_miss_count == 0
AND drop_delay_steps_max == 0
```

## Current Capability Boundary

Supported:

- non-native DAG nodes
- `materialize_for_both`
- shared + expensive nodes
- node-store entry drop only

Not supported:

- native-heavy active drop
- working-frame column drop
- native buffer lifecycle
- allocator or GC-level lifecycle
- unknown DAG shapes outside the validated first-wave / L2.2 boundary

## Regression Workloads

Lifecycle hardening is guarded by the existing L2.1/L2.2 workloads:

- `repeated_heavy`
- `multi_consumer_dag`
- `multi_shared_nodes`
- `nested_dag`
- `partial_reuse`

Each should be comparable under:

```text
lifecycle_mode=off
lifecycle_mode=first_wave
```

The required acceptance signals are:

- no semantic drift
- `drop_miss_count == 0`
- drop delay remains zero for first-wave candidates
- before-drop live bytes are higher than after-drop live bytes
- no structural runtime regression
