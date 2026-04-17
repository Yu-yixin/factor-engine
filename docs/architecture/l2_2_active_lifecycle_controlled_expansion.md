# L2.2 Active Lifecycle Controlled Expansion

L2.2 expands active lifecycle only inside the existing first-wave class:

- non-native
- `materialization_eligibility = materialize_for_both`
- shared and expensive
- node-store entry drop only

It still does not remove working-frame helper columns, touch native buffers, or
perform allocator/GC work.

## Wave 2A: Multiple Shared Nodes

The executor now validates multiple materialized nodes in the same batch with
independent ref-counts and drop traces.

Required signals:

- every eligible node drops
- `drop_delay_steps = 0`
- `drop_miss_count = 0`
- `multi_node_overlap_peak` records the number of simultaneously materialized
  node-store entries
- `multi_node_peak_live_bytes_before` and
  `multi_node_peak_live_bytes_after` show residency reduction
- `per_node_drop_order` records the drop sequence

## Wave 2B: Nested DAG

Planner lifecycle now respects materialization boundaries. If an inner shared
node is consumed by an outer materialized node, the inner node's consumer step is
the outer node's `producer_step`, not the final output step.

Node execution trace includes:

- `node_depth`
- `parent_node_id`
- `dependency_chain`
- `nested_drop_order_valid`

The expected order is:

```text
inner dropped_at_step <= outer dropped_at_step
```

## Wave 2C: Partial Reuse

Partial reuse uses planner consumer multiplicity and step order. A shared node
used by two asymmetric output paths is dropped only after the maximum planned
consumer step.

The safety flag is:

- `partial_reuse_safety_flag`

It remains true only when active drops occur after the last runtime read, ref
count reaches zero, and no drop miss is recorded.

## Denylist Still Applies

L2.2 still denies:

- native-heavy active drop
- cheap nodes
- blocker nodes
- non-materialized nodes
- final-output-retention nodes

`native_heavy` remains a probe for later phases.
