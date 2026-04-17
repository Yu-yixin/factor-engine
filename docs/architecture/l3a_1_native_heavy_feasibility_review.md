# L3A.1 Native-Heavy Feasibility Review

L3A.1 is a review stage. It does not implement native-heavy active drop, does not add a lifecycle mode, and does not change executor/helper behavior.

## Probe Scope

Commands run:

```text
examples/benchmark_r4_executor_reuse.py --rows 1000 --consumer-counts 2 --workloads native_heavy_probe,native_heavy_nested,native_heavy_multi_read --lifecycle-mode off
examples/benchmark_r4_executor_reuse.py --rows 1000000 --consumer-counts 2 --workloads native_heavy_probe,native_heavy_nested,native_heavy_multi_read --lifecycle-mode off
examples/benchmark_r4_executor_reuse.py --rows 0 --consumer-counts 2 --workloads native_heavy_multi_read --lifecycle-mode off
```

Artifacts:

- `benchmarks/l3a1_native_heavy_smoke`
- `benchmarks/l3a1_native_heavy_1m`
- `benchmarks/l3a1_native_heavy_full_key`

## Table 1: Gain Split

| workload | rows | cse | native compute ms | native path ms | native storage bytes | total sec |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| native_heavy_probe | 1,000 | off | 0.000 | 0.000 | 0 | 0.025 |
| native_heavy_probe | 1,000 | on | 5.011 | 0.000 | 8,000 | 0.013 |
| native_heavy_nested | 1,000 | off | 0.000 | 0.000 | 0 | 0.044 |
| native_heavy_nested | 1,000 | on | 5.503 | 0.000 | 8,000 | 0.017 |
| native_heavy_multi_read | 1,000 | off | 0.000 | 0.000 | 0 | 0.017 |
| native_heavy_multi_read | 1,000 | on | 4.825 | 0.000 | 8,000 | 0.014 |
| native_heavy_probe | 1,000,000 | off | 0.000 | 0.000 | 0 | 5.031 |
| native_heavy_probe | 1,000,000 | on | 2,500.806 | 0.000 | 8,000,000 | 2.634 |
| native_heavy_nested | 1,000,000 | off | 0.000 | 0.000 | 0 | 5.292 |
| native_heavy_nested | 1,000,000 | on | 2,378.887 | 0.000 | 8,000,000 | 2.592 |
| native_heavy_multi_read | 1,000,000 | off | 0.000 | 0.000 | 0 | 4.652 |
| native_heavy_multi_read | 1,000,000 | on | 2,105.781 | 0.000 | 8,000,000 | 2.240 |
| native_heavy_multi_read | 29,048,679 | off | 0.000 | 0.000 | 0 | 130.283 |
| native_heavy_multi_read | 29,048,679 | on | 63,726.643 | 0.000 | 232,389,432 | 71.879 |

Interpretation:

- CSE on cuts attributed native compute from two fallback occurrences to one node-store compute.
- The wall-clock gain is large and stable at 1M and full data.
- `native_path_normalization_time_ms` is currently a bookkeeping timer around store hits, so path normalization benefit is better inferred from `native_fallback_eval_count: 1 -> 0`, `native_rewrite_applied_count: 0 -> 1`, and the collapse in total runtime.
- Storage residency is meaningful at full data: one native-heavy helper is about `232 MB`.

## Table 2: Consumer Semantics

| workload | rows | cse | logical consumers | store reads | effective uses | helper usage pattern |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| native_heavy_probe | 1,000 | off | 0 | 0 | 0 | unread |
| native_heavy_probe | 1,000 | on | 1 | 2 | 2 | single_consumer_multi_read |
| native_heavy_nested | 1,000 | off | 0 | 0 | 0 | unread |
| native_heavy_nested | 1,000 | on | 1 | 2 | 2 | single_consumer_multi_read |
| native_heavy_multi_read | 1,000 | off | 0 | 0 | 0 | unread |
| native_heavy_multi_read | 1,000 | on | 1 | 2 | 2 | single_consumer_multi_read |
| native_heavy_probe | 1,000,000 | on | 1 | 2 | 2 | single_consumer_multi_read |
| native_heavy_nested | 1,000,000 | on | 1 | 2 | 2 | single_consumer_multi_read |
| native_heavy_multi_read | 1,000,000 | on | 1 | 2 | 2 | single_consumer_multi_read |
| native_heavy_multi_read | 29,048,679 | on | 1 | 2 | 2 | single_consumer_multi_read |

Interpretation:

- The CSE-on consumer shape is stable across smoke, 1M, and full data for the key workload.
- The important shape is not multiple logical consumers. It is one logical rewritten expression reading the helper multiple times.
- This confirms that L2 ref-count semantics cannot be copied directly onto native-heavy without a separate normalized-expression read model.

## Table 3: Blocker Distribution

