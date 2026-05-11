# Benchmark And Profiling Policy

Benchmark material must be split by role. Mixing scripts, summaries, raw profiling traces, and temporary outputs makes the repository hard to trust.

## Categories

- Benchmark scripts: runnable code that defines workloads and measurements.
- Benchmark reports: curated summaries used for decisions.
- Profiling artifacts: detailed traces such as `latest_run.json`, `latest_*_details.jsonl`, event logs, and memory/node/stage records.
- Temporary outputs: scratch files created while investigating a local run.

## Git Rules

- Benchmark scripts may be committed.
- Selected benchmark summaries may be committed when they explain context, data size, machine assumptions, and the decision they supported.
- Performance decision reports may remain in Git, but they must name their context and should not masquerade as universal current truth.
- `latest_*.jsonl` must not be committed.
- `history.csv` is not committed by default.
- Large run artifacts and profiling directories must not be committed.
- Temporary benchmark outputs must go under ignored artifact locations.

## Recommended Layout Going Forward

- Keep scripts in a clear scripts location in a later phase.
- Keep curated summaries in a small, reviewable reports location.
- Put full runs under `artifacts/benchmark_runs/`.
- Put profiling traces under `artifacts/profiling/`.

Phase 1 only establishes these rules. It does not move existing benchmark history.

