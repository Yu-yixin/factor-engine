# DAG/CSE Refactor Plan

Phase 3.10 is a read-only map of the remaining executor core. It does not prescribe behavior changes.

## Executor DAG/CSE Function Map

Current DAG/CSE-related helpers in `src/factor_engine/executor.py`:

- `_plan_ordered_batch_stage_consumers`: counts explicit staged/materialized/positional consumers for stage registry expectations.
- `_collect_explicit_stage_consumers`: recursively walks positional and materialized ordered plans to count explicit child consumers.
- `_increment_planned_consumer`: small counter helper.
- `_explicit_stage_cache_key`: produces stage cache keys for positional and materialized ordered child stages.
- `_dag_identity_for_expr`: builds a one-output DAG to recover an expression identity.
- `_rewrite_expr_with_materialized_nodes`: rewrites expression AST nodes to materialized column references and returns node-hit counts.
- `_merge_node_hit_counts`: merges node hit-count dictionaries.
- `_count_materializable_node_occurrences`: counts materialized DAG node occurrences in an expression tree.
- `_materialize_shared_dag_nodes_on_sorted_df`: materializes shared DAG nodes, records store policy, records planned reads/consumption, registers stages, and attaches lifecycle eligibility metadata.
- `_evaluate_many_ordered_batch_plan`: main coordinator for batch DAG/CSE, staged, materialized, positional, lifecycle, profiling, restore, and output attach.

## Node Store Structures

Primary node store types live in `src/factor_engine/dag.py`:

- `DagNode`: node identity, expression, materialization policy, consumers, output names, guardrail metadata, and dependency metadata.
- `NodeResultStoreEntry`: store entry for final or materialized outputs.
- `NodeResultStore`: store policy, materialized entries, stats, read/write accounting, planned consumption, drop metadata, and reuse statistics.

Executor-owned node-store interaction points:

- `result_store = NodeResultStore()` inside `_evaluate_many_ordered_batch_plan`.
- `result_store.register_policy(...)` when batch DAG nodes are materializable.
- `result_store.put_materialized(...)` in `_materialize_shared_dag_nodes_on_sorted_df`.
- `result_store.record_reads(...)` and `result_store.record_planned_consumption(...)` for rewritten materialized-node hits.
- `result_store.put(...)` for final output entries from compiled, positional, materialized, and staged bindings.
- `result_store.materialized_entries`, `result_store.stats`, and profiling aggregation in `_record_result_store_profile`.

## Consumer Count / Last Use / Materialization Candidate Structures

Consumer and last-use facts come from two places:

- Planner/DAG facts on `DagNode`: `occurrence_count`, `consumers`, `output_names`, `materialize`, `default_materialize`, `materialization_kind`, `materialization_reason`, `materialization_eligibility`, `recomputation_expansion_if_inline`, `recomputation_guardrail_pass`.
- Lifecycle plan facts from `batch_plan.dag.lifecycle_plan_by_node_id()`: `producer_step`, `consumer_steps`, `last_use_step`, `ref_count_initial`, `drop_candidate`, `drop_blocker_reason`, `structural_release_lag_steps`, `node_depth`, `parent_node_id`, and `dependency_chain`.

Executor materialization touchpoints:

- `_materialize_shared_dag_nodes_on_sorted_df` creates physical helper columns for `DagNode.materialize`.
- `_rewrite_expr_with_materialized_nodes` changes later compiled expressions to read already materialized helper columns.
- `_count_materializable_node_occurrences` updates heavy/native-heavy runtime accounting.
- Runtime guardrail counters are filled in `_evaluate_many_ordered_batch_plan` from `batch_plan.dag.nodes`.

## Executor-Native Reuse Structures

Native-heavy reuse is represented by DAG/lifecycle accounting rather than a separate native store:

- `_node_lifecycle_class` classifies `argmax`/`argmin` identities as `native_heavy`.
- `_count_materializable_node_occurrences(..., node_lifecycle_class="native_heavy")` tracks native-heavy occurrences.
- Runtime fields include `native_heavy_node_count`, `native_heavy_forbidden_count`, `native_heavy_observable_only_count`, `native_heavy_candidate_future_count`, `native_heavy_reuse_hit_count`, `native_fallback_eval_count`, `native_buffer_reuse_proxy_hit_count`, and related logical consumer/read counters.
- `_record_result_store_profile` emits native-heavy node profiling fields based on `NodeResultStore` stats and lifecycle classification.

## Lifecycle / DAG-CSE Boundary

Lifecycle integration crosses DAG/CSE at these executor helpers:

- `_materialized_helper_has_nested_dependency`
- `_append_helper_trace_event`
- `_prepare_helper_lifecycle_metadata`
- `_revalidate_helper_drop`
- `_drop_first_wave_helper_columns`
- `_nested_drop_order_valid`
- `_assert_lifecycle_step_model`
- `_record_result_store_profile`

The key boundary is that `lifecycle.py` defines policy and classification, while executor integration decides when stored helper columns can be dropped from the active frame and how that is recorded in `NodeResultStore`.

## Profiling / DAG-CSE Boundary

Profiling integration crosses DAG/CSE at:

- `OrderedBatchRuntime` batch counters populated from `batch_plan.dag`.
- `_record_result_store_profile`, which builds `NodeExecutionDetail` records and runtime summary counters.
- `NodeResultStore` stats, which provide compute/read/store/drop timing, materialization, and lifecycle fields.
- `StageRegistry` events for `dag_shared_intermediate`, staged prefixes, materialized outputs, positional outputs, and deferred outputs.

Profiling schema fields must remain stable during any extraction.

## Safe First Extractions

Lower-risk candidates:

- DAG identity and AST rewrite helpers.
- Node hit-count merge helper.
- Materializable occurrence counting helper.
- Small result-store initialization/index helper for `dag_nodes_by_output`, `dag_identity_by_node_id`, `dag_nodes_by_identity`, and `lifecycle_plans_by_node_id`.
- Runtime DAG summary counter population from `batch_plan.dag`.
- Lifecycle helper trace append and nested dependency checks.

## Unsafe To Touch First

Do not start by moving or rewriting:

- `_evaluate_many_ordered_batch_plan` as a whole.
- `_materialize_shared_dag_nodes_on_sorted_df` execution loop if it would change materialization order.
- `_drop_first_wave_helper_columns` behavior.
- `_record_result_store_profile` field construction if it would alter profiling schema.
- Planner canonicalization or DAG identity semantics in `dag.py`.
- Any lifecycle drop decision from `lifecycle.py`.

The recommended extraction style is callback-based delegation from executor, keeping existing wrappers until tests and external references prove they are unnecessary.
