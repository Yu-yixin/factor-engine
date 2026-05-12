# EMA Merge Readiness Review

## Scope

- branch reviewed: `feature/ema-macd-experiment`
- comparison target: `master`
- review mode: inspection-first, no merge performed
- worktree status at review time: `clean`

## Changed Files

| File Path | Change Type | Category | Merge Risk | Reason | Recommended Action |
| --- | --- | --- | --- | --- | --- |
| `docs/architecture/dirty_tree_final_separation_report.md` | `A` | `DOC` | `medium` | Historical governance snapshot is useful context, but it is not part of the EMA feature surface and can be read as stale current state if merged casually. | `review` |
| `docs/architecture/ema_dirty_inventory.md` | `A` | `DOC` | `high` | This file records a past dirty-tree snapshot and is intentionally historical, so it can mislead readers if treated as current branch state. | `defer` |
| `docs/architecture/ema_dirty_reduction_report.md` | `A` | `DOC` | `medium` | The report is now truthful about `expressions.zip`, but it still documents branch-cleanup history rather than EMA runtime semantics. | `review` |
| `docs/architecture/full_native_rolling_engine_plan.md` | `A` | `DOC` | `medium` | Future native-rolling planning is outside the EMA operator change and should not be mistaken for accepted implementation scope. | `defer` |
| `docs/architecture/group2_review_descriptions.md` | `A` | `DOC` | `high` | This is a review log for previously dirty files, not a stable product-facing artifact, and it uses historical decision framing. | `defer` |
| `docs/architecture/rolling_operator_semantics_matrix.md` | `A` | `DOC` | `medium` | The semantics matrix is potentially valuable, but it makes broad readiness statements that need separate truthfulness review. | `review` |
| `docs/current/macd_capability_audit.md` | `A` | `DOC` | `low` | The audit clearly states the stable baseline does not accept EMA/MACD and describes the branch as experiment-only. | `merge` |
| `docs/design.md` | `M` | `DOC` | `low` | The design note adds an explicit experimental EMA operator path without claiming stable rollout. | `merge` |
| `docs/functions.md` | `M` | `DOC` | `medium` | The function reference is technically consistent, but it is easy to misread as stable contract unless the experimental qualifiers stay prominent. | `review` |
| `docs/language.md` | `M` | `DOC` | `low` | The language note only adds an explicit experiment-branch boundary for `ema(...)`. | `merge` |
| `docs/performance_memory_self_audit.md` | `A` | `DOC` | `medium` | Audit material is useful background, but it is not required to land the EMA experiment and may contain context-specific performance interpretation. | `defer` |
| `examples/macd_ema_dsl_example.py` | `A` | `EXAMPLE` | `low` | The example is explicitly marked experimental and demonstrates composition without implying a production `macd()` primitive. | `merge` |
| `src/factor_engine/executor.py` | `M` | `RUNTIME` | `medium` | The only behavioral addition is an explicit `ema(...)` execution path, but it touches ordered evaluation semantics and should merge with deliberate review. | `review` |
| `src/factor_engine/registry.py` | `M` | `RUNTIME` | `medium` | Registry metadata introduces the recursive ordered contract for `ema`, which is targeted but affects planner-visible semantics. | `review` |
| `src/factor_engine/validator.py` | `M` | `RUNTIME` | `medium` | Validator changes are narrow and explicit to `ema` span rules, but they participate in the user-facing DSL contract. | `review` |
| `tests/integration/test_ema_operator.py` | `A` | `TEST` | `low` | The integration suite directly freezes the experimental EMA path and guards against a stray `macd()` primitive. | `merge` |

## Runtime Semantic Review

Inspected runtime files:

- `src/factor_engine/executor.py`
- `src/factor_engine/registry.py`
- `src/factor_engine/validator.py`

Observed change surface:

