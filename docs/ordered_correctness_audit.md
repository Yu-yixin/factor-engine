# Ordered Correctness Audit

## Goal

This audit closes the current ordered execution correctness gap without expanding into DAG/CSE, grammar work, workflow schema work, or performance-only changes.

The target is narrow:

- inventory ordered roots
- define family-level boundary rules
- add split-step correctness tests
- route audited unsafe cases to safe materialization
- document what is now safe and what still remains outside scope

## Scope outcome

Audited families in this pass:

- `rolling_single`
- `pair`
- `positional`
- `rank`

Audited roots in this pass:

- `ts_mean`
- `ts_std`
- `ts_sum`
- `ts_min`
- `ts_max`
- `ts_median`
- `skew`
- `kurt`
- `corr`
- `cov`
- `argmax`
- `argmin`
- `ts_rank`

## Route decision

Current rule:

- keep direct `compiled` execution for plain pointwise or already-ordered children
- insert `materialized_ordered` for audited roots consuming `cross` or `grouped` children
- keep expressions containing segmented windows on the `segmented` route; this prevents silent fallback to plain `compiled`, but it is not part of the audited widening claim

This keeps correctness explicit and does not claim a generalized nested-window planner.

## Current Landed State

The currently landed work includes:

- audited ordered coverage for `rolling_single`, `pair`, `positional`, and `rank`
- `materialized_ordered` execution for audited `cross` and `grouped` child cases
- route inspection support through `FactorEngine.inspect_plan(...)` and `ExecutionPlanner.inspect_route(...)`
- registry-backed audit inventory helpers through `get_ordered_roots()` and `get_ordered_audit_matrix()`
- defensive tests for split-step equality, route selection, completeness, row alignment, grouped boundaries, and representative null behavior

## Test strategy

`tests/test_ordered_audit.py` covers:

- inventory-backed route expectations for all audited roots
- split-step equality between nested and manual materialized execution
- grouped cross-sectional child cases for all audited families
- negative coverage that segmented child combinations do not silently fall back to the plain `compiled` path
- route-trace assertions via planner inspection support
- audit completeness checks against registry-defined ordered roots
- structural invariants such as row alignment, grouped-boundary preservation, and representative null behavior

## What this audit does not claim

- full arbitrary nested-window correctness
- generalized graph execution
- cross-expression CSE
- performance optimality of the newly widened families

## Remaining issues

- The audited widening still depends on `materialized_ordered` only accepting child expressions that resolve through `compiled` or `staged` paths.
- If a new ordered root is added later, it must be explicitly inventoried, documented, and tested before consuming `cross` or `grouped` children.
- Ordered policy is not yet fully normalized into one canonical per-child-class structure in `registry.py`; root inventory and route rules are still represented through multiple helpers and planner logic.
- `inspect_plan(...)` is useful today, but the closure target contract fields such as `root`, `family`, `child_class`, and `guard_mode` are not yet fully stabilized in code.
- Ordered docs are still synchronized manually; doc drift protection has not yet been mechanized.
- This audit is correctness-first; follow-up optimization should still be gated by benchmark evidence.

## Guardrail hardening

The current hardening layer adds three closure checks:

- route-trace inspection through `FactorEngine.inspect_plan(...)` and `ExecutionPlanner.inspect_route(...)`
- registry-backed completeness checks through `get_ordered_roots()` and `get_ordered_audit_matrix()`
- negative tests that ensure segmented-child combinations do not silently fall back to the main compiled path

## Closure Status

Closure work has been analyzed but not fully landed yet.

The most important not-yet-landed items are:

- one canonical ordered policy structure in `src/factor_engine/registry.py`
- planner behavior derived mechanically from that canonical policy
- a fully stabilized route-inspection contract for closure tests
- doc drift protection that validates ordered docs against code policy instead of relying on manual sync

This document set therefore records the current landed truth and the remaining closure gap, rather than claiming that the full closure milestone is already complete.
