# Native Workflow Trust Rules

## Hard Rules

- Do not change public DSL semantics without docs and golden tests.
- Do not enable native rolling by default without A/B `ACCEPT`.
- Do not silently change null or `NaN` behavior.
- Do not claim RSS release from logical drop alone.
- Do not leave benchmark artifacts in source directories.
- Do not track `__pycache__`, `.pyc`, local data, env files, or Rust target directories.
- Do not make broad executor or planner refactors before benchmark evidence.

## Phase Exit Checklist

- `git status --short`
- targeted pytest run
- benchmark report path recorded
- architecture/current docs updated
- `.ai_state/current.yaml` updated
- commit created only when the worktree is intentionally ready and unrelated dirty files are understood

## Current Native corr/cov State

The prototype is isolated in `src/factor_engine/native_corr_cov.py` and `native/factor_engine_native/src/rolling_moments.rs`. Production corr/cov execution remains Polars-backed until rollout evidence says otherwise.
