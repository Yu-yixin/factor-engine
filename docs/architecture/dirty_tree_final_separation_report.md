# Dirty Tree Final Separation Report

## Preflight

- Starting dirty file count: `56`
- Starting HEAD: `61e7c4df3f87df768c7772fc85c99f95b7917094`
- Starting branch: `master`
- Starting staged files count: `0`
- Starting untracked files count: `32`
- Final committed HEAD before this report write: `d8471f8cb0817e9d62a8e90e2274ff65669bdc4f`
- Final dirty file count before this report write: `37`
- Final staged files count before this report write: `0`
- Final untracked files count before this report write: `17`
- YAML_PARSE_STATUS: `MANUAL_ONLY`

## Classification Summary

- `BENCHMARK_TRUTH_LAYER`: `0`
- `CORR_COV_GOLDEN_FREEZE`: `2`
- `NATIVE_CORR_COV_REJECTED_EXPERIMENT`: `11`
- `GOVERNANCE_DOCS_ALREADY_COMMITTED_OR_LEFTOVER`: `6`
- `GENERATED_BENCHMARK_ARTIFACT`: `1`
- `CACHE_OR_TEMP`: `4`
- `PRE_EXISTING_USER_CHANGE`: `29`
- `HUMAN_DECISION_REQUIRED`: `3`
- `UNKNOWN_OWNERSHIP`: `0`

No `BENCHMARK_TRUTH_LAYER` file was safe to stage. The benchmark-truth candidates in the dirty tree all matched pre-existing user/prior-work ownership, so commit group 1 was skipped.

## Classification Table

