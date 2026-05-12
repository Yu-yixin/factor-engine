# Profiling Schema

This document freezes the current profiling and benchmark output contract before Phase 3 executor refactoring. It is based on `src/factor_engine/profiling.py`, `tests/profiling/`, and benchmark scripts. If a field is not fully described here, the current tests and scripts remain the source of truth until a later schema snapshot test locks it down.

## Output Files

| File | Purpose | Generator | Consumers | Git policy | Artifact policy | Compatibility |
| --- | --- | --- | --- | --- | --- | --- |
| `latest_run.json` | Top-level run summary for a profiling/benchmark run. | `StageLifecycleProfiler.persist()` and related profiling persistence code. | Benchmark readers, run summaries, manual inspection. | Generated latest files do not enter Git by default. | Belongs under `artifacts/benchmark_runs/` or `artifacts/profiling/` for local runs. | Field names and default values must remain stable unless a migration is documented. |
| `history.csv` | Append-friendly run history for comparison over time. | Profiling/benchmark persistence layer. | Benchmark trend checks and manual comparison. | Generated history files do not enter Git by default. | Artifact. | Columns must not be removed casually. |
| `latest_stage_details.jsonl` | Per-stage lifecycle details. | `StageLifecycleProfiler` from stage registry snapshots. | `tests/profiling`, lifecycle reports, benchmark analysis. | Generated latest files do not enter Git. | Artifact. | Stage field names are compatibility-sensitive. |
| `latest_memory_events.jsonl` | Memory/output/native-buffer event stream. | Executor runtime profiling hooks. | `tests/profiling`, memory/lifecycle analysis. | Generated latest files do not enter Git. | Artifact. | Event keys and default/null behavior must remain stable. |
| `latest_node_execution_details.jsonl` | DAG/CSE node execution and materialization accounting. | Executor DAG/CSE profiling hooks. | Benchmark reports and profiling tests. | Generated latest files do not enter Git. | Artifact. | Existing key names must not change during refactor. |
| `latest_output_details.jsonl` | Output creation, attach, release, and final retention details. | Executor runtime output tracking. | `tests/profiling`, lifecycle/output reports. | Generated latest files do not enter Git. | Artifact. | Output field names must remain stable. |
| `latest_native_buffer_details.jsonl` | Native output buffer lifecycle details. | Executor native-buffer profiling hooks. | `tests/profiling`, native/lifecycle analysis. | Generated latest files do not enter Git. | Artifact. | Native buffer keys and default values must not change. |
| `latest_positional_phase_details.jsonl` | Positional ordered phase timings and native/fallback flags. | Executor positional ordered path. | Native fallback tests, benchmark reports. | Generated latest files do not enter Git. | Artifact. | Native/fallback boolean fields are compatibility-sensitive. |

Native corr/cov prototype profile fields are reserved for guarded rollout:
`native_corr_cov_used`, `native_corr_cov_time_ms`,
`native_corr_cov_bridge_time_ms`, `native_corr_cov_output_build_time_ms`,
`native_corr_cov_fallback_reason`, `native_corr_cov_pair_count`,
`native_corr_cov_window`, and `native_corr_cov_null_mode`.

## Field Compatibility Principles

- Field names must not be renamed casually.
- Existing fields must not be removed casually.
- Default values and `None` behavior must not change during helper extraction.
- Benchmark acceptance and profiling tests depend on these fields.
- Profiling refactors may move builder/recorder code, but must not change schema.
- If schema is uncertain, `tests/profiling` and benchmark scripts are the current truth source.
- A future schema snapshot test should freeze representative records for each output file.

## Refactor Boundary

Allowed in Phase 3.2:

- Move event/detail builders.
- Move default field/schema constants.
- Move formatting helpers that produce the same dataclass fields.

Not allowed in Phase 3.2:

- DataFrame execution changes.
- Lifecycle drop decision changes.
- DAG/CSE execution changes.
- Native fallback behavior changes.
- Benchmark report field changes.
