# Current Invariants

These are repository-level invariants that must not be broken by cleanup, refactoring, benchmark work, or AI-assisted edits.

- `evaluate()` and `evaluate_many()` public behavior must not change without explicit design, tests, and review.
- Ordered paths must preserve sort and restore semantics. Outputs must align back to the caller's original row order.
- Grouped cross-sectional functions must preserve their grouping semantics, including the distinction between normal cross-sectional and grouped cross-sectional behavior.
- Segmented execution must not be casually merged into the ordinary ordered path. Segment specification, segment-count reuse, and length-spec behavior need explicit tests.
- Materialization boundaries must not be pierced casually. Planner/executor decisions about when to materialize are part of correctness and performance behavior.
- Lifecycle drop behavior must never affect final outputs. A drop is valid only when the result remains equivalent and required state is not removed early.
- Native execution must remain optional. The Python path and fallback behavior must continue to work when the native extension is missing, disabled, or fails.
- Benchmark and profiling logic must not become core semantic logic. Profiling may observe execution; it must not define correctness.
- All refactoring must start from a known test baseline. If a path lacks coverage, add or identify tests before moving code.
- Large cleanup must not delete historical evidence or benchmark context without an explicit archive/migration plan.

