# Benchmarks

`benchmarks/` separates executable benchmark entry points from curated reports and historical snapshots.

## Layout

- `scripts/`: benchmark and profiling scripts. These should remain runnable from the repository root with `PYTHONPATH=src`.
- `reports/`: curated human-readable summaries and decision reports that are useful to keep in Git.
- `latest/`: local recent-run landing area. Detailed generated outputs should normally stay untracked.
- `archive/`: historical benchmark snapshots retained for context.

Detailed run artifacts are not tracked by default. This includes `latest_*`, `history.csv`, JSONL traces, memory events, node execution details, and stage event dumps.

Full benchmark runs should go under `artifacts/benchmark_runs/`. Profiling traces should go under `artifacts/profiling/`.
