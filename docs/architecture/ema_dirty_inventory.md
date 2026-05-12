# EMA Dirty Inventory

Inspection scope:

- branch: `feature/ema-macd-experiment`
- worktree: `C:\Users\yuyix\Desktop\factor-engine`
- mode: inspection only, no staging/commit/reset/clean

| File Path | Git Status Code | Tracked/Untracked | Likely Category | One-Line Reason | Recommended Action | Safe To Stage |
| --- | --- | --- | --- | --- | --- | --- |
| `.vscode/extensions.json` | `M` | `tracked` | `UNKNOWN` | Editor workspace recommendation file, not part of core engine/runtime semantics. | `review` | `no` |
| `conftest.py` | `M` | `tracked` | `TEST_ONLY` | Test bootstrap path file; affects pytest environment rather than production runtime. | `review` | `no` |
| `docs/current/README.md` | `M` | `tracked` | `DOC_ONLY` | Docs index update that appears to point at the MACD capability audit. | `review` | `unknown` |
| `docs/design.md` | `M` | `tracked` | `EMA_RELATED` | Design doc includes EMA/ordered-recursive framing and is tied to the experiment line. | `review` | `no` |
| `docs/functions.md` | `M` | `tracked` | `EMA_RELATED` | Function reference now documents `ema()` and MACD-shaped usage while the feature is not accepted. | `review` | `no` |
| `docs/language.md` | `M` | `tracked` | `EMA_RELATED` | Language rules mention EMA span constraints and therefore track the EMA DSL experiment. | `review` | `no` |
| `expressions.yaml` | `M` | `tracked` | `EMA_RELATED` | Expression workload catalog likely changed to exercise EMA/MACD paths. | `review` | `no` |
| `expressions.zip` | `D` | `tracked` | `SECRET_RISK` | Opaque tracked archive is deleted locally, so contents/ownership should be treated cautiously. | `discard later` | `no` |
| `outputs/alpha101_data_parquet_20260417_113656/README.md` | `M` | `tracked` | `GENERATED` | Output/report README under `outputs/` looks like run-generated documentation rather than source. | `keep` | `no` |
| `outputs/alpha101_selected10_data_parquet_20260417_114240/README.md` | `M` | `tracked` | `GENERATED` | Output/report README under `outputs/` looks like run-generated documentation rather than source. | `keep` | `no` |
| `outputs/alpha101_selected10_data_parquet_20260417_114240/selection_report.md` | `M` | `tracked` | `GENERATED` | Selection report under `outputs/` appears to be generated analysis output. | `keep` | `no` |
| `scratch_test/hello.txt` | `M` | `tracked` | `UNKNOWN` | Scratch file with no stable ownership signal beyond being local test debris. | `discard later` | `no` |
| `src/factor_engine/ast_nodes.py` | `M` | `tracked` | `EMA_RELATED` | Core AST file is part of the isolated EMA/MACD runtime change set. | `keep` | `no` |
| `src/factor_engine/errors.py` | `M` | `tracked` | `EMA_RELATED` | Error-path updates are part of the isolated EMA/MACD runtime change set. | `keep` | `no` |
| `src/factor_engine/executor.py` | `M` | `tracked` | `EMA_RELATED` | Executor contains the experimental EMA execution path and must stay outside the stable baseline. | `keep` | `no` |
| `src/factor_engine/lexer.py` | `M` | `tracked` | `EMA_RELATED` | Lexer change is part of the isolated EMA/MACD parser/runtime line. | `keep` | `no` |
| `src/factor_engine/parser.py` | `M` | `tracked` | `EMA_RELATED` | Parser change is part of the isolated EMA/MACD parser/runtime line. | `keep` | `no` |
| `src/factor_engine/registry.py` | `M` | `tracked` | `EMA_RELATED` | Registry change likely registers EMA semantics and therefore belongs to the experiment line. | `keep` | `no` |
| `src/factor_engine/tokens.py` | `M` | `tracked` | `EMA_RELATED` | Token definition change is part of the isolated EMA/MACD parser/runtime line. | `keep` | `no` |
| `src/factor_engine/validator.py` | `M` | `tracked` | `EMA_RELATED` | Validator change likely enforces EMA argument rules and is part of the experiment line. | `keep` | `no` |
| `benchmarks/artifacts/native_corr_cov_ab.json` | `??` | `untracked` | `GENERATED` | Native corr/cov A/B artifact is a generated benchmark output, not stable source. | `ignore` | `no` |
| `docs/architecture/dirty_tree_final_separation_report.md` | `??` | `untracked` | `DOC_ONLY` | Governance report from the earlier dirty-tree separation pass. | `review` | `unknown` |
| `docs/architecture/full_native_rolling_engine_plan.md` | `??` | `untracked` | `DOC_ONLY` | Future full-native design document, not part of accepted stable implementation scope. | `review` | `unknown` |
| `docs/architecture/rolling_operator_semantics_matrix.md` | `??` | `untracked` | `DOC_ONLY` | Readiness/semantics matrix with broader scope than the current accepted baseline. | `review` | `unknown` |
| `docs/current/macd_capability_audit.md` | `??` | `untracked` | `EMA_RELATED` | MACD/EMA audit directly describes the experiment and its non-acceptance constraints. | `review` | `no` |
| `docs/performance_memory_self_audit.md` | `??` | `untracked` | `DOC_ONLY` | Performance/memory self-audit note appears documentation-only and outside the stable core path. | `review` | `unknown` |
| `examples/macd_ema_dsl_example.py` | `??` | `untracked` | `EMA_RELATED` | Example script demonstrates EMA/MACD DSL usage from the experiment line. | `keep` | `no` |
| `tests/integration/test_ema_operator.py` | `??` | `untracked` | `TEST_ONLY` | Integration test exercises the experimental EMA operator path and should stay with that line. | `keep` | `no` |

## Notes

- `EMA_RELATED` means the file appears to belong to the isolated EMA/MACD experiment and should not be staged into the stable core baseline without deliberate review.
- `GENERATED` means the file looks like benchmark/output material rather than authored source.
- `SECRET_RISK` is used conservatively for `expressions.zip` because it is a tracked opaque archive whose local deletion should not be acted on blindly.
- `Safe To Stage` is intentionally conservative; `unknown` means the file is documentation-only but still may have ownership or truthfulness concerns.
