# M4.2 CSE Candidate Report

- candidate: `m4_cse_expand_repeated_subgraphs`
- selected family: `rolling_neutral_add_input`
- matched groups: `2`
- reused groups: `2`
- estimated helper bytes saved: `16000000`
- score: `1.556`
- decision: `ACCEPT`
- correctness pass: `True`
- audit explainable: `True`
- isolation pass: `True`

## Identity Rules

- baseline: baseline keeps the full first-argument subtree in rolling call identity
- expanded: for ts_rank/ts_mean only, first argument var+0 or 0+var canonicalizes to var
- baseline miss reason: neutral pointwise add creates a distinct child identity despite identical numeric value
- safe merge rationale: x + 0 and 0 + x are value-preserving for the numeric rolling inputs in this selected family

## Affected Signatures

- `('call', 'ts_mean', ('function_context', 'time_series', 'rolling', True, 'time', True, 'ths_code'), (('var', 'close'), ('number', 10)), ())`
- `('call', 'ts_rank', ('function_context', 'time_series', 'rolling', True, 'time', True, 'ths_code'), (('var', 'close'), ('number', 10)), (('ascending', ('boolean', False)), ('pct', ('boolean', False))))`
