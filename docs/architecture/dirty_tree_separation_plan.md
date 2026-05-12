# Dirty Tree Separation Plan

This plan separates current dirty-tree ownership after the native corr/cov gate. It is a planning document only: no commit, rollback, or deletion is authorized from this file alone.

## Commands Reviewed

```text
git status --short --untracked-files=all
git diff --name-only
git diff --stat
```

Current state: the tree is dirty with mixed ownership. Do not force commit the whole tree.

## corr_cov_native_experiment

Files:

```text
native/factor_engine_native/src/lib.rs
native/factor_engine_native/src/rolling_moments.rs
src/factor_engine/native_corr_cov.py
tests/unit/test_corr_cov_golden.py
tests/unit/test_native_corr_cov_parity.py
```

Recommendation:

- Keep and commit only as an isolated experimental/native-gate commit after human review.
- Keep native disabled by default.
- Do not merge into production route because the A/B gate rejected the prototype.
- If the experiment is retained, commit it with the benchmark report that proves rejection.

## benchmark_truth_layer

Files:

```text
benchmarks/scripts/benchmark_native_corr_cov.py
benchmarks/scripts/benchmark_mixed_segmented_ordered_sorting.py
benchmarks/scripts/benchmark_ordered_finalize_restore.py
benchmarks/scripts/benchmark_rolling_operators.py
benchmarks/scripts/performance_truth_common.py
benchmarks/reports/performance_truth_baseline.md
benchmarks/reports/performance_truth_scaleup.md
```

Recommendation:

- `benchmark_native_corr_cov.py`: keep and commit with the corr/cov experiment or benchmark-gate commit.
- Existing performance-truth scripts/reports: ask human before touching; they predate this cleanup and look like prior benchmark work.
- Do not move benchmark scripts to artifacts. Scripts belong in `benchmarks/scripts/`.

## docs_and_governance

Files:

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
```

Recommendation:

- Keep and commit as a separate governance/docs commit after confirming the corr/cov experiment is intentionally retained.
- `.gitignore` should be kept because it prevents temp/benchmark noise.
- `.ai_state/current.yaml` is append-only state work; do not squash or overwrite existing state history.
- The readiness and bridge-review docs should travel together with the A/B report so the rejection remains auditable.

Mixed docs:

```text
docs/functions.md
```

Recommendation:

- Ask human before committing. This file contains pre-existing EMA/MACD changes plus native corr/cov notes, so it has mixed ownership.
- If a clean commit is desired, split the native corr/cov doc lines from the prior EMA/MACD edits.

## pre_existing_user_changes

Files:

```text
.vscode/extensions.json
conftest.py
docs/current/README.md
docs/design.md
docs/language.md
expressions.yaml
expressions.zip
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
docs/current/macd_capability_audit.md
docs/performance_memory_self_audit.md
examples/macd_ema_dsl_example.py
tests/integration/test_ema_operator.py
```

Recommendation:

- Keep uncommitted until the owner decides whether these are one feature, several features, or scratch work.
- Do not rollback.
- Do not include in a native corr/cov cleanup commit.
- `outputs/.../*.md` are tracked reports/documentation, not raw data payloads; ask human before moving or deleting.
- `expressions.zip` is deleted in the working tree. Do not restore or remove from index without human confirmation.

## generated_artifacts

Files:

```text
benchmarks/reports/native_corr_cov_ab.md
benchmarks/artifacts/native_corr_cov_ab.json
src/factor_engine.egg-info/PKG-INFO
src/factor_engine.egg-info/SOURCES.txt
src/factor_engine.egg-info/dependency_links.txt
src/factor_engine.egg-info/top_level.txt
```

Recommendation:

- Keep `benchmarks/reports/native_corr_cov_ab.md` and `benchmarks/artifacts/native_corr_cov_ab.json` if the rejection evidence should be committed.
- Consider committing the report but treating the JSON artifact according to benchmark policy; if JSON artifacts are normally generated-only, keep uncommitted or move under an ignored archive path.
- `src/factor_engine.egg-info/*` should normally be ignored/generated packaging output. Ask human before deleting because it predates this cleanup in status, but the preferred future state is ignored/untracked.

## cache_or_temp

Observed:

```text
.pytest_cache
__pycache__/
*.pyc
.ruff_cache
.mypy_cache
native/factor_engine_native/target/
.venv/Lib/site-packages/__pycache__/
```

Recommendation:

- Delete only clear cache/temp outside `.venv`.
- Leave `.venv` internals alone except through package-management commands.
- Keep native `target/` ignored.
- No tracked cache/temp files were found by `git ls-files`.

## unknown

Files:

```text
none beyond the groups above
```

Recommendation:

- If new unclassified files appear, ask human before touching.

## Proposed Commit Split

1. User/prior feature commit: EMA/MACD/DSL/expression changes, owned by human or prior task.
2. Corr/cov semantics and native experiment commit: golden tests, native bridge, Rust prototype, native A/B script.
3. Corr/cov gate evidence commit: A/B report/artifact and readiness/bridge review docs.
4. Governance commit: `.ai_state`, `.gitignore`, lifecycle/rollout/trust docs.

Do not create these commits until ownership is confirmed.
