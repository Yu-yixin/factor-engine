# Scripts

`scripts/` contains runnable project utilities that are not minimal usage examples and are not benchmark entry points.

## Layout

- `workflow/`: workflow and file-oriented command line helpers.
- `maintenance/`: repository maintenance helpers. Keep behavior explicit and documented before adding scripts here.
- `dev/`: local development probes or one-off developer utilities that are still worth tracking.

User-facing examples belong in `examples/`. Benchmark and profiling entry points belong in `benchmarks/scripts/`.
