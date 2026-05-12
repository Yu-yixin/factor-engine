# Dirty Tree Commit Boundary Plan

## Scope

This document defines a safe commit/keep/ignore boundary for the current dirty tree before any low-copy corr/cov work or any full native rolling work begins.

Guardrails:

- do not claim a clean tree
- do not claim implementation readiness
- do not include unknown pre-existing user changes in proposed commits
- do not hide the current native corr/cov A/B `REJECT` result
- do not delete unknown user files

## Command Snapshot

Commands run for this plan:

```text
git status --short --untracked-files=all
git diff --name-only
git diff --stat
```

Observed dirty file count before adding this plan: `58`

This plan file is itself a new dirty file, so the classified file count in this document is `59`.

## Classification Legend

- `COMMIT_NOW_SAFE`: isolated planning/docs file with clear ownership and no runtime behavior change
- `COMMIT_LATER_AFTER_REVIEW`: isolated enough to commit later, but should move only after dependency/intent review
- `KEEP_UNCOMMITTED_EXPERIMENT`: keep as local experimental scope for now; do not commit until the owner explicitly wants to retain the rejected prototype
- `IGNORE_ARTIFACT`: generated artifact or packaging output that should not drive a source commit boundary
- `DELETE_CACHE_SAFE`: safe to delete cache/temp if it appears dirty
- `HUMAN_DECISION_REQUIRED`: pre-existing, mixed-ownership, or dependency-uncertain file that should not be grouped automatically

## Per-File Classification

