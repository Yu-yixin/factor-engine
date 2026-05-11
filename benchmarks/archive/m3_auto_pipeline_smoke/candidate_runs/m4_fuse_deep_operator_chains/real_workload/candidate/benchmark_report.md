# Stage Lifecycle Benchmark Report

- run_id: `1e715ae50bd54a76be8a7e5d516c04e1`
- benchmark: `m3_m4_fuse_deep_operator_chains_real_workload`
- dataset: `dataframe`
- rows: `1000`
- groups: `1000`
- expressions: `3`
- total_time_sec: `0.016355`
- peak_rss_mb: `70.07`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `1e715ae50bd54a76be8a7e5d516c04e1:batch:1` | `ordered_batch` | 3 | 1 | 1 | 13 | 1 | 0 | 9 | 0 | 3 | 0 | 70.06 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `1e715ae50bd54a76be8a7e5d516c04e1:batch:1` | 15 | 10 | 3 | 3 | 1 | 2 | 2 | 1 | 1 | 0 | 2 | 2 | 0.667 | 0.980 | 0.883 | 0.631 | 0.208 | 0.840 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `1e715ae50bd54a76be8a7e5d516c04e1:batch:1` | `first_wave` | True | 1 | 1 | 1 | 8000 | 0 | 1 | 0 | `n3` | True | True | 16 | 4.000 | 4 | 3.000 | 3 | 32000 | 1 |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `1e715ae50bd54a76be8a7e5d516c04e1:batch:1` | `second_wave_nested` | False | 1 | 1 | 0 | 8000 | 8000 | 8000 | 0 | 0 | 13 | 13 | 0.000 | 32000 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `1e715ae50bd54a76be8a7e5d516c04e1:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000 | 4 | 32000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `1e715ae50bd54a76be8a7e5d516c04e1:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `1e715ae50bd54a76be8a7e5d516c04e1:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `a` | `None` | 1 | 6 | 6 | False | False |
| `b` | `None` | 2 | 7 | 7 | False | False |
| `c` | `None` | 3 | 8 | 8 | False | False |
