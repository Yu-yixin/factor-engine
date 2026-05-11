# M4.3 Fusion Candidate Report

- candidate: `m4_fuse_deep_operator_chains`
- selected family: `rolling_unary_chain_ts_mean_into_ts_rank`
- matched chains: `2`
- nodes reduced: `2`
- estimated intermediate eliminated: `16000`
- score: `0.450`
- decision: `ACCEPT`
- correctness pass: `True`
- audit explainable: `True`
- isolation pass: `True`

## Fusion Rules

- baseline: baseline materializes repeated expensive ts_mean and repeated expensive ts_rank nodes independently
- fused: for pure ts_rank(ts_mean(variable, w1), w2) repeated chains, the shared inner ts_mean stays transient while the outer ts_rank remains the materialized helper
- safe fusion rationale: the selected family is a single-parent unary rolling chain with no branching, no inner output retention, and no route or DSL semantic change

## Fused Chains

- `['n3', 'n4']`
- `['n3', 'n4']`
