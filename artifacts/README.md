# Artifacts

`artifacts/` is the default local home for files produced or consumed during development, benchmarking, profiling, and experiments.

The directory is ignored by Git except for this README and `.gitkeep` placeholders.

Use the subdirectories as follows:

- `benchmark_runs/`: full benchmark run outputs.
- `profiling/`: profiling traces and detailed execution artifacts.
- `tmp/`: temporary local work files.
- `outputs/`: generated result files.
- `local_data/`: externally supplied local data.

Do not commit real data, large generated results, or profiling dumps.

