# Path Normalization

Path normalization is the P4 name for lifting repeated expensive ordered work out
of final output evaluation and into an explicit materialized DAG helper column.

## Before

```text
final output restore
-> evaluate repeated heavy compiled expression
-> assemble output
```

This made CSE-off profiles look like `finalize_time_ms` was the bottleneck even
when the restore stage was actually executing heavy rolling or positional work.

## After

```text
shared expensive DAG node
-> compute once as __dag_node*
-> final output expression reads helper column
-> restore assembles already-evaluated outputs
```

The first supported rule is intentionally narrow:

- repeated expensive ordered/window nodes are eligible
- repeated cheap nodes stay inline
- materialization reason is `shared_reuse_and_path_normalization`
- the executor applies this only in the compiled ordered consumer path

## Attribution

P4 keeps the two gains separate:

- compute reduction: `estimated_unshared_compute_calls` vs
  `node_store_compute_calls`
- path normalization: `compiled_output_eval_time_ms` and
  `restore_assemble_time_ms`

When CSE-on succeeds, repeated heavy cases should show:

```text
node_store_compute_calls = 1
compiled_output_heavy_occurrence_count = 0
node_store_read_count grows with repeated reads
```

## Non-Goals

This is not full graph execution, full CSE, or lifecycle drop scheduling. Route
local stage caches still exist and remain valid for staged/materialized/positional
families that already have explicit reuse paths.
