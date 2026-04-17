# DAG / CSE Foundation

## Scope

This work moves the next optimization layer above executor-only lifecycle tweaks.

The current priority is:

1. stable value identity
2. shared dependency graph
3. limited heavy-node CSE decisions
4. node-aware materialization/result-store metadata
5. executor-native reuse for shared expensive nodes

It does not add ref-count drop, last-use drop scheduling, native buffer pooling, allocator work, or a full global DAG optimizer.

## R1 Identity

`ExpressionDagBuilder` builds canonical identities from AST nodes. Identity includes:

- node kind
- operator or function name
- ordered/window-sensitive function metadata
- engine time/code column context for functions that require those columns
- positional arguments in order
- normalized keyword arguments
- constants and child identities

`rank`, `group_rank`, and `ts_rank` normalize omitted `ascending=false` and `pct=false` defaults into the canonical key. This allows `rank(close)` and `rank(close, ascending=false, pct=false)` to share identity while keeping `rank(close, pct=true)` separate.

`FactorEngine.inspect_dag(...)` returns:

- AST node count
- DAG node count
- deduplicated nodes
- per-node identity
- dependencies
- consumers
- output bindings

## R2 Limited CSE

The first CSE policy is deliberately narrow:

- repeated expensive nodes become materialization candidates
- repeated cheap nodes stay inline
- ordered/time-series/window nodes are expensive
- cross-sectional nodes are medium
- variables, constants, arithmetic wrappers, and simple boolean structure are cheap

The planner can explain each repeated node with:

- `share_decision`
- `share_reason`
- `cost_class`
- `materialization_kind`
- `materialization_reason`
- `materialization_eligibility`

This is not full CSE. It is a first explicit sharing surface for high-value repeated work.

## R3 Materialization Boundary

The first node-aware result store is keyed by DAG node id and separates:

- `final`
- `shared_intermediate`
- `ephemeral`

The planner remains deliberately conservative: only repeated expensive nodes become materialization
candidates, while cheap repeated nodes stay inline.

Profiling records DAG/materialization metrics:

- `ast_node_count`
- `dag_node_count`
- `deduplicated_node_count`
- `shared_node_count`
- `materialized_node_count`
- `expensive_node_count`
- `result_store_peak_entry_count`
- `finalize_time_ms`

This creates the bridge needed for future lifecycle work without adding new drop behavior now.

## R4 Executor-Native Reuse

Executor-native reuse closes the loop between planner decisions and execution:

```text
shared + expensive node
-> materialize once as a DAG-owned helper column
-> rewrite later compiled ordered expressions to read that helper column
-> record compute and store-hit economics
```

`FactorEngine.evaluate_many(..., dag_cse=False)` disables this execution-level reuse for
benchmark comparison. It does not change expression semantics.

P4 profiling splits R4 economics into:

- `total_compute_calls`
- `estimated_unshared_compute_calls`
- `node_store_compute_calls`
- `compiled_output_heavy_occurrence_count`
- `compiled_fallback_eval_count`
- `node_store_read_count`
- `reuse_consumer_count`
- `shared_node_hit_rate`
- `node_store_compute_time_ms`
- `compiled_output_eval_time_ms`
- `restore_assemble_time_ms`
- `append_time_ms`
- `finalize_time_ms`
- `store_write_time_ms`
- `store_hit_time_ms`
- `latest_node_execution_details.jsonl`

Each node execution detail includes:

- `node_id`
- `consumer_count`
- `reuse_consumer_count`
- `compute_count`
- `node_store_read_count`
- compute/store timing fields

The intended invariant for repeated heavy nodes is:

- the shared node computes once
- later consumers read from the node-aware store
- cheap repeated nodes do not enter the store

## Lifecycle Boundary

Lifecycle expansion is frozen at this layer. Current DAG/CSE structures reserve the data needed for future lifecycle:

- consumer count
- ref-count surface
- last-use planning
- drop eligibility

But actual drop scheduling remains out of scope until node identity, sharing, and materialization policy are stable.

## Validation

Run:

```powershell
$env:PYTHONPATH="src;.venv\Lib\site-packages"
python -m pytest tests\test_dag_cse.py -q
```

The focused tests lock:

- repeated heavy subexpressions deduplicate to one DAG node
- default keyword canonicalization does not merge semantically different options
- repeated cheap expressions remain inline
- repeated heavy positional work executes once
- profiling records DAG and node result-store metrics
- repeated heavy compiled subexpressions compute once and record store hits
- `dag_cse=False` preserves results while disabling executor-native store hits
- P4 attribution keeps heavy compiled eval out of `finalize_time_ms`
- store reads and reuse consumer counts are separate
- L1 planner lifecycle metadata exposes producer/consumer/last-use/ref-count/drop-candidate fields
- L1 runtime trace records materialized/read/release-lag observability without active drop
- repeated-heavy lifecycle consumer steps preserve dependency multiplicity, so
  `ts_rank(...) + ts_rank(...)` records two planner consumers even when both
  reads happen in one output-evaluation step
- L1.5 adds explicit restore/append/finalize/batch-end steps, structural
  release lag, finalize retention lag, and bytes-step potential savings so L2
  can rank drop candidates before any active drop exists

For executor-native reuse benchmarking on `data.parquet`:

```powershell
.venv\Scripts\python.exe examples\benchmark_r4_executor_reuse.py --data data\data.parquet --consumer-counts 1,2,4,8
```
