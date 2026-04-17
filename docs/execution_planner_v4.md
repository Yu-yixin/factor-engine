# Execution Planner V4

## 1. Goal

`execution_planner_v4` is still not full DAG/CSE. Its goal is to move batch staged execution one step closer to a real graph executor by making planner output:

- explicit staged nodes
- explicit dependency edges
- explicit output bindings

With this shape in place, executor no longer needs to infer staged prefix structure from ad-hoc caches. It can execute planner-owned nodes in dependency order.

## 2. What Changed From V3

V3 already introduced:

- stable expression keys
- stable staged step keys
- planner-side batch source/prefix planning
- conservative batch reuse for identical staged source and identical staged prefix

V4 adds one more layer of structure:

- `BatchStagedNode`
- `BatchStagedOutputBinding`

This turns batch staged planning into a graph-like intermediate representation.

## 3. New Planner Structures

### 3.1 `BatchStagedNode`

Each staged node now carries:

- `cache_key`
- `kind`
- `depends_on_cache_key`
- `expr` for source nodes
- `step` for prefix nodes
- `steps` for prefix lineage
- `consumer_outputs`

Current node kinds are:

- `source`
- `prefix`

### 3.2 `BatchStagedOutputBinding`

Each staged batch output now binds:

- `output_name`
- `cache_key`

So planner explicitly tells executor which final staged node should back each output column.

## 4. Execution Model

Current staged batch execution now follows this shape:

1. planner builds `BatchExecutionPlan`
2. planner emits staged nodes in dependency-safe order
3. executor materializes each staged node once
4. executor uses output bindings to alias final node results to requested output columns

This is still conservative:

- no arbitrary subgraph sharing
- no route-crossing graph
- no cost model

But it is now much closer to a topology-driven executor than the older source/prefix-specific logic.

## 5. Why This Matters

This change separates responsibilities more clearly:

### planner

- owns staged graph shape
- owns dependency metadata
- owns final output bindings

### executor

- executes planner-owned nodes
- materializes each node at most once inside the batch
- restores ordered output rows as before

That separation is important because full DAG/CSE should be a planner evolution first, not another layer of executor special cases.

## 6. What V4 Still Does Not Do

V4 does not yet implement:

- arbitrary shared subgraph extraction
- cross-route graph nodes
- topological optimization passes
- graph-level cost-based reordering

The system is now graph-shaped, but still limited to the conservative staged source/prefix subset.

## 7. Recommended Next Step

The most natural next step after V4 is:

1. benchmark batch staged workloads with shared prefixes
2. confirm the planner-owned graph shape is stable
3. extend sharing from full prefix reuse toward more general shared subgraphs

Only after that should the project move to true DAG/CSE planning.

## 8. One-Sentence Summary

`execution_planner_v4` turns staged batch reuse from “planner-known prefixes executed by executor-specific logic” into “planner-owned staged nodes with explicit bindings”, which is the cleanest next step before full DAG/CSE.