- `executor.py` adds a single explicit dispatch for `ema(...)` and a dedicated `_compile_ema()` implementation.
- `registry.py` registers `ema` as a `time_series` function with `window_kind="recursive"`, `needs_code_group=True`, and `needs_time_order=True`.
- `validator.py` adds a positive-integer literal contract for `span` and includes `ema` in numeric-returning functions.

Explicit review answers:

- Does EMA require time ordering? `Yes.` The registry contract requires `time` ordering and the tests validate ordered execution.
- Does EMA depend on code partitioning? `Yes.` The implementation uses per-`code` grouping and the registry requires `partition_by = ["code"]`.
- Does EMA preserve original row order after execution? `Yes.` The experiment reuses the existing ordered execution shell, and the integration tests assert the returned frame stays row-aligned with the input.
- Does EMA behave deterministically? `Yes, within the current tested contract.` The implementation is explicit, the span must be a positive integer literal, and tests compare results against a recursive reference.
- Does EMA introduce same-bar trading assumptions? `No explicit trading logic was added.` The branch adds an experimental EMA operator path only; it does not add signal/execution rules or claim live-trading readiness.
- Does EMA affect existing non-EMA expressions? `No direct code path change was found outside explicit ema handling.` Regression confidence mainly comes from the full pytest pass rather than new dedicated non-EMA regression tests.

Additional semantic notes:

- The implementation is an `experimental EMA operator path`, not a production-grade lifecycle freeze.
- EMA is intentionally modeled as ordered-recursive rather than as a rolling-window alias for `ts_mean`.
- No native/Rust boundary was touched by the EMA change set.

## Test Coverage Review

Validation commands run during review:

```text
.venv\Scripts\python.exe -m pytest
cargo check
```

Results:

- `pytest`: `562 passed, 2 skipped`
- `cargo check`: `pass`

Coverage observations:

- basic EMA correctness: `covered`
- warmup/null behavior: `covered`
- row-order restoration: `covered`
- per-code partition behavior: `covered`
- batch `evaluate_many` behavior: `covered`
- MACD expression composition: `covered`
- regression safety for existing expressions: `indirectly covered` by the full test suite, not by a new dedicated regression test file

Coverage caveats:

- There is no dedicated new test that asserts a representative non-EMA expression remains byte-for-byte unchanged in behavior.
- There is no separate test framed in trading-language terms around same-bar assumptions, which is acceptable for an engine-level expression experiment but should not be overstated in downstream docs.

## Documentation Consistency Review

Inspected documents:

- `docs/architecture/ema_dirty_inventory.md`
- `docs/architecture/group2_review_descriptions.md`
- `docs/architecture/ema_dirty_reduction_report.md`

Consistency findings:

- `ema_dirty_reduction_report.md` is consistent with the current branch state: it explains that `expressions.zip` had appeared as `D`, was restored with `git restore -- expressions.zip`, and the branch ended clean.
- `ema_dirty_inventory.md` is not a current-state snapshot anymore. It is a historical record of an earlier dirty-tree inspection and still lists files as dirty.
- `group2_review_descriptions.md` is also historical. It documents prior review decisions for files that are no longer dirty on this branch.

Implication:

- These historical docs are not wrong, but they need to be understood as audit trail documents rather than current-state inventory.
- That caveat keeps this branch out of a strict `MERGE_READY` rating and into `MERGE_READY_WITH_NOTES`.

## Merge Risk Decision

`MERGE_READY_WITH_NOTES`

Reasoning:

- the worktree is clean
- `pytest` passes
- `cargo check` passes
- the changed file set is explainable and bounded
- the runtime change is narrow and explicit to `ema(...)`
- no unexplained artifacts or secrets remain dirty
- the main remaining risk is documentation framing: several review/governance docs are historical snapshots and should be merged only if the target branch wants that audit trail

Recommended merge posture:

- safe to consider merging the experimental EMA runtime, test, example, and core experiment-status docs
- review before merging the broader governance/history docs
- defer unrelated future-native planning docs unless the target branch explicitly wants research context bundled with the EMA experiment