| File | Git Status | Bucket | Proposed Action | Reason | Safe To Stage |
| --- | --- | --- | --- | --- | --- |
| `.ai_state/current.yaml` | `M` | `GOVERNANCE_DOCS_ALREADY_COMMITTED_OR_LEFTOVER` | `commit group 4` | Current repo state freeze update. | `yes` |
| `.gitignore` | `M` | `GOVERNANCE_DOCS_ALREADY_COMMITTED_OR_LEFTOVER` | `commit group 4` | Governance hygiene for temp artifacts. | `yes` |
| `.vscode/extensions.json` | `M` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing editor config change. | `no` |
| `conftest.py` | `M` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing test harness change. | `no` |
| `docs/current/README.md` | `M` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing docs work outside corr/cov scope. | `no` |
| `docs/current/profiling_schema.md` | `M` | `GOVERNANCE_DOCS_ALREADY_COMMITTED_OR_LEFTOVER` | `commit group 4` | Reserves native corr/cov profile fields. | `yes` |
| `docs/design.md` | `M` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing design doc edits. | `no` |
| `docs/functions.md` | `M` | `HUMAN_DECISION_REQUIRED` | `leave dirty` | Mixed EMA/MACD work plus corr/cov notes. | `no` |
| `docs/language.md` | `M` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing language doc edits. | `no` |
| `expressions.yaml` | `M` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing DSL workload change. | `no` |
| `expressions.zip` | `D` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing tracked deletion needs owner call. | `no` |
| `native/factor_engine_native/src/lib.rs` | `M` | `NATIVE_CORR_COV_REJECTED_EXPERIMENT` | `commit group 3` | Adds opt-in corr/cov binding only. | `yes` |
| `outputs/alpha101_data_parquet_20260417_113656/README.md` | `M` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Tracked output doc owned outside this cleanup. | `no` |
| `outputs/alpha101_selected10_data_parquet_20260417_114240/README.md` | `M` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Tracked output doc owned outside this cleanup. | `no` |
| `outputs/alpha101_selected10_data_parquet_20260417_114240/selection_report.md` | `M` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Tracked output report owned outside this cleanup. | `no` |
| `scratch_test/hello.txt` | `M` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Scratch file with unknown owner intent. | `no` |
| `src/factor_engine/ast_nodes.py` | `M` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing parser/runtime feature work. | `no` |
| `src/factor_engine/errors.py` | `M` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing core error-path change. | `no` |
| `src/factor_engine/executor.py` | `M` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing executor change outside isolated native gate. | `no` |
| `src/factor_engine/lexer.py` | `M` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing parser/DSL change. | `no` |
| `src/factor_engine/parser.py` | `M` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing parser/DSL change. | `no` |
| `src/factor_engine/registry.py` | `M` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing registry change outside isolated native gate. | `no` |
| `src/factor_engine/tokens.py` | `M` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing parser/DSL change. | `no` |
| `src/factor_engine/validator.py` | `M` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing validation change. | `no` |
| `.ai_state/snapshots/340553f.yaml` | `??` | `GOVERNANCE_DOCS_ALREADY_COMMITTED_OR_LEFTOVER` | `commit group 4` | Snapshot evidence for pre-full-native freeze. | `yes` |
| `benchmarks/artifacts/native_corr_cov_ab.json` | `??` | `GENERATED_BENCHMARK_ARTIFACT` | `leave dirty` | Generated artifact referenced by docs, but boundary plan did not mark it source-safe. | `no` |
| `benchmarks/reports/native_corr_cov_ab.md` | `??` | `NATIVE_CORR_COV_REJECTED_EXPERIMENT` | `commit group 3` | Canonical source-visible `REJECT` report. | `yes` |
| `benchmarks/reports/performance_truth_baseline.md` | `??` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing benchmark truth report. | `no` |
| `benchmarks/reports/performance_truth_scaleup.md` | `??` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing benchmark truth report. | `no` |
| `benchmarks/scripts/benchmark_mixed_segmented_ordered_sorting.py` | `??` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing benchmark script. | `no` |
| `benchmarks/scripts/benchmark_native_corr_cov.py` | `??` | `NATIVE_CORR_COV_REJECTED_EXPERIMENT` | `commit group 3` | Native gate benchmark script for rejected prototype. | `yes` |
| `benchmarks/scripts/benchmark_ordered_finalize_restore.py` | `??` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing benchmark script. | `no` |
| `benchmarks/scripts/benchmark_rolling_operators.py` | `??` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing benchmark script. | `no` |
| `benchmarks/scripts/performance_truth_common.py` | `??` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing benchmark support code. | `no` |
| `docs/architecture/dirty_tree_separation_plan.md` | `??` | `GOVERNANCE_DOCS_ALREADY_COMMITTED_OR_LEFTOVER` | `commit group 4` | Dirty-tree governance plan. | `yes` |
| `docs/architecture/full_native_readiness_after_corr_cov_gate.md` | `??` | `NATIVE_CORR_COV_REJECTED_EXPERIMENT` | `commit group 3` | Records native import, parity, and `REJECT`. | `yes` |
| `docs/architecture/full_native_rolling_engine_plan.md` | `??` | `HUMAN_DECISION_REQUIRED` | `leave dirty` | Future full-native design doc outside current separation boundary. | `no` |
| `docs/architecture/native_corr_cov_bridge_review.md` | `??` | `NATIVE_CORR_COV_REJECTED_EXPERIMENT` | `commit group 3` | Documents why current bridge lost to Polars. | `yes` |
| `docs/architecture/native_corr_cov_dirty_tree_report.md` | `??` | `NATIVE_CORR_COV_REJECTED_EXPERIMENT` | `commit group 3` | Audit trail for native corr/cov ownership split. | `yes` |
| `docs/architecture/native_corr_cov_rollout.md` | `??` | `NATIVE_CORR_COV_REJECTED_EXPERIMENT` | `commit group 3` | Keeps default-off and gate rules explicit. | `yes` |
| `docs/architecture/native_corr_cov_shared_moments_design.md` | `??` | `CORR_COV_GOLDEN_FREEZE` | `commit group 2` | Semantics/design freeze doc paired with golden test. | `yes` |
| `docs/architecture/native_resource_lifecycle.md` | `??` | `NATIVE_CORR_COV_REJECTED_EXPERIMENT` | `commit group 3` | Native lifecycle guardrails for prototype evidence. | `yes` |
| `docs/architecture/native_workflow_trust.md` | `??` | `GOVERNANCE_DOCS_ALREADY_COMMITTED_OR_LEFTOVER` | `commit group 4` | Governance rules for native workflow. | `yes` |
| `docs/architecture/rolling_operator_semantics_matrix.md` | `??` | `HUMAN_DECISION_REQUIRED` | `leave dirty` | Broader multi-operator readiness matrix exceeds isolated corr/cov freeze. | `no` |
| `docs/current/macd_capability_audit.md` | `??` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing MACD docs work. | `no` |
| `docs/performance_memory_self_audit.md` | `??` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing performance audit work. | `no` |
| `examples/macd_ema_dsl_example.py` | `??` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing example work. | `no` |
| `native/factor_engine_native/src/rolling_moments.rs` | `??` | `NATIVE_CORR_COV_REJECTED_EXPERIMENT` | `commit group 3` | Experimental Rust shared-moment kernel. | `yes` |
| `src/factor_engine.egg-info/PKG-INFO` | `??` | `CACHE_OR_TEMP` | `leave dirty` | Generated packaging metadata, not source. | `no` |
| `src/factor_engine.egg-info/SOURCES.txt` | `??` | `CACHE_OR_TEMP` | `leave dirty` | Generated packaging metadata, not source. | `no` |
| `src/factor_engine.egg-info/dependency_links.txt` | `??` | `CACHE_OR_TEMP` | `leave dirty` | Generated packaging metadata, not source. | `no` |
| `src/factor_engine.egg-info/top_level.txt` | `??` | `CACHE_OR_TEMP` | `leave dirty` | Generated packaging metadata, not source. | `no` |
| `src/factor_engine/native_corr_cov.py` | `??` | `NATIVE_CORR_COV_REJECTED_EXPERIMENT` | `commit group 3` | Opt-in Python bridge only; default path unchanged. | `yes` |
| `tests/integration/test_ema_operator.py` | `??` | `PRE_EXISTING_USER_CHANGE` | `leave dirty` | Pre-existing unrelated integration test. | `no` |
| `tests/unit/test_corr_cov_golden.py` | `??` | `CORR_COV_GOLDEN_FREEZE` | `commit group 2` | Freezes current corr/cov semantics. | `yes` |
| `tests/unit/test_native_corr_cov_parity.py` | `??` | `NATIVE_CORR_COV_REJECTED_EXPERIMENT` | `commit group 3` | Opt-in parity coverage for native prototype. | `yes` |

