# Benchmarks

`benchmarks/` may contain benchmark scripts, curated human-readable summaries, and performance decision reports.

Detailed run artifacts are not tracked by default. This includes `latest_*`, `history.csv`, JSONL traces, memory events, node execution details, and stage event dumps.

Full benchmark runs should go under `artifacts/benchmark_runs/`. Profiling traces should go under `artifacts/profiling/`.

Future cleanup may split scripts, reports, and historical archives into separate directories. Phase 2 only de-tracks generated run details and documents the boundary.

