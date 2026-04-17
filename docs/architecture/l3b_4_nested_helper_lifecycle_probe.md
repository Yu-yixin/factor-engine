# L3B.4 Nested Helper Lifecycle Probe

L3B.4 is a probe and classification stage. It does not delete nested helper columns, does not change the first-wave allowlist, does not enable nested helper active drop, does not touch native-heavy, and does not change the executor main path.

The question for this stage:

```text
Can nested_dag enter second-wave helper active-drop design?
```

## Probe Patterns

Pattern A:

```text
ts_rank(ts_rank(close, 10), 10) + ts_rank(ts_rank(close, 10), 10)
```

Pattern B:

```text
ts_rank(ts_mean(close, 10), 10) + ts_rank(ts_mean(close, 10), 10)
```

Pattern C:

```text
ts_rank(ts_mean(close, 10), 10) + ts_std(ts_mean(close, 10), 10)
```

Pattern A was run at smoke, 1M rows, and full-data scale. Pattern B was run at 1M rows. Pattern C was run at 1M rows and full-data scale.

Artifacts:

- `benchmarks/l3b4_nested_probe_a_smoke`
- `benchmarks/l3b4_nested_probe_a_1m`
- `benchmarks/l3b4_nested_probe_b_1m`
- `benchmarks/l3b4_nested_probe_c_1m`
- `benchmarks/l3b4_nested_probe_a_full`
- `benchmarks/l3b4_nested_probe_c_full`

## Table 1: Nested Helper Lifecycle

| workload | rows | helper | depth | parent | children | logical last use | structural dependency end | safe step | bytes | blocker |
| --- | ---: | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| nested_probe_a | 1,000 | `__dag_node` | 1 | `___dag_node` | `` | 4 | 4 | 7 | 8,000 | `` |
| nested_probe_a | 1,000 | `___dag_node` | 2 | `` | `__dag_node` | 6 | 6 | 7 | 8,000 | `` |
| nested_probe_a | 1,000,000 | `__dag_node` | 1 | `___dag_node` | `` | 4 | 4 | 7 | 8,000,000 | `` |
| nested_probe_a | 1,000,000 | `___dag_node` | 2 | `` | `__dag_node` | 6 | 6 | 7 | 8,000,000 | `` |
| nested_probe_b | 1,000,000 | `__dag_node` | 1 | `___dag_node` | `` | 4 | 4 | 7 | 8,000,000 | `` |
| nested_probe_b | 1,000,000 | `___dag_node` | 2 | `` | `__dag_node` | 6 | 6 | 7 | 8,000,000 | `` |
| nested_probe_c | 1,000,000 | `__dag_node` | 1 | `` | `` | 7 | 7 | 8 | 8,000,000 | `` |
| nested_probe_a | 29,048,679 | `__dag_node` | 1 | `___dag_node` | `` | 4 | 4 | 7 | 232,389,432 | `` |
| nested_probe_a | 29,048,679 | `___dag_node` | 2 | `` | `__dag_node` | 6 | 6 | 7 | 232,389,432 | `` |
| nested_probe_c | 29,048,679 | `__dag_node` | 1 | `` | `` | 7 | 7 | 8 | 232,389,432 | `` |

Interpretation:

- Pattern A and B produce a stable two-helper nested chain: inner helper -> outer helper.
- Pattern C produces a stable shared-inner-only helper: the two outer consumers remain physical consumers rather than materialized helper columns.
- No probe produced `helper_drop_safe_step < helper_structural_dependency_end_step`.
- No nested helper was actively dropped. `helper_dropped_count = 0` throughout this probe.

## Table 2: Nested Blocker Breakdown

| workload | rows | blocker reason | count | bytes |
| --- | ---: | --- | ---: | ---: |
| nested_probe_a | 1,000 | none | 0 | 0 |
| nested_probe_a | 1,000,000 | none | 0 | 0 |
| nested_probe_b | 1,000,000 | none | 0 | 0 |
| nested_probe_c | 1,000,000 | none | 0 | 0 |
| nested_probe_a | 29,048,679 | none | 0 | 0 |
| nested_probe_c | 29,048,679 | none | 0 | 0 |

Interpretation:

- `parent_helper_dependency` did not appear as a blocker in these probes.
- `nested_execution_order_uncertain` did not appear as a blocker in these probes.
- Blocker distribution is stable between 1M and full-data for Pattern A and Pattern C.

## Table 3: Nested Candidate Table

| workload | pattern | clean subset? | blocker | wave2 possible? | reason |
| --- | --- | --- | --- | --- | --- |
| nested_probe_a | `f(f(x)) + f(f(x))` | yes | none | yes | inner/outer helper chain is stable, safe step is after structural dependency end, full-data bytes are material |
| nested_probe_b | `f(g(x)) + f(g(x))` | yes | none | yes, after full-data confirmation | 1M chain matches Pattern A; full-data was not required because Pattern A already covers the full-data chain shape |
| nested_probe_c | `f(g(x)) + h(g(x))` | yes | none | yes | shared-inner-only helper has stable structural end and full-data bytes are material |

## Gate Review

Pass signals:

- At least one nested pattern is blocker-free.
- Safe-step ordering is stable.
- Inner/outer ordering is explainable for Pattern A/B.
- 1M and full-data agree for Pattern A and Pattern C.
- Full-data bytes and bytes-step are material:
  - Pattern A full-data helper bytes: `464,778,864`
  - Pattern A full-data bytes-step: `2,323,894,320`
  - Pattern C full-data helper bytes: `232,389,432`
  - Pattern C full-data bytes-step: `929,557,728`

Non-goals preserved:

- no nested helper column was deleted
- no first-wave allowlist expansion was made
- no native-heavy helper was touched

## Conclusion

Conclusion A:

```text
A stable nested helper subgroup exists and may enter second-wave helper active drop design.
```

The second-wave design should split nested helpers into at least two subgroups:

- nested chain helpers: Pattern A/B style inner -> outer helper
- shared-inner-only helpers: Pattern C style one helper consumed by multiple non-materialized outer expressions

This is a design-entry conclusion only. It does not authorize active nested helper drop yet.
