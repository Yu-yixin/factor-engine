# Cleanup Plan

The cleanup plan is intentionally staged. Phase 1 establishes rules only.

## Phase 1: Establish Rules

- Harden `.gitignore`.
- Create `docs/current/` as the current truth source.
- Define repository rules.
- Define artifact policy.
- Define benchmark and profiling policy.
- Define test layering policy.
- Record later cleanup work without deleting, moving, or refactoring existing history.

## Phase 2: Establish Layers

- Split tests into clearer layers and apply markers such as `unit`, `integration`, `workflow`, `native`, `slow`, `perf`, and `profiling`.
- Split examples, benchmark scripts, and operational scripts into clearer locations.
- Split documentation into current, history, and archive layers.
- Split data, outputs, and artifacts so generated files and local data are outside Git.
- Decide which existing benchmark summaries remain in Git and which detailed run artifacts move to external storage or archive.
- Remove tracked artifact files only through an explicit, reviewed plan.

## Phase 3: Refactor

- Split `executor.py` only after the test baseline is stable.
- Narrow planner, lifecycle, and profiling boundaries where tests prove behavior is protected.
- Clarify native bridge boundaries and fallback contracts.
- Keep public `evaluate()` and `evaluate_many()` behavior stable unless an explicit design changes it.
- Treat performance-sensitive refactoring as benchmark-driven work, not cosmetic cleanup.

