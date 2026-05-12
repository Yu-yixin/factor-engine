# MACD Capability Audit

This report records the MACD/EMA capability audit for the current Factor Engine
codebase. It intentionally does not add an `ema` primitive, an `ema` alias, or a
`macd()` primitive.

## Branch Status Note

Stable baseline answer:

- stable `master` still does not accept EMA/MACD as a formal DSL contract

Current experiment-branch exception:

- `feature/ema-macd-experiment` carries an isolated `ema(x, span)` operator path
  for evaluation and testing only
- the experiment is not merged to stable `master`
- the experiment must not be described as production-ready trading capability

## Existing EMA-like capability found in stable baseline?

- no

## Candidate existing operators

- `ts_mean(x, n)`: rolling arithmetic mean. Not equivalent to EMA because it
  uses a finite rolling window instead of recursive state.
- `ts_sum`, `ts_min`, `ts_max`, `ts_median`, `ts_std`, `ts_rank`, `corr`, `cov`,
  `argmax`, `argmin`, `skew`, `kurt`: ordered or rolling roots, but none define
  exponential weighting or recursive smoothing.
- `ewm_mean`, `ewm_std`, and `ewm_var` appear only in
  `docs/strategy/future_operator_roadmap.md` as future weighted/stateful rolling
  candidates.

## Can `ema` be added as alias only in stable baseline?

- no

There is no landed exponential moving average or equivalent EWM operator to
alias. Adding `ema(x, n) -> ts_mean(x, n)` would be incorrect.

## Evidence

Files inspected:

- `src/factor_engine/registry.py`
- `src/factor_engine/parser.py`
- `src/factor_engine/validator.py`
- `src/factor_engine/planner.py`
- `src/factor_engine/executor.py`
- `src/factor_engine/execution_ordered.py`
- `src/factor_engine/execution_positional.py`
- `src/factor_engine/runtime/`
- `tests/unit/`
- `tests/integration/`
- `docs/functions.md`
- `docs/ordered_roots_matrix.md`
- `docs/strategy/future_operator_roadmap.md`
- `examples/`
- `benchmarks/`

Relevant functions/classes:

- `FUNCTION_REGISTRY` and `FUNCTION_ALIASES` in `registry.py`
- `canonical_function_name()` and `get_function_spec()` in `registry.py`
- `Parser._parse_call()` in `parser.py`
- `Validator._infer_value_type()` in `validator.py`
- `ExecutionPlanner` route inspection/build logic in `planner.py`
- `Executor._compile_ts_mean()` in `executor.py`
- `Executor._build_materialized_single_input_ordered_expr()` in `executor.py`

## Composite Feasibility

### Can EMA be built from existing primitives?

- no

### Required base operators

EMA requires an ordered recursive operator such as one of:

- `scan`
- `fold`
- `recursive_apply`
- `accumulate`
- a stateful ordered kernel
- a custom ordered recursive execution class

No such user-facing primitive or planner-visible recursive execution class is
currently available.

### Reasoning

EMA is recursive:

```text
ema_t = alpha * x_t + (1 - alpha) * ema_{t-1}
```

Normal rolling operators are insufficient because they aggregate a finite
window independently for each row. EMA depends on the previous computed EMA
state, so it cannot be represented as `ts_mean(close, n)` or as a simple
composition of current rolling/window primitives.

### Risk

- EMA requires ordered recursive state.
- Rolling mean is not equivalent to EMA.
- A hidden executor special case would weaken planner and lifecycle semantics.

## Report-Only Primitive Proposal

Recommended future primitive:

```text
ema(x, span)
```

Do not add:

```text
macd()
```

Recommended future execution class:

```text
ordered_recursive
```

Reason:

- depends on symbol partition
- depends on time order
- depends on previous computed state
- cannot be evaluated row-independently
- cannot be represented as a normal rolling window

Expected future contract:

```text
requires_partition_by = ["code"]
requires_order_by = ["time"]
produces_mode = "row_aligned"
accepts_materialized_input = true
```

Implementation suggestion for a later confirmed phase:

1. Start with a Python/Polars-safe implementation.
2. Validate against `pandas.Series.ewm(span=n, adjust=False).mean()` in tests.
3. Add a native Rust kernel only after correctness is frozen.

## MACD Status

MACD cannot currently be represented safely through Factor Engine DSL
composition because the required `ema` capability is not available.

The desired future DSL expressions are:

```text
dif = ema(close, 12) - ema(close, 26)
dea = ema(ema(close, 12) - ema(close, 26), 9)
hist = (ema(close, 12) - ema(close, 26)) - ema(ema(close, 12) - ema(close, 26), 9)
```

Until `ema(x, span)` is explicitly accepted as an ordered recursive operator in
stable `master`, these should remain unsupported in the stable baseline. The
current experiment branch therefore remains evaluation-only rather than a
stable capability rollout.