| workload | rows | cse | eligibility | blocker | count |
| --- | ---: | --- | --- | --- | ---: |
| native_heavy_probe | 1,000 | off | forbidden | unresolved_fallback_path | 1 |
| native_heavy_probe | 1,000 | on | observable_only | unstable_consumer_semantics | 1 |
| native_heavy_nested | 1,000 | off | forbidden | unresolved_fallback_path | 1 |
| native_heavy_nested | 1,000 | on | observable_only | unstable_consumer_semantics | 1 |
| native_heavy_multi_read | 1,000 | off | forbidden | unresolved_fallback_path | 1 |
| native_heavy_multi_read | 1,000 | on | observable_only | unstable_consumer_semantics | 1 |
| native_heavy_probe | 1,000,000 | off | forbidden | unresolved_fallback_path | 1 |
| native_heavy_probe | 1,000,000 | on | observable_only | unstable_consumer_semantics | 1 |
| native_heavy_nested | 1,000,000 | off | forbidden | unresolved_fallback_path | 1 |
| native_heavy_nested | 1,000,000 | on | observable_only | unstable_consumer_semantics | 1 |
| native_heavy_multi_read | 1,000,000 | off | forbidden | unresolved_fallback_path | 1 |
| native_heavy_multi_read | 1,000,000 | on | observable_only | unstable_consumer_semantics | 1 |
| native_heavy_multi_read | 29,048,679 | off | forbidden | unresolved_fallback_path | 1 |
| native_heavy_multi_read | 29,048,679 | on | observable_only | unstable_consumer_semantics | 1 |

Interpretation:

- CSE off is structurally blocked by unresolved fallback path.
- CSE on consistently removes fallback and rewrites to helper usage, but remains blocked by consumer semantics.
- No observed native-heavy node reaches `candidate_future` under the current rules.

## Table 4: Future Candidate Review

| workload | rows | helper usage pattern | eligibility | blocker | candidate future? | reason |
| --- | ---: | --- | --- | --- | --- | --- |
| native_heavy_probe | 1,000,000 | single_consumer_multi_read | observable_only | unstable_consumer_semantics | no | clean rewrite, but native ref-count/read model not yet hardened |
| native_heavy_nested | 1,000,000 | single_consumer_multi_read | observable_only | unstable_consumer_semantics | no | rewrite works, but nested/non-native co-materialization makes this second priority |
| native_heavy_multi_read | 1,000,000 | single_consumer_multi_read | observable_only | unstable_consumer_semantics | no, but closest | stable pattern and 8 MB storage; needs normalized read lifecycle hardening |
| native_heavy_multi_read | 29,048,679 | single_consumer_multi_read | observable_only | unstable_consumer_semantics | no, but closest | stable pattern and 232 MB storage; enough value for further design, not active drop |

## Answers

### Q1: What Is The Main Gain?

Current native-heavy gain is mostly compute reduction plus path normalization.

Evidence:

- At 1M rows, `native_heavy_multi_read` improves from `4.652s` to `2.240s`.
- At full data, it improves from `130.283s` to `71.879s`.
- CSE on converts fallback occurrences from `1` to `0` and computes one native node-store value.
- Storage is valuable at full data (`232,389,432` bytes), but no storage benefit is realized yet because native-heavy active drop remains disabled.

### Q2: Can Consumer Semantics Be Stabilized?

Partially, but not enough for active drop.

The repeated CSE-on pattern is stable:

```text
logical_consumer_count = 1
node_store_read_count = 2
native_effective_use_count = 2
helper_usage_pattern = single_consumer_multi_read
```

That is explainable, but it is not the same model as L2. Native-heavy needs a normalized-expression read lifecycle before storage drop can be considered safe.

### Q3: Are Blockers Temporary Or Structural?

There are two groups:

- `unresolved_fallback_path`: structural blocker for CSE-off paths. Do not pursue lifecycle here.
- `unstable_consumer_semantics`: temporary/design blocker for CSE-on rewritten paths. This is the only path worth further design.

### Q4: Does A True Candidate Future Subset Exist?

Not yet under the current eligibility rules.

There is a plausible candidate-shaped subgroup:

```text
cse = true
native_rewrite_applied = true
native_fallback_eval_count = 0
helper_usage_pattern = single_consumer_multi_read
storage bytes are material at full data
```

But it remains `observable_only`, because consumer semantics are not yet hardened into a safe native-specific release model.

## Conclusion

Conclusion C: native-heavy is not a single lifecycle domain.

Subgroup A may be future candidate:

- CSE-on native-heavy
- fallback eliminated
- helper rewrite applied
- `single_consumer_multi_read`
- material storage residency at full scale

Subgroup B remains forbidden:

- CSE-off native-heavy
- unresolved fallback path
- unread helper pattern
- no safe storage lifecycle boundary

Next step should not be active drop. The only justified next step is native-heavy observability hardening around the normalized-expression read model:

- prove `single_consumer_multi_read` across higher fan-out
- define native-specific planned read multiplicity
- separate helper-read lifecycle from logical consumer lifecycle
- only then reconsider `candidate_future`

Native-heavy active lifecycle should not proceed yet.
