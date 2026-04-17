# L3B.1 Helper / Working-Frame Lifecycle Acceptance

L3B.1 is an acceptance and probe stage. It does not delete DataFrame columns, does not change executor order, does not add active helper-drop mode, and does not include native-heavy in active helper lifecycle.

## Probe Scope

Commands run:

```text
examples/benchmark_r4_executor_reuse.py --rows 1000000 --consumer-counts 2 --workloads repeated_heavy,multi_shared_nodes,nested_dag,partial_reuse --lifecycle-mode off
examples/benchmark_r4_executor_reuse.py --rows 1000000 --consumer-counts 2 --workloads repeated_heavy,multi_shared_nodes,nested_dag,partial_reuse --lifecycle-mode first_wave
examples/benchmark_r4_executor_reuse.py --rows 0 --consumer-counts 2 --workloads repeated_heavy,multi_shared_nodes,nested_dag,partial_reuse --lifecycle-mode first_wave
```

Artifacts:

- `benchmarks/l3b1_helper_1m_off`
- `benchmarks/l3b1_helper_1m_first_wave`
- `benchmarks/l3b1_helper_full_first_wave`

## Table 1: Helper Lifecycle Summary

| workload | rows | mode | helper columns | releasable | blocked | helper live bytes | helper bytes-step |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| repeated_heavy | 1,000,000 | off | 1 | 1 | 0 | 8,000,000 | 32,000,000 |
| multi_shared_nodes | 1,000,000 | off | 2 | 2 | 0 | 16,000,000 | 64,000,000 |
| nested_dag | 1,000,000 | off | 2 | 2 | 0 | 16,000,000 | 80,000,000 |
| partial_reuse | 1,000,000 | off | 1 | 1 | 0 | 8,000,000 | 32,000,000 |
| repeated_heavy | 1,000,000 | first_wave | 1 | 1 | 0 | 8,000,000 | 32,000,000 |
| multi_shared_nodes | 1,000,000 | first_wave | 2 | 2 | 0 | 16,000,000 | 64,000,000 |
| nested_dag | 1,000,000 | first_wave | 2 | 2 | 0 | 16,000,000 | 80,000,000 |
| partial_reuse | 1,000,000 | first_wave | 1 | 1 | 0 | 8,000,000 | 32,000,000 |
| repeated_heavy | 29,048,679 | first_wave | 1 | 1 | 0 | 232,389,432 | 929,557,728 |
| multi_shared_nodes | 29,048,679 | first_wave | 2 | 2 | 0 | 464,778,864 | 1,859,115,456 |
| nested_dag | 29,048,679 | first_wave | 2 | 2 | 0 | 464,778,864 | 2,323,894,320 |
| partial_reuse | 29,048,679 | first_wave | 1 | 1 | 0 | 232,389,432 | 929,557,728 |

Interpretation:

- Every CSE-on helper in the tested non-native workloads is `logically_dead`, blocker-free, and retained until batch end.
- The pattern is stable from 1M rows to full data.
- Full-data helper bytes are significant: about `232 MB` per helper column.

## Table 2: Helper Blocker Breakdown

| workload | rows | mode | blocker reason | count | bytes | bytes-step |
| --- | ---: | --- | --- | ---: | ---: | ---: |
| repeated_heavy | 1,000,000 | first_wave | none | 0 | 0 | 0 |
| multi_shared_nodes | 1,000,000 | first_wave | none | 0 | 0 | 0 |
| nested_dag | 1,000,000 | first_wave | none | 0 | 0 | 0 |
| partial_reuse | 1,000,000 | first_wave | none | 0 | 0 | 0 |
| repeated_heavy | 29,048,679 | first_wave | none | 0 | 0 | 0 |
| multi_shared_nodes | 29,048,679 | first_wave | none | 0 | 0 | 0 |
| nested_dag | 29,048,679 | first_wave | none | 0 | 0 | 0 |
| partial_reuse | 29,048,679 | first_wave | none | 0 | 0 | 0 |

Interpretation:

