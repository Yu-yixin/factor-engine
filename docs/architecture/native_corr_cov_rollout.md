# Native corr/cov Guarded Rollout

## Default State

`corr` and `cov` remain Polars-backed by default. The native prototype is opt-in only:

- disabled: `FACTOR_ENGINE_NATIVE_CORR_COV=0`
- enabled for parity or benchmark work: `FACTOR_ENGINE_NATIVE_CORR_COV=1`
- optional group parallelism: `FACTOR_ENGINE_NATIVE_CORR_COV_PARALLEL=1`

No native corr/cov path may become default until the A/B gate records `ACCEPT`.

## Enable Conditions

- `tests/unit/test_corr.py`, `tests/unit/test_cov.py`, and `tests/unit/test_corr_cov_golden.py` pass.
- Native parity tests pass when the extension is installed.
- `benchmarks/reports/native_corr_cov_ab.md` records `ACCEPT`.
- Median total wall-time speedup is at least `1.25x`.
- Native CV is at most `0.15`.
- Peak RSS is not materially worse.
- Fallback preserves current Polars semantics.

## Disable Conditions

- Any null or `NaN` mask mismatch.
- Numeric mismatch greater than `1e-12` in golden/parity tests.
- Benchmark result is `REJECT`, `PENDING`, or `NOT_RUN`.
- Bridge cost erases kernel benefit.
- Native extension import or kernel execution fails.
- Profile cannot identify whether native or fallback was used.

## Fallback Conditions

- env flag is disabled
- native extension is unavailable
- unsupported dtype or unsupported expression shape
- Rust kernel raises an error
- output construction fails

Fallback must be semantically invisible: users get the current Polars result.

## Known Risks

- Rolling moment add/remove formulas can accumulate floating-point drift.
- `NaN` must remain distinct from null.
- Pairwise validity is stricter than one-input rolling null handling.
- Kernel-only timing can look good while total wall time loses.
- Logical buffer release does not imply immediate RSS reduction.

## Evidence

Current report path: `benchmarks/reports/native_corr_cov_ab.md`.

Current artifact path: `benchmarks/artifacts/native_corr_cov_ab.json`.
