# Capability Upgrade Protocol

This document defines what must happen whenever Factor Engine gains a new
system capability. It exists to prevent old operator rules from drifting after
planner, native, lifecycle, memory, or parallel execution upgrades.

## Mandatory Update Rule

Every capability upgrade must update this folder and
`docs/operator_addition_guide.md`.

Capability upgrade means any change to:

- DSL semantics;
- registry or function contract model;
- validator capability;
- physical properties or operator contracts;
- planner routes;
- DAG/CSE identity or materialization policy;
- node-store lifecycle;
- helper-column lifecycle;
- native buffer lifecycle;
- native kernel ABI;
- CPU parallel execution;
- frame projection/materialization discipline;
- M4 structural optimization boundary;
- profiling schema that affects acceptance decisions.

## Required Review Checklist

For every capability upgrade, answer these questions.

### 1. What New Operator Families Become Acceptable?

Examples:

- native rolling reducer framework may unblock `product`;
- weighted rolling framework may unblock `decay_linear`;
- group-aware contract may unblock `indneutralize`;
- multi-output schema may unblock model/stat decomposition operators.

Update:

- `future_operator_roadmap.md`;
- `operator_addition_guide.md`;
- relevant ordered/native/lifecycle docs.

### 2. What Previously Blocked Families Remain Blocked?

Do not assume a broad unlock. Example:

If `product` becomes nativeable, that does not automatically unlock
`rolling_ols`, `quantile`, or UDF reducers.

Update blocker reasons explicitly.

### 3. Did The Accepted Boundary Change?

If yes, update:

- accepted operator classes;
- denied operator classes;
- required tests;
- route audit matrix;
- lifecycle allowlist/denylist;
- benchmark gates.

### 4. Is Profiling Still Sufficient?

If a new capability creates a new kind of memory or compute object, profiling
must expose it before active optimization is accepted.

Examples:

- native scratch state;
- multi-output bundles;
- per-worker buffers;
- segment precompute cache.

### 5. Are Frozen Layers Still Frozen?

If a change touches M2 or M4 freeze boundaries, it is not a small operator
addition. It requires an architecture phase and a freeze-review update.

## Required Files To Check

At minimum, review:

- `docs/strategy/README.md`
- `docs/strategy/future_operator_roadmap.md`
- `docs/strategy/native_runtime_strategy.md`
- `docs/strategy/memory_and_lifecycle_strategy.md`
- `docs/strategy/parallel_execution_strategy.md`
- `docs/operator_addition_guide.md`
- `docs/functions.md`
- `docs/ordered_roots_matrix.md`
- `docs/ordered_boundary_rules.md`
- `docs/ordered_correctness_audit.md`

If the capability touches lifecycle:

- `docs/history/architecture/lifecycle_entry_gate.md`
- relevant L1/L2/L3 architecture documents

If the capability touches M3/M4:

- `docs/history/architecture/m3_auto_pipeline_and_m4_bridge.md`

## Capability Upgrade Record Template

Use this template in the PR or architecture note.

```yaml
capability_upgrade:
  id: ...
  date: YYYY-MM-DD
  capability_area:
    - native_kernel
    - planner_route
    - lifecycle
    - parallel
    - materialization
  summary: ...
  newly_acceptable_operator_families:
    - ...
  still_blocked_operator_families:
    - ...
  profiling_changes:
    - ...
  lifecycle_changes:
    - ...
  route_changes:
    - ...
  docs_updated:
    - docs/strategy/...
    - docs/operator_addition_guide.md
  tests_added:
    - ...
  freeze_boundary_impact:
    m2: none | reviewed | changed
    m3: none | reviewed | changed
    m4: none | reviewed | changed
```

## Release Gate

A capability upgrade is not complete until:

1. docs are updated;
2. acceptance boundaries are updated;
3. tests cover the new boundary;
4. profiling can observe the new behavior;
5. frozen layer impact is explicitly stated.

