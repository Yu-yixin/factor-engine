# Materialization Boundary

P4 closes the first materialization boundary for DAG/CSE work. The current policy
is conservative by design.

## Eligibility Matrix

| shared | expensive | restore-heavy | eligibility | reason |
| --- | --- | --- | --- | --- |
| no | no | no | `inline_required` | `none` |
| yes | no | no | `inline_required` | `none` |
| no | yes | no | `inline_required` | `none` |
| yes | yes | yes | `materialize_for_both` | `shared_reuse_and_path_normalization` |

The first implementation treats repeated expensive ordered/window nodes in
compiled ordered consumers as restore-heavy because leaving them inline pushes
heavy evaluation into final output evaluation.

## Allow Zone

- repeated expensive ordered/window nodes
- repeated native-sensitive positional roots when they are visible as repeated
  expensive DAG nodes
- repeated heavy multi-consumer DAG nodes in compiled ordered consumers

## Deny Zone

- cheap repeated nodes
- arithmetic wrappers and simple boolean structure
- single-consumer expensive nodes in this phase
- shared low-value nodes where store/write/read costs can dominate

## Lifecycle Meaning

Only materialized shared intermediates are future lifecycle candidates. Even then,
P4 only marks eligibility. It does not drop, evict, or shrink the store.

Lifecycle may later consume:

- `materialization_eligibility`
- `materialization_reason`
- `consumer_count`
- `reuse_consumer_count`
- materialized residency traces

Cheap inline nodes and final outputs are not lifecycle-managed intermediates.