| File | Git status | Classification | Proposed commit group | Notes |
| --- | --- | --- | --- | --- |
| `.ai_state/current.yaml` | `M` | `COMMIT_LATER_AFTER_REVIEW` | `commit 4: governance / AI state docs` | Current state file is intentional, but should travel with the freeze docs after review. |
| `.gitignore` | `M` | `COMMIT_LATER_AFTER_REVIEW` | `commit 4: governance / AI state docs` | Useful hygiene change, but review with artifact policy first. |
| `.vscode/extensions.json` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Tracked editor config with pre-existing ownership. |
| `conftest.py` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing user/prior-work change. |
| `docs/current/README.md` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing docs change outside corr/cov boundary. |
| `docs/current/profiling_schema.md` | `M` | `COMMIT_LATER_AFTER_REVIEW` | `commit 4: governance / AI state docs` | Schema doc ties to native corr/cov observability and should be reviewed with docs/state. |
| `docs/design.md` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing user/prior-work docs change. |
| `docs/functions.md` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Mixed ownership per prior reports; must be split by owner first. |
| `docs/language.md` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing user/prior-work docs change. |
| `expressions.yaml` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing DSL/workload content. |
| `expressions.zip` | `D` | `HUMAN_DECISION_REQUIRED` | excluded | Deleted tracked file; do not restore or remove without owner decision. |
| `native/factor_engine_native/src/lib.rs` | `M` | `KEEP_UNCOMMITTED_EXPERIMENT` | `commit 3: native corr/cov rejected prototype and docs` | Experimental native binding only; do not promote while A/B is `REJECT`. |
| `outputs/alpha101_data_parquet_20260417_113656/README.md` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Tracked output/report doc owned outside this boundary. |
| `outputs/alpha101_selected10_data_parquet_20260417_114240/README.md` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Tracked output/report doc owned outside this boundary. |
| `outputs/alpha101_selected10_data_parquet_20260417_114240/selection_report.md` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Tracked output/report doc owned outside this boundary. |
| `scratch_test/hello.txt` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Scratch file; owner intent unknown. |
| `src/factor_engine/ast_nodes.py` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing code change outside isolated corr/cov plan scope. |
| `src/factor_engine/errors.py` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing code change outside isolated corr/cov plan scope. |
| `src/factor_engine/executor.py` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing core engine change; must not be bundled automatically. |
| `src/factor_engine/lexer.py` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing parser/DSL change. |
| `src/factor_engine/parser.py` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing parser/DSL change. |
| `src/factor_engine/registry.py` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing core engine change; may affect test dependencies. |
| `src/factor_engine/tokens.py` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing parser/DSL change. |
| `src/factor_engine/validator.py` | `M` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing validation change. |
| `.ai_state/snapshots/340553f.yaml` | `??` | `COMMIT_LATER_AFTER_REVIEW` | `commit 4: governance / AI state docs` | Snapshot is useful evidence, but should travel with state/docs review. |
| `benchmarks/artifacts/native_corr_cov_ab.json` | `??` | `IGNORE_ARTIFACT` | excluded | Generated A/B artifact; keep locally, but do not let it define the source boundary. |
| `benchmarks/reports/native_corr_cov_ab.md` | `??` | `COMMIT_LATER_AFTER_REVIEW` | `commit 1: benchmark truth layer` | Preserve the `REJECT` result in source-visible form. |
| `benchmarks/reports/performance_truth_baseline.md` | `??` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing benchmark report. |
| `benchmarks/reports/performance_truth_scaleup.md` | `??` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing benchmark report. |
| `benchmarks/scripts/benchmark_mixed_segmented_ordered_sorting.py` | `??` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing benchmark script. |
| `benchmarks/scripts/benchmark_native_corr_cov.py` | `??` | `COMMIT_LATER_AFTER_REVIEW` | `commit 1: benchmark truth layer` | Keep with the A/B report if the rejected experiment is intentionally retained. |
| `benchmarks/scripts/benchmark_ordered_finalize_restore.py` | `??` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing benchmark script. |
| `benchmarks/scripts/benchmark_rolling_operators.py` | `??` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing benchmark script. |
| `benchmarks/scripts/performance_truth_common.py` | `??` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing benchmark support code. |
| `docs/architecture/dirty_tree_separation_plan.md` | `??` | `COMMIT_LATER_AFTER_REVIEW` | `commit 4: governance / AI state docs` | Boundary/governance doc; safe enough for a later docs commit. |
| `docs/architecture/full_native_readiness_after_corr_cov_gate.md` | `??` | `COMMIT_LATER_AFTER_REVIEW` | `commit 3: native corr/cov rejected prototype and docs` | Readiness doc must retain the current `REJECT` decision. |
| `docs/architecture/full_native_rolling_engine_plan.md` | `??` | `COMMIT_LATER_AFTER_REVIEW` | `commit 3: native corr/cov rejected prototype and docs` | Planning doc only; should not be confused with implementation approval. |
| `docs/architecture/low_copy_corr_cov_experiment_plan.md` | `??` | `COMMIT_NOW_SAFE` | `commit 4: governance / AI state docs` | Pure planning doc created in the freeze window; no runtime behavior change. |
| `docs/architecture/native_corr_cov_bridge_review.md` | `??` | `COMMIT_LATER_AFTER_REVIEW` | `commit 3: native corr/cov rejected prototype and docs` | Must travel with the rejection evidence. |
| `docs/architecture/native_corr_cov_dirty_tree_report.md` | `??` | `COMMIT_LATER_AFTER_REVIEW` | `commit 3: native corr/cov rejected prototype and docs` | Ownership evidence doc. |
| `docs/architecture/native_corr_cov_rollout.md` | `??` | `COMMIT_LATER_AFTER_REVIEW` | `commit 3: native corr/cov rejected prototype and docs` | Rollout guardrail doc; keep the default-off rule explicit. |
| `docs/architecture/native_corr_cov_shared_moments_design.md` | `??` | `COMMIT_LATER_AFTER_REVIEW` | `commit 3: native corr/cov rejected prototype and docs` | Experimental design material; review before retaining. |
| `docs/architecture/native_resource_lifecycle.md` | `??` | `COMMIT_LATER_AFTER_REVIEW` | `commit 3: native corr/cov rejected prototype and docs` | Design/governance doc tied to the rejected prototype family. |
| `docs/architecture/native_workflow_trust.md` | `??` | `COMMIT_LATER_AFTER_REVIEW` | `commit 3: native corr/cov rejected prototype and docs` | Workflow/governance note tied to the native gate. |
| `docs/architecture/pre_full_native_freeze_report.md` | `??` | `COMMIT_NOW_SAFE` | `commit 4: governance / AI state docs` | Pure freeze report created for planning only. |
| `docs/architecture/rolling_operator_semantics_matrix.md` | `??` | `COMMIT_LATER_AFTER_REVIEW` | `commit 3: native corr/cov rejected prototype and docs` | Reference doc should be reviewed with the rest of the native planning set. |
| `docs/current/macd_capability_audit.md` | `??` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing user/prior-work docs. |
| `docs/performance_memory_self_audit.md` | `??` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing user/prior-work docs. |
| `examples/macd_ema_dsl_example.py` | `??` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing example code. |
| `native/factor_engine_native/src/rolling_moments.rs` | `??` | `KEEP_UNCOMMITTED_EXPERIMENT` | `commit 3: native corr/cov rejected prototype and docs` | Core rejected native prototype implementation. |
| `src/factor_engine.egg-info/PKG-INFO` | `??` | `IGNORE_ARTIFACT` | excluded | Generated packaging metadata. |
| `src/factor_engine.egg-info/SOURCES.txt` | `??` | `IGNORE_ARTIFACT` | excluded | Generated packaging metadata. |
| `src/factor_engine.egg-info/dependency_links.txt` | `??` | `IGNORE_ARTIFACT` | excluded | Generated packaging metadata. |
| `src/factor_engine.egg-info/top_level.txt` | `??` | `IGNORE_ARTIFACT` | excluded | Generated packaging metadata. |
| `src/factor_engine/native_corr_cov.py` | `??` | `KEEP_UNCOMMITTED_EXPERIMENT` | `commit 3: native corr/cov rejected prototype and docs` | Experimental opt-in bridge only; keep default-off and unpromoted. |
| `tests/integration/test_ema_operator.py` | `??` | `HUMAN_DECISION_REQUIRED` | excluded | Pre-existing unrelated feature test. |
| `tests/unit/test_corr_cov_golden.py` | `??` | `COMMIT_LATER_AFTER_REVIEW` | `commit 2: corr/cov golden semantics freeze` | Useful semantics lock, but confirm it does not depend on excluded dirty engine changes. |
| `tests/unit/test_native_corr_cov_parity.py` | `??` | `KEEP_UNCOMMITTED_EXPERIMENT` | `commit 3: native corr/cov rejected prototype and docs` | Parity test belongs to the rejected opt-in experiment. |
| `docs/architecture/dirty_tree_commit_boundary_plan.md` | `??` | `COMMIT_NOW_SAFE` | `commit 4: governance / AI state docs` | This task's planning output; isolated and non-behavioral. |

