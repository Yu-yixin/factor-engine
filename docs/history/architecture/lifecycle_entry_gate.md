# Lifecycle Entry Gate

P4 does not implement lifecycle drops. It defines the minimum checklist before
starting L1 lifecycle observability.

## L1 First Round

L1 lifecycle observability has started with a read-only plan/trace/summarize
sequence:

1. planner-level lifecycle metadata from DAG/materialization decisions
2. executor runtime trace to validate planner last-use shape
3. profiling summary metrics for release potential

No active drop is introduced in this phase.

Planner lifecycle metadata contains:

- `producer_step`
- `consumer_steps`
- `last_use_step`
- `ref_count_initial`
- `drop_candidate`
- `drop_blocker_reason`

Runtime trace contains:

- `materialized_at_step`
- `first_read_step`
- `last_read_step`
- `retained_until_end`
- `theoretical_release_step`

Summary metrics contain:

- `lifecycle_candidate_count`
- `lifecycle_releasable_node_count`
- `lifecycle_peak_live_node_count`
- `lifecycle_peak_live_bytes_est`
- `avg_release_lag_steps`
- `max_release_lag_steps`

Planner `consumer_steps` preserve dependency multiplicity. Repeated reads inside
one compiled output can share the same step value, while multi-output consumers
usually occupy separate output-evaluation steps.

L1.5 extends this with explicit residency boundary steps:

- `restore_assemble_step`
- `append_step`
- `finalize_step`
- `batch_end_step`

`release_lag_steps` is now a compatibility alias for
`structural_release_lag_steps`, which measures
`batch_end_step - theoretical_release_step`.

## Gate 1: Attribution Is Stable

- `node_store_compute_time_ms` records node-store compute.
- `compiled_output_eval_time_ms` records final output expression evaluation.
- `restore_assemble_time_ms` records only row-order restoration and assembly.
- `append_time_ms` records final append.
- CSE-off and CSE-on both have non-zero attributed compute when heavy work is
  actually executed.

## Gate 2: Materialization Policy Is Stable

- repeated expensive ordered/window nodes can materialize
- repeated cheap nodes stay inline
- `materialization_reason` is inspectable
- `materialization_eligibility` is inspectable

## Gate 3: Store Semantics Are Clean

- `node_store_read_count` is read frequency
- `reuse_consumer_count` is consumer multiplicity
- final outputs are separate from shared intermediates
- helper-column residency is observable but not actively managed

## Gate 4: Lifecycle Starts Observational

The next stage may compute:

- ref-count inputs
- last-use candidates
- drop candidacy
- residency traces

It must not yet perform:

- active drop
- store eviction
- allocator/GC tricks
- native buffer lifetime rewrites

L2 first-wave active drop is gated by the L1.5 allowlist/denylist in
[L1.5 Residency Distance Closure](l1_5_residency_distance_closure.md). The first
active-drop workloads are limited to `repeated_heavy` and `multi_consumer_dag`;
`native_heavy` remains a probe.
