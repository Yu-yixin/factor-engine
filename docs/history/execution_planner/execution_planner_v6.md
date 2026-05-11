# Execution Planner V6

## 1. Goal

`execution_planner_v6` fixes the opposite nesting direction from the earlier staged-chain work:

- V1-V5 made `cross/grouped over ordered` safe
- V6 makes `ordered corr/cov over cross/grouped inputs` safe

The concrete target is expressions such as:

- `corr(rank(open), rank(volume), 10)`
- `cov(rank(open), rank(volume), 10)`

## 2. What Was Wrong Before

Before V6, expressions like `corr(rank(open), rank(volume), 10)` were compiled as nested window expressions:

1. `rank(open)` was compiled as a cross-sectional window over `time`
2. `corr(..., ..., 10)` then wrapped those window expressions inside an ordered rolling window over `code`

That shape is not equivalent to:

1. materialize `rank(open)` and `rank(volume)` as real columns
2. run rolling `corr/cov` over those materialized columns

On real data, this could degenerate into almost-all-`NaN` results.

## 3. V6 Change

V6 adds a narrow new route:

- `materialized_ordered`

It currently applies only when:

- the root function is `corr` or `cov`
- at least one ordered input expression needs cross-sectional grouping

When the route matches, execution becomes:

1. materialize the left input expression
2. materialize the right input expression
3. run ordered rolling `corr/cov` over those materialized columns

## 4. Why This Is Deliberately Narrow

V6 does not try to solve every `ordered over cross/grouped` pattern at once.

It is intentionally scoped to:

- `corr`
- `cov`

This keeps the patch small, grounded in a reproduced real-workload failure, and easy to validate against split-step execution.

## 5. Batch Behavior

The new route also participates in `evaluate_many()`:

- compiled ordered outputs
- materialized ordered `corr/cov` outputs
- staged graph outputs

can now share one ordered prepared frame inside the same batch execution shell.

So V6 extends the ordered fusion boundary from V5 without jumping to a full DAG/CSE executor.

## 6. Validation Target

The main regression targets for V6 are:

- `corr(rank(x), rank(y), n)` matches manual split-step execution
- `cov(rank(x), rank(y), n)` matches manual split-step execution
- mixed batches with one compiled ordered expression and one materialized ordered expression still use one prepared frame

## 7. One-Sentence Summary

`execution_planner_v6` fixes `ordered over cross/grouped` for `corr/cov` by inserting explicit materialization barriers before rolling ordered execution.
