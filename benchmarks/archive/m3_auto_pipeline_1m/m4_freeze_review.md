# M4 Freeze Readiness Review

```yaml
accepted_candidates:
  - m4_cse_expand_repeated_subgraphs
  - m4_fuse_deep_operator_chains
rejected_candidates:
dominant_bottleneck_class: wide_fanout
required_candidate_classes_tested: true
structure_is_primary_bottleneck: true
optimization_space_exhausted: true
freeze_path: strong_success
safe_to_consider_freeze: true
safe_to_freeze: true
m4_frozen: true
```

## Accepted

- `m4_cse_expand_repeated_subgraphs`
- `m4_fuse_deep_operator_chains`

## Rejected


## Conclusion

M4 is frozen under the strong-success path. The required CSE and fusion classes have both been tested and accepted, and the result is now a bounded structural conclusion rather than an open-ended optimization hunt.

## Final Value Summary

- M3 closed because attach/projection/materialization-threshold candidates did not show durable positive value at the 1M scale.
- M4 succeeded because localized CSE expansion and minimal unary-chain fusion both produced positive, benchmarked, guardrailed results.
- The remaining dominant residual class is `wide_fanout`.
- M4 stops now because the strong-success freeze path is satisfied; continuing into elimination, batching, or heavy-path rewrite would expand risk faster than it improves certainty.

## Frozen Boundary

- no new M4 proposal is introduced in the current cycle
- no materialized-intermediate elimination in the current freeze window
- no wide-fanout batching in the current freeze window
- no heavy-path rewrite in the current freeze window
- accepted knobs are retained:
  - `planner_cse_mode=expanded_repeated_family`
  - `fusion_mode=unary_chain_fusion`
- untested high-risk structural classes remain deferred, not failed work

## Reopen Conditions

M4 may only be reopened when at least one of these conditions is met:

- a new workload shows materially larger wide-fanout pressure than the freeze workload
- either accepted candidate becomes unstable on real data
- a refreshed structural report identifies a new dominant family
- a deliberate new M4+ cycle is opened with its own proposal/executable/score contract
