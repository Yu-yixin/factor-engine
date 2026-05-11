# Data

`data/` is for local data used during development, experiments, and benchmarks.

Large data files must not be committed. Real, private, business, or otherwise sensitive data must not be committed.

Tests should use small sanitized fixtures or generated data. Benchmark and real-data runs should document the required schema and accept externally supplied files.

Historical large data files may still exist locally after Phase 2, but they are no longer intended to be tracked by Git.