## Commits Created

| Group | Commit Hash | Message | Files Count | Validation |
| --- | --- | --- | --- | --- |
| `2` | `78fb459` | `test: freeze corr cov rolling semantics` | `2` | `git diff --cached --check`; `pytest` -> `60 passed` |
| `3` | `2de094b` | `feat(native): add experimental corr cov prototype gate` | `11` | `git diff --cached --check`; `cargo.exe check` pass; base `pytest` -> `11 passed, 2 skipped`; native-enabled `pytest` -> `13 passed`; benchmark smoke -> `REJECT` |
| `4` | `d8471f8` | `docs: finalize dirty tree separation state` | `6` | `git diff --cached --check`; `YAML_PARSE_STATUS: MANUAL_ONLY` |

## Files Left Dirty

| File | Bucket | Reason Left Dirty |
| --- | --- | --- |
| `.vscode/extensions.json` | `PRE_EXISTING_USER_CHANGE` | Pre-existing editor config change. |
| `conftest.py` | `PRE_EXISTING_USER_CHANGE` | Pre-existing test harness change. |
| `docs/current/README.md` | `PRE_EXISTING_USER_CHANGE` | Pre-existing docs work outside corr/cov scope. |
| `docs/design.md` | `PRE_EXISTING_USER_CHANGE` | Pre-existing design doc edits. |
| `docs/functions.md` | `HUMAN_DECISION_REQUIRED` | Mixed EMA/MACD ownership plus corr/cov notes. |
| `docs/language.md` | `PRE_EXISTING_USER_CHANGE` | Pre-existing language doc edits. |
| `expressions.yaml` | `PRE_EXISTING_USER_CHANGE` | Pre-existing DSL workload change. |
| `expressions.zip` | `PRE_EXISTING_USER_CHANGE` | Pre-existing tracked deletion needs owner call. |
| `outputs/alpha101_data_parquet_20260417_113656/README.md` | `PRE_EXISTING_USER_CHANGE` | Tracked output doc owned outside this cleanup. |
| `outputs/alpha101_selected10_data_parquet_20260417_114240/README.md` | `PRE_EXISTING_USER_CHANGE` | Tracked output doc owned outside this cleanup. |
| `outputs/alpha101_selected10_data_parquet_20260417_114240/selection_report.md` | `PRE_EXISTING_USER_CHANGE` | Tracked output report owned outside this cleanup. |
| `scratch_test/hello.txt` | `PRE_EXISTING_USER_CHANGE` | Scratch file with unknown owner intent. |
| `src/factor_engine/ast_nodes.py` | `PRE_EXISTING_USER_CHANGE` | Pre-existing parser/runtime feature work. |
| `src/factor_engine/errors.py` | `PRE_EXISTING_USER_CHANGE` | Pre-existing core error-path change. |
| `src/factor_engine/executor.py` | `PRE_EXISTING_USER_CHANGE` | Pre-existing executor change outside isolated native gate. |
| `src/factor_engine/lexer.py` | `PRE_EXISTING_USER_CHANGE` | Pre-existing parser/DSL change. |
| `src/factor_engine/parser.py` | `PRE_EXISTING_USER_CHANGE` | Pre-existing parser/DSL change. |
| `src/factor_engine/registry.py` | `PRE_EXISTING_USER_CHANGE` | Pre-existing registry change outside isolated native gate. |
| `src/factor_engine/tokens.py` | `PRE_EXISTING_USER_CHANGE` | Pre-existing parser/DSL change. |
| `src/factor_engine/validator.py` | `PRE_EXISTING_USER_CHANGE` | Pre-existing validation change. |
| `benchmarks/artifacts/native_corr_cov_ab.json` | `GENERATED_BENCHMARK_ARTIFACT` | Canonical generated artifact intentionally left uncommitted. |
| `benchmarks/reports/performance_truth_baseline.md` | `PRE_EXISTING_USER_CHANGE` | Pre-existing benchmark truth report. |
| `benchmarks/reports/performance_truth_scaleup.md` | `PRE_EXISTING_USER_CHANGE` | Pre-existing benchmark truth report. |
| `benchmarks/scripts/benchmark_mixed_segmented_ordered_sorting.py` | `PRE_EXISTING_USER_CHANGE` | Pre-existing benchmark script. |
| `benchmarks/scripts/benchmark_ordered_finalize_restore.py` | `PRE_EXISTING_USER_CHANGE` | Pre-existing benchmark script. |
| `benchmarks/scripts/benchmark_rolling_operators.py` | `PRE_EXISTING_USER_CHANGE` | Pre-existing benchmark script. |
| `benchmarks/scripts/performance_truth_common.py` | `PRE_EXISTING_USER_CHANGE` | Pre-existing benchmark support code. |
| `docs/architecture/full_native_rolling_engine_plan.md` | `HUMAN_DECISION_REQUIRED` | Future full-native design doc left outside this separation pass. |
| `docs/architecture/rolling_operator_semantics_matrix.md` | `HUMAN_DECISION_REQUIRED` | Broader multi-operator readiness matrix left outside this separation pass. |
| `docs/architecture/dirty_tree_final_separation_report.md` | `GOVERNANCE_DOCS_ALREADY_COMMITTED_OR_LEFTOVER` | Intentionally left uncommitted so it can truthfully record group 4 hash. |
| `docs/current/macd_capability_audit.md` | `PRE_EXISTING_USER_CHANGE` | Pre-existing MACD docs work. |
| `docs/performance_memory_self_audit.md` | `PRE_EXISTING_USER_CHANGE` | Pre-existing performance audit work. |
| `examples/macd_ema_dsl_example.py` | `PRE_EXISTING_USER_CHANGE` | Pre-existing example work. |
| `src/factor_engine.egg-info/PKG-INFO` | `CACHE_OR_TEMP` | Generated packaging metadata. |
| `src/factor_engine.egg-info/SOURCES.txt` | `CACHE_OR_TEMP` | Generated packaging metadata. |
| `src/factor_engine.egg-info/dependency_links.txt` | `CACHE_OR_TEMP` | Generated packaging metadata. |
| `src/factor_engine.egg-info/top_level.txt` | `CACHE_OR_TEMP` | Generated packaging metadata. |
| `tests/integration/test_ema_operator.py` | `PRE_EXISTING_USER_CHANGE` | Pre-existing unrelated integration test. |

