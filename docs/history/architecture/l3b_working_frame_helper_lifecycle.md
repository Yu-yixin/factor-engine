# L3B Working-Frame / Helper Column Lifecycle

L3B introduces observability for working-frame helper columns. It does not delete DataFrame columns, change executor ordering, add active frame drop, alter final output assembly, or change native-heavy policy.

## Scope

The first modeled object is the DAG materialized helper column:

```text
__dag_node...
```

These columns back materialized shared intermediates. Node-store entry lifecycle can already drop the logical store reference, but the helper column remains in the working frame until batch end.

## Helper Last Use

For an observed helper column:

```text
helper_last_use_step = max(
    DAG/planner last_use_step,
    runtime rewrite read step,
    final output usage step when applicable
)
```

The current implementation records this without deleting the column.

## Lifecycle State

Each helper receives:

```text
helper_lifecycle_state:
  active
  logically_dead
  structurally_required
  drop_blocked
```

Current meaning:

- `active`: no structural lag after helper last use.
- `logically_dead`: no blocker and `batch_end_step > helper_last_use_step`.
- `structurally_required`: final output / late select dependency keeps the column required.
- `drop_blocked`: non-output blocker exists.

## Blockers

The helper blocker taxonomy is:

```text
final_output_dependency
late_select_dependency
rewrite_alias_dependency
execution_order_uncertain
```

The first implementation emits blockers conservatively:

- `final_output_dependency` when the helper column is still a direct final output source.
- `execution_order_uncertain` for materialized non-shared helper classes not yet in the L3B target set.

## Profiling Fields

Per node:

- `helper_column_name`
- `helper_column_created_step`
- `helper_last_use_step`
- `helper_retained_until_end`
- `helper_structural_lag_steps`
- `helper_bytes_estimate`
- `helper_potential_bytes_step_savings`
- `helper_lifecycle_state`
- `helper_drop_blocker_reason`

Batch / run:

- `helper_column_count`
- `helper_releasable_count`
- `helper_blocked_count`
- `helper_peak_live_bytes`
- `helper_potential_savings`
- `helper_blocker_reasons`

## Future Candidate Rule

A helper column may become a future active-drop candidate only if:

```text
helper_lifecycle_state = logically_dead
helper_drop_blocker_reason = ""
helper_structural_lag_steps > 0
helper_bytes_estimate is meaningful at scale
```

One-vote veto blockers:

- `final_output_dependency`
- `rewrite_alias_dependency`
- `execution_order_uncertain`

## Relationship To Existing Lifecycle

| Phase | Object | Trigger |
| --- | --- | --- |
| L2 | node-store entry | DAG last use |
| L3A | native-heavy read/path/storage model | normalized read model |
| L3B | working-frame helper column | frame last use |

L3B deliberately does not change L2. It shows the remaining gap after a node-store entry is dropped: the working-frame helper column may still be retained to batch end.

## Entry Gate For Future L3B.2

Active helper-column drop is not allowed until:

- helper last-use is stable across L2 workloads
- blockers explain all retained helpers
- at least one helper class is `logically_dead` with no blocker
- benchmark reports show meaningful helper bytes and bytes-step savings
- final output correctness is protected by tests
