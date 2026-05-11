# Tests

`tests/` is physically layered by test responsibility. The default pytest entry remains the same:

```powershell
$env:PYTHONPATH="src"
python -m pytest -q
```

## Layout

- `unit/`: parser, lexer, validator, registry, isolated operators, and small local behavior checks.
- `integration/`: `FactorEngine`, planner plus executor behavior, DAG/CSE, ordered paths, FFT/table behavior, and smoke coverage.
- `workflow/`: file/workflow IO, workflow error handling, workflow benchmarking plumbing, and run summaries.
- `native/`: tests that require or directly target the native extension boundary. This layer is reserved for future native-only tests.
- `perf/`: timing or benchmark-like tests that are useful for performance signals but should stay separate from unit coverage.
- `profiling/`: execution profile, memory/profile events, and lifecycle profiling behavior.

Do not move tests across layers as part of a source refactor unless the behavior is already protected by a passing baseline.
