# Full Native Rolling Engine Plan

## 1. Engine Boundary

The native rolling engine owns grouped, ordered rolling kernels only. It does not own parsing, public DSL semantics, planner legality, final output selection, or default rollout decisions.

## 2. Operator Priority

1. `corr` / `cov` shared moments after A/B `ACCEPT`
2. `ts_mean` / `ts_sum`
3. `ts_min` / `ts_max`
4. `ts_std`
5. `argmax` / `argmin`
6. `ts_rank`
7. `skew` / `kurt`

No operator advances without golden semantics.

## 3. Rust Module Layout

```text
native/factor_engine_native/src/
  lib.rs
  buffers.rs
  groups.rs
  nulls.rs
  positional.rs
  rolling/
    mod.rs
    mean_sum.rs
    min_max.rs
    rank.rs
    moments.rs
    std.rs
    skew_kurt.rs
```

`lib.rs` should only expose Python bindings and delegate implementation.

## 4. Python Bridge Layout

```text
src/factor_engine/
  native_bridge.py
  native_positional.py
  native_corr_cov.py
  native_rolling.py
```

Bridge files own env flags, availability checks, fallback profiles, and Polars series construction.

## 5. Planner Integration

Planner integration starts as detection, not default rewrite. It may group equivalent rolling specs after semantics and A/B evidence exist.

## 6. Fallback Strategy

Fallback to current Polars/Python paths when native is disabled, unavailable, unsupported, or fails. Fallback must preserve null masks, `NaN` masks, row order, group boundaries, and public errors.

## 7. Lifecycle Strategy

Native buffers must produce profile events for create, attach, release, fallback, and bridge failure. Logical release must be tracked separately from measured RSS.

## 8. Benchmark Gate

Every native operator needs an A/B report with total wall time, CV, peak RSS, fallback status, and correctness status. Kernel-only timings are diagnostic, not acceptance evidence.

## 9. Correctness Gate

Each operator needs golden tests covering nulls, `NaN`, insufficient samples, group boundaries, row restoration, repeated `evaluate_many`, and any operator-specific edge cases.

## 10. Rollout Strategy

Default remains Polars until docs, tests, benchmark report, and state files all record acceptance. Rollout starts behind env flags, then can move to guarded auto mode only after repeated benchmark evidence.