## Human Decision Required

Count: `32`

| File | Reason Human Decision Required | Suggested Human Action |
| --- | --- | --- |
| `.vscode/extensions.json` | Pre-existing editor config change. | `inspect diff manually` |
| `conftest.py` | Pre-existing test harness change. | `commit in separate feature` |
| `docs/current/README.md` | Pre-existing docs work outside corr/cov scope. | `keep for later review` |
| `docs/design.md` | Pre-existing design doc edits. | `keep for later review` |
| `docs/functions.md` | Mixed EMA/MACD ownership plus corr/cov notes. | `inspect diff manually` |
| `docs/language.md` | Pre-existing language doc edits. | `keep for later review` |
| `expressions.yaml` | Pre-existing DSL workload change. | `commit in separate feature` |
| `expressions.zip` | Pre-existing tracked deletion needs owner call. | `discard only by explicit human instruction` |
| `outputs/alpha101_data_parquet_20260417_113656/README.md` | Tracked output doc owned outside this cleanup. | `inspect diff manually` |
| `outputs/alpha101_selected10_data_parquet_20260417_114240/README.md` | Tracked output doc owned outside this cleanup. | `inspect diff manually` |
| `outputs/alpha101_selected10_data_parquet_20260417_114240/selection_report.md` | Tracked output report owned outside this cleanup. | `inspect diff manually` |
| `scratch_test/hello.txt` | Scratch file with unknown owner intent. | `keep for later review` |
| `src/factor_engine/ast_nodes.py` | Pre-existing parser/runtime feature work. | `move to separate branch` |
| `src/factor_engine/errors.py` | Pre-existing core error-path change. | `move to separate branch` |
| `src/factor_engine/executor.py` | Pre-existing executor change outside isolated native gate. | `move to separate branch` |
| `src/factor_engine/lexer.py` | Pre-existing parser/DSL change. | `move to separate branch` |
| `src/factor_engine/parser.py` | Pre-existing parser/DSL change. | `move to separate branch` |
| `src/factor_engine/registry.py` | Pre-existing registry change outside isolated native gate. | `move to separate branch` |
| `src/factor_engine/tokens.py` | Pre-existing parser/DSL change. | `move to separate branch` |
| `src/factor_engine/validator.py` | Pre-existing validation change. | `move to separate branch` |
| `benchmarks/reports/performance_truth_baseline.md` | Pre-existing benchmark truth report. | `inspect diff manually` |
| `benchmarks/reports/performance_truth_scaleup.md` | Pre-existing benchmark truth report. | `inspect diff manually` |
| `benchmarks/scripts/benchmark_mixed_segmented_ordered_sorting.py` | Pre-existing benchmark script. | `commit in separate feature` |
| `benchmarks/scripts/benchmark_ordered_finalize_restore.py` | Pre-existing benchmark script. | `commit in separate feature` |
| `benchmarks/scripts/benchmark_rolling_operators.py` | Pre-existing benchmark script. | `commit in separate feature` |
| `benchmarks/scripts/performance_truth_common.py` | Pre-existing benchmark support code. | `commit in separate feature` |
| `docs/architecture/full_native_rolling_engine_plan.md` | Future full-native design doc outside current separation boundary. | `keep for later review` |
| `docs/architecture/rolling_operator_semantics_matrix.md` | Broader multi-operator readiness matrix exceeds isolated corr/cov freeze. | `keep for later review` |
| `docs/current/macd_capability_audit.md` | Pre-existing MACD docs work. | `keep for later review` |
| `docs/performance_memory_self_audit.md` | Pre-existing performance audit work. | `keep for later review` |
| `examples/macd_ema_dsl_example.py` | Pre-existing example work. | `commit in separate feature` |
| `tests/integration/test_ema_operator.py` | Pre-existing unrelated integration test. | `commit in separate feature` |

## Native Corr/Cov Status

- default enabled: `no`
- env gated: `yes`
- current A/B decision: `REJECT`
- production rollout: `no`
- full native rolling implementation: `not started`

## Implementation Readiness

`NEEDS_HUMAN_DIRTY_FILES_REVIEW`
