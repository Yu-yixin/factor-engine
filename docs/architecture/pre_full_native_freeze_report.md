# Pre-Full-Native Freeze Report

## Scope

This document freezes the current corr/cov native-preparation state before any full native rolling implementation begins.

Rules for this freeze:

- no full native rolling implementation
- no default native enablement
- no rollback of unknown user changes
- no commit from the current mixed-ownership tree
- documentation and instrumentation planning only

## Completed

- Corr/cov semantics are frozen at the engine level through golden and parity coverage.
- The native extension import/build path was validated for the current prototype.
- Native corr/cov parity ran successfully behind `FACTOR_ENGINE_NATIVE_CORR_COV=1`.
- The first corr/cov A/B gate was executed and recorded as evidence.
- The repository already has one accepted native low-copy precedent in the positional path, which is the design reference for the next corr/cov experiment.
- Dirty-tree ownership, guarded rollout, bridge review, readiness, and native-resource notes exist in `docs/architecture/`.

Evidence:

- `tests/unit/test_corr.py`
- `tests/unit/test_cov.py`
- `tests/unit/test_corr_cov_golden.py`
- `tests/unit/test_native_corr_cov_parity.py`
- `benchmarks/scripts/benchmark_native_corr_cov.py`
- `benchmarks/reports/native_corr_cov_ab.md`
- `docs/architecture/native_corr_cov_bridge_review.md`
- `docs/architecture/full_native_readiness_after_corr_cov_gate.md`

## Rejected

The current corr/cov native prototype is rejected as a rollout candidate.

Rejected items:

- the current Python-object corr/cov bridge as a performance acceptance candidate
- any claim that native corr/cov is faster than Polars
- any default enablement of `FACTOR_ENGINE_NATIVE_CORR_COV`
- any start of the full native rolling engine from the current tree

Reason:

- the reduced A/B matrix recorded `REJECT`
- native total wall time was slower than Polars
- the benchmark does not yet isolate bridge, scan, output-build, and RSS costs well enough to justify expansion

The rejected prototype remains experimental only.

## Blocked

- The worktree is still dirty with mixed ownership.
- `docs/functions.md` has mixed ownership and should not be treated as clean native-only scope.
- The current benchmark artifact does not yet record the timing split needed to prove whether low-copy fixes the current loss.
- The current prototype still uses `to_list()` input conversion and Python-value output construction.
- The reduced matrix was enough to reject the current prototype, but it is not enough to justify the next bridge design without better instrumentation.
- Full native rolling should not start while corr/cov is still bridge-uncertain and the tree is not cleanly separated.

## Safe To Keep

- Corr/cov golden semantics and parity tests.
- The current Rust rolling-moments prototype as an experimental reference only.
- The opt-in env-gated Python bridge in `src/factor_engine/native_corr_cov.py` as benchmark/parity scaffolding only.
- The native corr/cov A/B script and its rejection evidence.
- Existing architecture/governance docs that explain rollout limits, bridge risks, lifecycle boundaries, and dirty-tree ownership.
- `.ai_state/snapshots/340553f.yaml`.

## Must Not Be Enabled

- `FACTOR_ENGINE_NATIVE_CORR_COV` must not become default-on.
- The rejected Python-object corr/cov bridge must not be wired into the normal executor route.
- The current prototype must not be described as production-ready.
- No full native rolling engine plan may be treated as implementation authorization.
- No corr/cov speedup claim may be made from kernel-only timing.
- No commit should bundle unrelated user/prior-work changes with the corr/cov experiment.

## Dirty File Ownership Groups

### Group A: pre-existing user or prior-work changes

Treat these as user-owned or previously in-flight work. Do not rollback or absorb into native corr/cov cleanup.

```text
.vscode/extensions.json
conftest.py
docs/current/README.md
docs/design.md
docs/language.md
expressions.yaml
expressions.zip (deleted in working tree)
outputs/alpha101_data_parquet_20260417_113656/README.md
outputs/alpha101_selected10_data_parquet_20260417_114240/README.md
outputs/alpha101_selected10_data_parquet_20260417_114240/selection_report.md
scratch_test/hello.txt
src/factor_engine/ast_nodes.py
src/factor_engine/errors.py
src/factor_engine/executor.py
src/factor_engine/lexer.py
src/factor_engine/parser.py
src/factor_engine/registry.py
src/factor_engine/tokens.py
src/factor_engine/validator.py
benchmarks/reports/performance_truth_baseline.md
benchmarks/reports/performance_truth_scaleup.md
benchmarks/scripts/benchmark_mixed_segmented_ordered_sorting.py
benchmarks/scripts/benchmark_ordered_finalize_restore.py
benchmarks/scripts/benchmark_rolling_operators.py
benchmarks/scripts/performance_truth_common.py
docs/current/macd_capability_audit.md
docs/performance_memory_self_audit.md
examples/macd_ema_dsl_example.py
tests/integration/test_ema_operator.py
```

### Group B: mixed ownership

This file contains pre-existing work plus native corr/cov additions and should stay isolated until split by the owner.

```text
docs/functions.md
```

### Group C: corr/cov experimental code and tests

These files are the experimental native corr/cov ownership group. They are safe to keep as experimental-only scope, but not safe to promote.

```text
native/factor_engine_native/src/lib.rs
native/factor_engine_native/src/rolling_moments.rs
src/factor_engine/native_corr_cov.py
tests/unit/test_corr_cov_golden.py
tests/unit/test_native_corr_cov_parity.py
```

### Group D: docs, governance, and freeze-state files

These files document the gate, rollout, readiness, and current freeze state.

```text
.ai_state/current.yaml
.ai_state/snapshots/340553f.yaml
.gitignore
docs/current/profiling_schema.md
docs/architecture/dirty_tree_separation_plan.md
docs/architecture/full_native_readiness_after_corr_cov_gate.md
docs/architecture/full_native_rolling_engine_plan.md
docs/architecture/native_corr_cov_bridge_review.md
docs/architecture/native_corr_cov_dirty_tree_report.md
docs/architecture/native_corr_cov_rollout.md
docs/architecture/native_corr_cov_shared_moments_design.md
docs/architecture/native_resource_lifecycle.md
docs/architecture/native_workflow_trust.md
docs/architecture/rolling_operator_semantics_matrix.md
docs/architecture/pre_full_native_freeze_report.md
docs/architecture/low_copy_corr_cov_experiment_plan.md
```

### Group E: benchmark gate evidence and generated outputs

Keep these as evidence or generated artifacts, depending on the repository's benchmark-artifact policy.

```text
benchmarks/scripts/benchmark_native_corr_cov.py
benchmarks/reports/native_corr_cov_ab.md
benchmarks/artifacts/native_corr_cov_ab.json
src/factor_engine.egg-info/*
```

## Readiness Statement

NEEDS_DIRTY_TREE_CLEANUP_FIRST
