# Full Native Readiness After corr/cov Gate

## Native Extension Import

Status: `PASS`

Command:

```text
./.venv/Scripts/python.exe -c "import factor_engine_native; print(factor_engine_native.__file__)"
```

Result:

```text
C:\Users\yuyix\Desktop\factor-engine\.venv\Lib\site-packages\factor_engine_native\__init__.py
```

Build/install command used:

```text
./.venv/Scripts/python.exe -m maturin develop --manifest-path native/factor_engine_native/Cargo.toml
```

The installed package exposes:

```text
grouped_corr_cov
grouped_positional_extreme
grouped_positional_extreme_buffers
```

## Parity Tests

Status: `PASS`

The WSL shell env assignment did not propagate into the Windows Python process, so the native-enabled test was run with a Python wrapper that sets `os.environ` inside the process before invoking pytest.

Command shape:

```text
./.venv/Scripts/python.exe - <<'PY'
import os
import pytest
os.environ["FACTOR_ENGINE_NATIVE_CORR_COV"] = "1"
raise SystemExit(pytest.main([
    "tests/unit/test_native_corr_cov_parity.py",
    "tests/unit/test_corr_cov_golden.py",
]))
PY
```

Result:

```text
13 passed
```

## A/B Decision

Decision: `REJECT`

Command:

```text
./.venv/Scripts/python.exe benchmarks/scripts/benchmark_native_corr_cov.py --repeats 3
```

Report:

```text
benchmarks/reports/native_corr_cov_ab.md
```

Artifact:

```text
benchmarks/artifacts/native_corr_cov_ab.json
```

Result summary:

```text
native_used: true
median_speedup: 0.329x
worst_native_cv: 0.033
```

Native actually ran, but total wall time did not meet the `>= 1.25x` acceptance threshold. No native speedup is claimed.

## Dirty Tree Status

Status: `DIRTY_WITH_MIXED_OWNERSHIP`

Classification report:

```text
docs/architecture/native_corr_cov_dirty_tree_report.md
```

The tree contains:

- pre-existing dirty user/prior-work files
- pre-full-native corr/cov files
- generated A/B benchmark artifacts
- mixed ownership in `docs/functions.md`

No force commit should be created from this mixed state.

## Ready For Full Native Rolling Design

Status: `CONDITIONALLY_READY_FOR_DESIGN_REVIEW`

The repository now has golden corr/cov semantics, native import/build verification, a real native parity run, and an A/B gate result. That is enough to discuss the full native rolling design with evidence.

The design must account for the corr/cov prototype rejection: the current Python object bridge/native prototype is slower than Polars at reduced scale and must not be promoted.

## Ready For Full Native Rolling Implementation

Status: `NO`

Reasons:

- git status is still dirty with mixed ownership
- corr/cov native A/B decision is `REJECT`
- native corr/cov remains experimental and opt-in
- benchmark evidence does not support enabling or expanding this prototype

Implementation should wait until the dirty tree is separated and the next native rolling design chooses a bridge/kernel strategy that can beat total wall time, not just kernel time.
