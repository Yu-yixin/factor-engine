# Current Strategy State

This file records the current strategic decisions that future work should treat
as the baseline.

## Frozen / Stable Layers

```yaml
system_strategy_state:
  m1_observability: stable
  m2_lifecycle: frozen
  m3_materialization_current_cycle: exhausted
  m4_structural_optimization: frozen_strong_success
```

## M2 Lifecycle State

Accepted:

- non-native node-store active drop;
- helper-column first-wave active drop;
- pure nested helper second-wave active drop.

Not accepted:

- native-heavy active drop;
- arbitrary helper-column drop;
- allocator-level lifecycle;
- unbounded second-wave expansion.

Strategic rule:

> Future operators may use existing lifecycle capabilities, but they must not
> expand lifecycle semantics inside operator implementation work.

## M3 Materialization State

M3 v1 proposal space is exhausted for the current cycle. Future changes to
attach timing, projection discipline, or materialization threshold must re-enter
the proposal -> executable -> benchmark -> score -> decision loop. They must
not be attached to ordinary operator work.

Strategic rule:

> Materialization is a discipline layer, not a place to hide operator-specific
> exceptions.

## M4 Structural Optimization State

Accepted candidates:

- `m4_cse_expand_repeated_subgraphs`
- `m4_fuse_deep_operator_chains`

Deferred candidates:

- structural materialization elimination;
- wide fan-out batching;
- heavy-path rewrite.

Strategic rule:

> M4 proved that structure is a real optimization layer, but the current cycle
> is frozen. New structural candidates require a new M4 cycle, not a side effect
> of operator addition.

## Current Operator Addition Boundary

Accepted in ordinary batches:

- clean pointwise expression operators;
- cross-sectional operators expressible by existing group expression paths;
- rolling operators only when backend-vectorized or already accepted by route
  audit;
- aliases that canonicalize to existing functions.

Blocked in ordinary batches:

- Python window callbacks;
- Python row/object loops;
- native-heavy one-offs;
- new routes;
- unprofiled native buffers;
- operators with unclear helper/materialization lifecycle.

## Product Decision

`product(x, d)` is currently not supported.

Reason:

- The available implementation path used `rolling_map`, which is a Python
  callback/object-level rolling fallback.
- This violates the current operator addition boundary.

Future condition to reopen:

- A native or backend-vectorized rolling reducer framework exists.
- Null/window semantics are defined.
- Ordered audit and lifecycle observability are updated.

Status:

```yaml
product:
  current_status: remove_from_batch
  future_family: native_rolling_reducer
  reopen_condition: native_or_backend_vectorized_reducer_framework
```

