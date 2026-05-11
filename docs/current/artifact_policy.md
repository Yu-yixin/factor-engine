# Artifact Policy

Runtime artifacts are not source. They should be kept outside Git by default.

Use this ignored layout for future generated files:

```text
artifacts/
├── benchmark_runs/
├── profiling/
├── tmp/
├── outputs/
└── local_data/
```

## Rules

- `artifacts/` is ignored by default and should not be committed.
- Large parquet, csv, database, sqlite, and jsonl files belong under `artifacts/`.
- Reproducible output files belong under `artifacts/outputs/`.
- Temporary profiling dumps belong under `artifacts/profiling/` or `artifacts/tmp/`.
- Real or local data belongs under `artifacts/local_data/`.
- Benchmark run directories belong under `artifacts/benchmark_runs/` unless a curated summary is intentionally committed.

## Small Data Exception

Small example data may be committed only when it is:

- small enough to keep clone and diff behavior healthy;
- sanitized and safe to share;
- documented with its purpose and schema;
- required for examples or tests.

When unsure, keep the data out of Git and document how to regenerate or obtain it.