## Classification Summary

- `COMMIT_NOW_SAFE`: 3
- `COMMIT_LATER_AFTER_REVIEW`: 17
- `KEEP_UNCOMMITTED_EXPERIMENT`: 4
- `IGNORE_ARTIFACT`: 5
- `DELETE_CACHE_SAFE`: 0
- `HUMAN_DECISION_REQUIRED`: 30

Total classified dirty files: `59`

## Proposed Commit Groups

These are proposed commit boundaries only. Do not commit them until the owner explicitly approves.

### commit 1: benchmark truth layer

Included:

```text
benchmarks/scripts/benchmark_native_corr_cov.py
benchmarks/reports/native_corr_cov_ab.md
```

Excluded:

```text
benchmarks/artifacts/native_corr_cov_ab.json
benchmarks/reports/performance_truth_baseline.md
benchmarks/reports/performance_truth_scaleup.md
benchmarks/scripts/benchmark_mixed_segmented_ordered_sorting.py
benchmarks/scripts/benchmark_ordered_finalize_restore.py
benchmarks/scripts/benchmark_rolling_operators.py
benchmarks/scripts/performance_truth_common.py
```

Validation command required:

```text
./.venv/Scripts/python.exe benchmarks/scripts/benchmark_native_corr_cov.py --repeats 3
```

Risk level: `medium`

Rollback notes:

- revert the benchmark script and markdown report together
- keep the `REJECT` decision visible if any later native work is retained

### commit 2: corr/cov golden semantics freeze

Included:

```text
tests/unit/test_corr_cov_golden.py
```

Excluded:

```text
src/factor_engine/executor.py
src/factor_engine/registry.py
tests/unit/test_native_corr_cov_parity.py
all pre-existing parser/EMA/MACD/DSL changes
```

Validation command required:

```text
./.venv/Scripts/python.exe -m pytest tests/unit/test_corr.py tests/unit/test_cov.py tests/unit/test_corr_cov_golden.py -q
```

