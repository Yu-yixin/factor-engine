# Ordered Roots Matrix

This matrix is the current landed audit inventory for ordered roots in Factor Engine.

The current source of truth in code is still split inside `src/factor_engine/registry.py` via:

- `get_ordered_roots()`
- `get_ordered_audit_matrix()`

This means the repo can already enforce root-level audit completeness, but per-child-class canonical policy closure has not been landed yet.

| name | arity | family | current_route | risk | test_status | audit_status |
| --- | ---: | --- | --- | --- | --- | --- |
| `ts_mean` | 2 | `rolling_single` | `materialized_ordered` when child is cross/grouped, else `compiled` | medium | split-step covered | audited |
| `ts_std` | 2 | `rolling_single` | `materialized_ordered` when child is cross/grouped, else `compiled` | medium | split-step covered | audited |
| `ts_sum` | 2 | `rolling_single` | `materialized_ordered` when child is cross/grouped, else `compiled` | medium | split-step covered | audited |
| `ts_min` | 2 | `rolling_single` | `materialized_ordered` when child is cross/grouped, else `compiled` | medium | split-step covered | audited |
| `ts_max` | 2 | `rolling_single` | `materialized_ordered` when child is cross/grouped, else `compiled` | medium | split-step covered | audited |
| `ts_median` | 2 | `rolling_single` | `materialized_ordered` when child is cross/grouped, else `compiled` | medium | split-step covered | audited |
| `skew` | 2 | `rolling_single` | `materialized_ordered` when child is cross/grouped, else `compiled` | medium | split-step covered | audited |
| `kurt` | 2 | `rolling_single` | `materialized_ordered` when child is cross/grouped, else `compiled` | medium | split-step covered | audited |
| `corr` | 3 | `pair` | `materialized_ordered` when either child is cross/grouped, else `compiled` | high | split-step covered | audited |
| `cov` | 3 | `pair` | `materialized_ordered` when either child is cross/grouped, else `compiled` | high | split-step covered | audited |
| `argmax` | 2 | `positional` | `materialized_ordered` when child is cross/grouped, else `positional_ordered` | medium | split-step covered | audited |
| `argmin` | 2 | `positional` | `materialized_ordered` when child is cross/grouped, else `positional_ordered` | medium | split-step covered | audited |
| `ts_rank` | 2 | `rank` | `materialized_ordered` when child is cross/grouped, else `compiled` | medium | split-step covered | audited |

## Notes

- Current audited cross/grouped inputs are explicit cross-sectional and grouped cross-sectional expressions such as `rank(...)`, `demean(...)`, `zscore(...)`, `group_rank(...)`, `group_demean(...)`, and `group_zscore(...)`.
- Current route widening is intentional and still narrow: audited ordered roots may consume `compiled` or `staged` child expressions through a materialization barrier, but this is not a full generalized nested-window optimizer.
- If a new ordered root is introduced, it should stay out of the main `compiled` path for cross/grouped children until it is added to this matrix, covered by split-step tests, and documented in the boundary rules.
- Completeness is enforced by test: if a new rolling ordered root is added to the registry without a matching audit entry, `tests/integration/test_ordered_audit.py` must fail.

## Current Landed Guardrails

- `FactorEngine.inspect_plan(...)` and `ExecutionPlanner.inspect_route(...)` can expose the current selected route and `materialized_ordered` payload fields for tests.
- Audited `cross` and `grouped` child cases are currently routed to `materialized_ordered` rather than silently remaining on the plain `compiled` path.
- Segmented-child combinations are currently kept off the plain `compiled` path by the planner, but they are not part of the audited ordered guarantee surface.

## Known Closure Gaps

- The repository does not yet have one canonical per-child-class ordered policy structure in `registry.py`.
- Planner routing logic, audit inventory, and docs still require manual synchronization.
- Segmented-child behavior is only documented as current behavior; it is not yet encoded as a finalized canonical ordered policy contract.
