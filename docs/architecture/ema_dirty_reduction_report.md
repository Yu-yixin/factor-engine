# EMA Dirty Reduction Report

## Preflight Snapshot

- branch: `feature/ema-macd-experiment`
- starting dirty file count for this reduction pass: `29`
- starting staged file count: `0`
- safety rule: `expressions.zip` must remain untouched throughout this pass
- note: the starting count is `29` rather than `28` because the prior read-only
  inventory step intentionally created `docs/architecture/ema_dirty_inventory.md`

Starting dirty file list:

```text
 M .vscode/extensions.json
 M conftest.py
 M docs/current/README.md
 M docs/design.md
 M docs/functions.md
 M docs/language.md
 M expressions.yaml
 D expressions.zip
 M outputs/alpha101_data_parquet_20260417_113656/README.md
 M outputs/alpha101_selected10_data_parquet_20260417_114240/README.md
 M outputs/alpha101_selected10_data_parquet_20260417_114240/selection_report.md
 M scratch_test/hello.txt
 M src/factor_engine/ast_nodes.py
 M src/factor_engine/errors.py
 M src/factor_engine/executor.py
 M src/factor_engine/lexer.py
 M src/factor_engine/parser.py
 M src/factor_engine/registry.py
 M src/factor_engine/tokens.py
 M src/factor_engine/validator.py
?? benchmarks/artifacts/native_corr_cov_ab.json
?? docs/architecture/dirty_tree_final_separation_report.md
?? docs/architecture/ema_dirty_inventory.md
?? docs/architecture/full_native_rolling_engine_plan.md
?? docs/architecture/rolling_operator_semantics_matrix.md
?? docs/current/macd_capability_audit.md
?? docs/performance_memory_self_audit.md
?? examples/macd_ema_dsl_example.py
?? tests/integration/test_ema_operator.py
```

## Reduction Log

This report will be updated after:

1. Group 1 EMA experiment commits
2. Group 3 restore/move operations
3. Group 2 review documentation
4. validation and final dirty-tree confirmation

## Group 1 Outcome

Runtime commit created:

- `5ea7e16` `feat(ema): add experimental EMA DSL operator path`

Notes:

- semantic EMA runtime changes were narrowed to:
  - `src/factor_engine/executor.py`
  - `src/factor_engine/registry.py`
  - `src/factor_engine/validator.py`
- `src/factor_engine/ast_nodes.py`
- `src/factor_engine/errors.py`
- `src/factor_engine/lexer.py`
- `src/factor_engine/parser.py`
- `src/factor_engine/tokens.py`

were reviewed and restored because their dirty state was line-ending noise only.

Test/example commit created:

- `18f3ccf` `test(ema): cover experimental EMA operator behavior`

Docs commit created:

- `b83c553` `docs(ema): document experimental EMA and MACD capability`

Group 2 description commit created:

- `d68da24` `docs: describe unresolved EMA-adjacent dirty files`

## Group 3 Outcome

Restored tracked local-only files:

- `.vscode/extensions.json`
- `conftest.py`
- `docs/current/README.md`
- `expressions.yaml`
- `outputs/alpha101_data_parquet_20260417_113656/README.md`
- `outputs/alpha101_selected10_data_parquet_20260417_114240/README.md`
- `outputs/alpha101_selected10_data_parquet_20260417_114240/selection_report.md`
- `scratch_test/hello.txt`

Moved generated artifact out of the repository working tree:

- from `benchmarks/artifacts/native_corr_cov_ab.json`
- to `C:\Users\yuyix\Desktop\factor-engine-local-artifacts\native_corr_cov_ab.json`

## Remaining Dirty Before Final Docs Commit

At this point the remaining dirty files are:

```text
 D expressions.zip
?? docs/architecture/dirty_tree_final_separation_report.md
?? docs/architecture/ema_dirty_inventory.md
?? docs/architecture/ema_dirty_reduction_report.md
?? docs/architecture/full_native_rolling_engine_plan.md
?? docs/architecture/rolling_operator_semantics_matrix.md
?? docs/performance_memory_self_audit.md
```

Planned final action:

- commit the six untracked documentation/report files listed above
- leave `expressions.zip` untouched and unresolved

## Final Intent

Target final status after the final docs commit:

```text
 D expressions.zip
```

Reason it remains dirty:

- the file is opaque, tracked, and explicitly protected by the safety rules
- it was not inspected or altered in this reduction pass
- it requires a separate human decision

## Validation Results

- `pytest`: `562 passed, 2 skipped`
- `cargo check`: `PASS`

Validation commands run:

```text
../factor-engine/.venv/Scripts/python.exe -m pytest
cargo.exe check --target-dir C:\Users\yuyix\Desktop\factor-engine\native\factor_engine_native\target
git status --short --untracked-files=all
git log --oneline --decorate -n 8
```

## Final Dirty Tree

Actual final status after validation:

```text
 D expressions.zip
```

Unexpected remaining dirty files:

- none

## Final Outcome

- Group 1 committed: `yes`
- Group 3 cleaned/restored/moved: `yes`
- Group 2 description doc created: `yes`
- reset used: `no`
- clean used: `no`
- `expressions.zip` touched: `no`
- ready for `expressions.zip` decision: `yes`