- `final_output_dependency`, `rewrite_alias_dependency`, and `execution_order_uncertain` did not appear in the CSE-on helper candidate set for these workloads.
- This does not prove all helper classes are safe. It proves the tested shared non-native DAG helper class has a clean blocker profile.

## Table 3: Store-vs-Helper Gap

| workload | rows | node-store after drop | helper after batch | helper structural lag | interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| repeated_heavy | 1,000,000 | 0 | 8,000,000 | 4 | L2 store drop succeeds, frame helper remains |
| multi_shared_nodes | 1,000,000 | 0 | 16,000,000 | 4 | multiple helpers remain after store drop |
| nested_dag | 1,000,000 | 0 | 16,000,000 | 5 | nested helpers remain, longer lag |
| partial_reuse | 1,000,000 | 0 | 8,000,000 | 4 | partial reuse helper remains |
| repeated_heavy | 29,048,679 | 0 | 232,389,432 | 4 | full-data single helper gap is material |
| multi_shared_nodes | 29,048,679 | 0 | 464,778,864 | 4 | full-data multi-helper gap is material |
| nested_dag | 29,048,679 | 0 | 464,778,864 | 5 | full-data nested gap is largest by bytes-step |
| partial_reuse | 29,048,679 | 0 | 232,389,432 | 4 | full-data partial gap remains clean |

Interpretation:

- L2 and L3B boundaries are clean: node-store entries drop to zero, while working-frame helper columns remain retained.
- The “错位窗口” is meaningful at full-data scale.

## Answers

### Q1: Which Workloads Have High-Value White-Retained Helpers?

All four tested CSE-on non-native helper workloads have high-value retained helpers at full-data scale:

- `repeated_heavy`: `232,389,432` helper bytes, `929,557,728` bytes-step.
- `multi_shared_nodes`: `464,778,864` helper bytes, `1,859,115,456` bytes-step.
- `nested_dag`: `464,778,864` helper bytes, `2,323,894,320` bytes-step.
- `partial_reuse`: `232,389,432` helper bytes, `929,557,728` bytes-step.

`nested_dag` has the highest bytes-step because helper lag is `5` instead of `4`.

### Q2: Is Blocker Distribution Stable?

For the tested shared non-native DAG helper class, blockers are absent:

```text
helper_blocked_count = 0
helper_blocker_reasons = []
```

This is stable at 1M and full-data scale.

### Q3: Is Helper Last Use Stable In Complex DAGs?

Yes for the tested set.

- `repeated_heavy`: 1 helper, lag 4.
- `multi_shared_nodes`: 2 helpers, lag 4.
- `nested_dag`: 2 helpers, lag 5.
- `partial_reuse`: 1 helper, lag 4.

The nested workload does not introduce blockers; it only increases the observed lag.

### Q4: Is The L2 Store-vs-Helper Gap Worth Continuing?

Yes.

With `lifecycle_mode=first_wave`, node-store after-drop reaches `0`, but helper columns remain:

```text
full-data helper_after_batch:
232 MB to 465 MB depending on workload
```

That is large enough to justify L3B.2 implementation design, while still not justifying immediate deletion without a design phase.

## Conclusion

Conclusion A: a future candidate helper subgroup exists.

Candidate subgroup:

```text
shared non-native DAG helper columns
materialized by DAG/CSE
helper_lifecycle_state = logically_dead
helper_drop_blocker_reason = ""
helper_structural_lag_steps > 0
stable at 1M and full-data scale
meaningful full-data bytes and bytes-step savings
```

Representative workloads:

- `repeated_heavy`
- `multi_shared_nodes`
- `nested_dag`
- `partial_reuse`

Next step:

```text
L3B.2 helper lifecycle implementation design
```

This next step should still be design first. It should not immediately delete columns.

## Non-Goals Preserved

This review did not:

- delete DataFrame columns
- change final output assembly
- add active helper-drop mode
- change native-heavy lifecycle status
- merge helper lifecycle into L2 node-store lifecycle
