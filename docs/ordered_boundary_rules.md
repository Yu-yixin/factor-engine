# Ordered Boundary Rules

This document defines the current correctness boundary for ordered roots.

## 1. Input classes

Ordered roots may consume five relevant input classes:

- `pointwise`
- `cross`
- `grouped`
- `ordered`
- `segmented`

The rule of thumb is:

- direct ordered execution is safe for `pointwise` and already-ordered inputs
- direct ordered execution is **not** assumed safe for `cross` or `grouped` inputs
- audited families must insert a materialization barrier before ordered rolling execution
- segmented child expressions are outside the current ordered audit guarantee surface
- no unsafe combination should silently drop back to the plain `compiled` path

## 2. Family rules

### `rolling_single`

Members:

- `ts_mean`
- `ts_std`
- `ts_sum`
- `ts_min`
- `ts_max`
- `ts_median`
- `skew`
- `kurt`

Rules:

- input `pointwise` -> keep `compiled`
- input `ordered` -> keep `compiled`
- input `cross` -> route to `materialized_ordered`
- input `grouped` -> route to `materialized_ordered`
- input `segmented` -> current planner keeps the expression on `segmented`; this is isolated behavior, not audited widening

### `pair`

Members:

- `corr`
- `cov`

Rules:

- both inputs `pointwise` or `ordered` -> keep `compiled`
- either input `cross` -> route to `materialized_ordered`
- either input `grouped` -> route to `materialized_ordered`
- either input `segmented` -> current planner keeps the expression on `segmented`; this is isolated behavior, not audited widening

### `positional`

Members:

- `argmax`
- `argmin`

Rules:

- input `pointwise` -> keep `compiled`
- input `ordered` -> keep `compiled`
- input `cross` -> route to `materialized_ordered`
- input `grouped` -> route to `materialized_ordered`
- input `segmented` -> current planner keeps the expression on `segmented`; this is isolated behavior, not audited widening

### `rank`

Members:

- `ts_rank`

Rules:

- input `pointwise` -> keep `compiled`
- input `ordered` -> keep `compiled`
- input `cross` -> route to `materialized_ordered`
- input `grouped` -> route to `materialized_ordered`
- input `segmented` -> current planner keeps the expression on `segmented`; this is isolated behavior, not audited widening

## 3. Supported materialized child routes

Current `materialized_ordered` support accepts child expressions that end up as:

- `compiled`
- `staged`

This means audited ordered roots may safely consume:

- `rank(close)`
- `demean(close)`
- `group_rank(close, industry)`
- `group_demean(close, industry)`
- staged forms such as `demean(ts_rank(close, 2))`

Current support does **not** claim full arbitrary nested-window generality.

Current support does not include segmented child expressions in the audited ordered guarantee. In the current implementation, any expression that contains segmented windows is kept on the `segmented` route rather than being treated as audited `materialized_ordered` widening.

## 4. Blocking rule

No unaudited ordered root may silently consume `cross` or `grouped` child expressions through the main compiled path.

If the family is audited:

- force `materialized_ordered`

If the family is not audited:

- raise a planning error instead of silently changing semantics

If the child route falls outside current audited support, such as segmented children:

- current implementation keeps the expression on `segmented`, records it as outside the audited boundary, and does not treat it as an approved ordered widening
- future closure work still needs to normalize this into one canonical registry policy so tests/docs/planner cannot drift

## 5. Test requirement

Any ordered boundary change must include split-step tests for:

- `pointwise`
- `cross`
- `grouped`

At minimum, nested execution must match manual stepwise materialization for the audited family before the route is widened.

Guardrail tests should also assert:

- planner route selection directly
- audit completeness against registry-defined ordered roots
- row alignment and grouped-boundary invariants for representative materialized paths
- segmented-child combinations do not silently downgrade to `compiled`
