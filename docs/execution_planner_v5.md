# Execution Planner V5

## 1. Goal

`execution_planner_v5` does not introduce full DAG/CSE. Its goal is narrower:

- fuse compiled ordered outputs and staged graph outputs inside one ordered batch shell
- preserve compiled-expression cache reuse
- remove duplicate ordered prepared-frame setup inside one `evaluate_many()` call

This is the first step where batch execution reuse crosses the boundary between:

- compiled ordered expressions
- planner-owned staged graph execution

## 2. What Was Wasteful Before

Before V5, a mixed batch like:

- `delay(close, 1)`
- `rank(demean(ts_mean(close, 2)), pct=true)`

would typically do ordered work twice:

1. once for compiled ordered evaluation
2. once again for staged graph evaluation

Both paths needed the same ordered preparation concept:

- add row index
- sort by `[code, time]`
- compute ordered expressions
- restore original order

That meant extra executor churn and extra ordered shell setup even though the batch was still one logical `evaluate_many()` call.

## 3. V5 Change

V5 keeps the planner graph from V4, but changes batch execution flow:

1. compiled expressions are split into:
   - no-time-order compiled
   - ordered compiled
2. no-time-order compiled outputs still run first on the row-aligned path
3. ordered compiled outputs and staged graph outputs are executed together inside one ordered batch path

So V5 does **not** merge all routes into one graph yet. It only fuses the ordered shell where reuse is already safe and measurable.

## 4. Current Execution Shape

Inside `evaluate_many()`:

- compiled no-time-order outputs run through the existing compiled fast path
- segmented outputs still use their dedicated path
- compiled ordered outputs and staged outputs now share:
  - one executor
  - one prepared frame
  - one ordered restore step

This keeps the implementation incremental while reducing duplicated ordered work.

## 5. Why This Matters

This repository already has two strong pieces:

- compiled-expression caching in `engine.py`
- planner-owned staged graph execution in `planner.py` / `executor.py`

V5 connects them instead of replacing them.

That matters because the next path toward fuller DAG/CSE is not “rewrite everything as a graph immediately”, but:

1. keep compiled cache where it already works
2. expand safe shared execution shells
3. then grow the graph boundary further

## 6. What V5 Still Does Not Do

V5 still does not provide:

- arbitrary shared subgraph extraction
- cross-route graph nodes
- cost-based graph optimization
- full topology over every expression family

It is an ordered-batch fusion step, not a final graph planner.

## 7. Validation Target

The main regression target for V5 is:

- a mixed batch with one compiled ordered expression and one staged chain should use one prepared frame
- results must still match manual step-by-step execution

## 8. One-Sentence Summary

`execution_planner_v5` keeps the V4 staged graph intact and removes duplicate ordered-shell work by letting compiled ordered outputs and staged graph outputs share one prepared frame inside a single batch evaluation.
