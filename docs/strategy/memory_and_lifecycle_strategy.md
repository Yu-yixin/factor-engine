# Memory And Lifecycle Strategy

Memory strategy is now a first-class part of operator design. Future operators
must describe where their values live, when those values become unnecessary, and
which layer is allowed to release them.

## Current Lifecycle Baseline

The current lifecycle system has stable boundaries:

- non-native node-store entry drop is supported;
- helper-column first-wave active drop is supported;
- pure nested helper second-wave active drop is supported;
- native-heavy active drop is not supported;
- working-frame and native-buffer deeper lifecycle remain future work;
- M2 lifecycle is frozen for the current cycle.

Future operators must not expand these boundaries silently.

## Memory Objects

Every non-trivial operator should identify which memory objects it creates.

| object | examples | current control |
| --- | --- | --- |
| node-store entry | shared intermediate value | active drop for accepted non-native classes |
| helper column | `__dag_node_*` working-frame columns | first-wave and pure nested active drop |
| output column | final user-visible result | output attach and finalize policy |
| native output buffer | native kernel output before/after attach | observable, not broadly active-drop capable |
| scratch/state buffer | rolling/order-stat/model state | future native framework requirement |
| frame projection width | active frame columns | controlled only for accepted helper paths |

## Operator Memory Contract

Before a new operator family is accepted, it should answer:

```yaml
memory_contract:
  creates_node_store_entry: true/false
  creates_helper_column: true/false
  creates_native_buffer: true/false
  creates_scratch_state: true/false
  output_width: single_column | multi_column | variable
  materialization_reason:
    - shared_reuse
    - path_normalization
    - route_required
    - final_output
  lifecycle_supported:
    node_store: yes/no
    helper_column: yes/no
    native_buffer: yes/no
    scratch_state: yes/no
```

If this contract cannot be written, the operator should not be merged as a
normal function.

## Materialization Discipline

M3 showed that not every materialization-policy idea is useful. Future
materialization changes must remain experimental and benchmark-decided.

Rules:

1. Do not materialize cheap nodes merely because they repeat.
2. Materialization must have a reason: reuse, path normalization, route
   requirement, or final output assembly.
3. Raising thresholds without recomputation guardrails is forbidden.
4. Output attach changes must be isolated behind a knob before acceptance.
5. Projection changes must prove frame width reduction without correctness loss.

## Lifecycle Entry Gates For New Families

A new operator family may enter active lifecycle only after observability proves:

- producer step;
- consumer steps;
- last use step;
- structural dependency end step if helpers are involved;
- batch/finalize/end steps;
- bytes estimate;
- retained-past-last-read behavior;
- blocker taxonomy;
- active-drop allowlist and denylist.

Native-heavy and scratch/stateful operators require an additional native
residency model before active drop.

## Future Memory Directions

### Native Buffer Lifecycle

Future native-heavy families need:

- buffer ownership handoff;
- attach/release trace;
- double-hold window accounting;
- buffer pool or allocator strategy only after observability.

### Scratch State Lifecycle

Weighted rolling, order-statistics, and rolling models need:

- state allocation estimate;
- state reuse policy;
- per-partition lifetime;
- release timing;
- benchmark evidence that state residency is worth managing.

### Multi-Output Lifecycle

Multi-output operators require:

- output bundle identity;
- per-field or bundle-level materialization policy;
- per-field final-output dependency tracking;
- helper/drop policy that does not break schema assembly.