Risk level: `high`

Rollback notes:

- if the test depends on excluded dirty engine changes, do not commit it yet
- revert the golden test alone if it cannot stand on an isolated base

### commit 3: native corr/cov rejected prototype and docs

Included:

```text
native/factor_engine_native/src/lib.rs
native/factor_engine_native/src/rolling_moments.rs
src/factor_engine/native_corr_cov.py
tests/unit/test_native_corr_cov_parity.py
docs/architecture/full_native_readiness_after_corr_cov_gate.md
docs/architecture/full_native_rolling_engine_plan.md
docs/architecture/native_corr_cov_bridge_review.md
docs/architecture/native_corr_cov_dirty_tree_report.md
docs/architecture/native_corr_cov_rollout.md
docs/architecture/native_corr_cov_shared_moments_design.md
docs/architecture/native_resource_lifecycle.md
docs/architecture/native_workflow_trust.md
docs/architecture/rolling_operator_semantics_matrix.md
```

Excluded:

```text
benchmarks/artifacts/native_corr_cov_ab.json
docs/functions.md
all pre-existing user/prior-work code changes
any low-copy implementation work
```

Validation command required:

```text
./.venv/Scripts/python.exe - <<'PY'
import os
import pytest
os.environ["FACTOR_ENGINE_NATIVE_CORR_COV"] = "1"
raise SystemExit(pytest.main([
    "tests/unit/test_native_corr_cov_parity.py",
]))
PY
```

Risk level: `medium-high`

Rollback notes:

- revert the experiment as one unit if the owner does not want to retain a rejected prototype
- do not keep the prototype without its `REJECT` documentation

### commit 4: governance / AI state docs

Included:

```text
.ai_state/current.yaml
.ai_state/snapshots/340553f.yaml
.gitignore
docs/current/profiling_schema.md
docs/architecture/dirty_tree_separation_plan.md
docs/architecture/pre_full_native_freeze_report.md
docs/architecture/low_copy_corr_cov_experiment_plan.md
docs/architecture/dirty_tree_commit_boundary_plan.md
```

Excluded:

```text
docs/functions.md
benchmarks/artifacts/native_corr_cov_ab.json
all pre-existing user/prior-work docs and code changes
```

Validation command required:

```text
manual review of .ai_state/current.yaml structure
grep -nE '(__pycache__/|\\.pytest_cache/|\\.ruff_cache/|\\.mypy_cache/|tmp/|\\.tmp/|benchmarks/artifacts/tmp/|native/\\*\\*/target/|\\.venv/|\\.env|outputs/\\*)' .gitignore
```

Risk level: `medium`

Rollback notes:

- revert the docs/state commit separately from the prototype commit
- if `.ai_state/current.yaml` becomes stale relative to the retained docs, revert or restate it in a follow-up docs-only change

## .gitignore Coverage Check

Coverage result for requested areas:

| Area | Status | Notes |
| --- | --- | --- |
| cache | covered | `__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/` present |
| tmp | covered | `tmp/`, `.tmp/`, `*.tmp` present |
| `benchmarks/artifacts/tmp` | covered | explicit ignore present |
| native `target` | covered | `native/**/target/` present |
| local env | covered | `.venv/`, `venv/`, `env/`, `.env*` present |
| data | covered | `data/` is ignored after the safe hygiene patch |
| outputs | covered | `outputs/*` present, with `outputs/README.md` kept tracked |

Notes:

- tracked files under `outputs/` still appear dirty because ignore rules do not untrack existing files
- `data/` is now covered by the safe hygiene patch

## YAML Validation

Available parser check:

- Python `yaml` module in `.venv`: not available
- PowerShell `ConvertFrom-Yaml`: not available

YAML_PARSE_STATUS: `MANUAL_ONLY`

Manual validation performed:

- top-level keys are present and consistently indented
- list indentation under `focus`, `facts`, `assumptions`, `risks`, `open_questions`, `next_actions`, and `pre_full_native_rolling` remains structurally consistent by inspection
- quote usage and scalar formatting appear consistent with the existing file style

## Current Boundary Decision

- current native corr/cov A/B decision: `REJECT`
- implementation allowed now: `no`
- readiness for low-copy or full native implementation: blocked until ownership is cleaned up
