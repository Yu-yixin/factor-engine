# Group 2 Review Descriptions

This document describes the remaining Group 2 dirty files after the EMA
experiment commits. It is intentionally review-first: no file below should be
auto-committed or auto-discarded without an explicit per-path decision.

## `conftest.py`

- path: `conftest.py`
- current git status: `M`
- tracked/untracked: `tracked`
- subsystem: pytest bootstrap / import path setup
- why it is not safe to auto-commit:
  - it affects global test discovery/import behavior
  - it can hide or reveal import-path problems unrelated to EMA
  - current semantic diff looks like line-ending noise only, not required EMA behavior
- why it is not safe to auto-discard:
  - if future EMA tests truly depend on an import-path fix, restoring now could hide that need
- recommended final decision: `restore/discard later`
- exact command if accepted:
  - `git add conftest.py`
- exact command if rejected:
  - `git restore -- conftest.py`

## `expressions.yaml`

- path: `expressions.yaml`
- current git status: `M`
- tracked/untracked: `tracked`
- subsystem: workload catalog / benchmark and workflow expression set
- why it is not safe to auto-commit:
  - it can change experiment workload coverage and benchmark inputs
  - current semantic diff looks like line-ending noise only, not a clearly intentional EMA workload addition
- why it is not safe to auto-discard:
  - if EMA expressions were intentionally being added to the workload catalog, restoring would lose that experimental scope
- recommended final decision: `restore/discard later`
- exact command if accepted:
  - `git add expressions.yaml`
- exact command if rejected:
  - `git restore -- expressions.yaml`

## `docs/current/README.md`

- path: `docs/current/README.md`
- current git status: `M`
- tracked/untracked: `tracked`
- subsystem: documentation index / current-state reading order
- why it is not safe to auto-commit:
  - it can create a misleading current-state narrative if linked docs are not yet accepted
  - it belongs with the EMA docs set only if the linked audit clearly says experiment-only
- why it is not safe to auto-discard:
  - if the EMA audit doc is kept, the index link may be useful and truthful
- recommended final decision: `move into EMA docs commit`
- exact command if accepted:
  - `git add docs/current/README.md`
- exact command if rejected:
  - `git restore -- docs/current/README.md`

## `docs/architecture/dirty_tree_final_separation_report.md`

- path: `docs/architecture/dirty_tree_final_separation_report.md`
- current git status: `??`
- tracked/untracked: `untracked`
- subsystem: governance / dirty-tree ownership audit
- why it is not safe to auto-commit:
  - it records a past separation state and must remain historically truthful
  - if later files were resolved differently, the report should not imply more than it actually captured
- why it is not safe to auto-discard:
  - it is the best record of the earlier mixed-ownership split and commit boundaries
- recommended final decision: `move into future native rolling research docs`
- exact command if accepted:
  - `git add docs/architecture/dirty_tree_final_separation_report.md`
- exact command if rejected:
  - `mkdir -p ../factor-engine-held/docs/architecture && mv docs/architecture/dirty_tree_final_separation_report.md ../factor-engine-held/docs/architecture/dirty_tree_final_separation_report.md`

## `docs/architecture/full_native_rolling_engine_plan.md`

- path: `docs/architecture/full_native_rolling_engine_plan.md`
- current git status: `??`
- tracked/untracked: `untracked`
- subsystem: future native rolling research planning
- why it is not safe to auto-commit:
  - it is not part of the EMA experiment itself
  - it could be misread as implementation approval if bundled carelessly
- why it is not safe to auto-discard:
  - it contains useful future-research boundary rules and rollout constraints
- recommended final decision: `move into future native rolling research docs`
- exact command if accepted:
  - `git add docs/architecture/full_native_rolling_engine_plan.md`
- exact command if rejected:
  - `mkdir -p ../factor-engine-held/docs/architecture && mv docs/architecture/full_native_rolling_engine_plan.md ../factor-engine-held/docs/architecture/full_native_rolling_engine_plan.md`

## `docs/architecture/rolling_operator_semantics_matrix.md`

- path: `docs/architecture/rolling_operator_semantics_matrix.md`
- current git status: `??`
- tracked/untracked: `untracked`
- subsystem: operator semantics reference / native-readiness matrix
- why it is not safe to auto-commit:
  - it makes readiness claims that should stay aligned with tested behavior
  - it is broader than the EMA experiment and could be mistaken for a stable roadmap commitment
- why it is not safe to auto-discard:
  - it is useful architecture context for future rolling-kernel research
- recommended final decision: `move into future native rolling research docs`
- exact command if accepted:
  - `git add docs/architecture/rolling_operator_semantics_matrix.md`
- exact command if rejected:
  - `mkdir -p ../factor-engine-held/docs/architecture && mv docs/architecture/rolling_operator_semantics_matrix.md ../factor-engine-held/docs/architecture/rolling_operator_semantics_matrix.md`

## `docs/performance_memory_self_audit.md`

- path: `docs/performance_memory_self_audit.md`
- current git status: `??`
- tracked/untracked: `untracked`
- subsystem: performance / memory audit documentation
- why it is not safe to auto-commit:
  - it contains performance interpretation and hypotheses that should not be overstated
  - it is adjacent to native rolling research rather than the EMA experiment
- why it is not safe to auto-discard:
  - it is a useful audit artifact for later benchmark and memory work
- recommended final decision: `move into future native rolling research docs`
- exact command if accepted:
  - `git add docs/performance_memory_self_audit.md`
- exact command if rejected:
  - `mkdir -p ../factor-engine-held/docs && mv docs/performance_memory_self_audit.md ../factor-engine-held/docs/performance_memory_self_audit.md`
