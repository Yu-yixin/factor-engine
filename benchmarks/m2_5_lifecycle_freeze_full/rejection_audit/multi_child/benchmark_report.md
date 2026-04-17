# Stage Lifecycle Benchmark Report

- run_id: `c276a67dd23a4fdeaafbb8ea86daeea8`
- benchmark: `m2_5_reject_multi_child`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `20.587682`
- peak_rss_mb: `21301.16`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `c276a67dd23a4fdeaafbb8ea86daeea8:batch:1` | `ordered_batch` | 1 | 3 | 3 | 13 | 3 | 0 | 9 | 0 | 1 | 0 | 21257.67 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `c276a67dd23a4fdeaafbb8ea86daeea8:batch:1` | 23 | 8 | 5 | 5 | 3 | 3 | 8 | 3 | 3 | 0 | 6 | 4 | 0.667 | 5803.534 | 85.658 | 1556.048 | 1.594 | 1557.641 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `c276a67dd23a4fdeaafbb8ea86daeea8:batch:1` | `first_wave` | True | 3 | 3 | 3 | 700799381 | 0 | 3 | 0 | `n3,n4,n6` | True | True | 13 | 5.000 | 7 | 4.000 | 6 | 3500365820 | 3 |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `c276a67dd23a4fdeaafbb8ea86daeea8:batch:1` | `second_wave_nested` | False | 3 | 3 | 0 | 700799381 | 700799381 | 700799381 | 0 | 0 | 13 | 13 | 0.000 | 2803197524 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `c276a67dd23a4fdeaafbb8ea86daeea8:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 7 | 1626726024 |
| `n6` | `c276a67dd23a4fdeaafbb8ea86daeea8:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 236020517 | 4 | 944082068 |
| `n4` | `c276a67dd23a4fdeaafbb8ea86daeea8:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 4 | 929557728 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `c276a67dd23a4fdeaafbb8ea86daeea8:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |
| `c276a67dd23a4fdeaafbb8ea86daeea8:batch:1:stage:2` | `dag_shared_intermediate` | `___dag_node` | 0 | False | True |
| `c276a67dd23a4fdeaafbb8ea86daeea8:batch:1:stage:3` | `dag_shared_intermediate` | `____dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `c276a67dd23a4fdeaafbb8ea86daeea8:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `multi_child` | `None` | 1 | 8 | 8 | False | False |
