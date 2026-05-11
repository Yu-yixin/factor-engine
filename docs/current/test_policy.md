# Test Policy

This document defines the desired test layering. Phase 1 does not move existing test files.

## Proposed Markers

- `unit`: small, fast tests for isolated logic.
- `integration`: tests spanning parser, validator, planner, and executor behavior.
- `workflow`: file or batch workflow tests.
- `native`: tests requiring the optional native extension or native-specific environment.
- `slow`: tests that are correct but not suitable for every quick local run.
- `perf`: performance-sensitive tests or benchmark gates.
- `profiling`: tests that assert profiling artifact shape or lifecycle metrics.

## Daily Fast Tests

The daily target should be a quick command that exercises core semantics without relying on large local data, native builds, or benchmark artifacts.

Current baseline command:

```powershell
$env:PYTHONPATH="src"
py -m pytest -q
```

On shells without the `py` launcher, use the active environment's Python:

```bash
PYTHONPATH=src python -m pytest -q
```

## Slow Tests

Slow tests should be marked and run explicitly. They may cover larger data shapes, lifecycle sweeps, or more complete workflow behavior.

## Native Tests

Native tests must be optional. They should skip clearly when the native extension is not installed or when native execution is disabled.

## Perf And Profiling Tests

Performance and profiling tests should not run by default. They may validate benchmark plumbing, output schemas, and regression gates, but they should not depend on large tracked data files.

Phase 1 only records the policy. Test migration and marker application belong to a later phase.

