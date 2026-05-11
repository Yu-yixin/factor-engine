# Stage Lifecycle Benchmark Report

- run_id: `005c207f543640bfa0032bbda183c600`
- benchmark: `m2_5_reject_multi_child`
- dataset: `data.parquet`
- rows: `1000`
- groups: `1000`
- expressions: `1`
- total_time_sec: `0.022947`
- peak_rss_mb: `71.71`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `005c207f543640bfa0032bbda183c600:batch:1` | `ordered_batch` | 1 | 3 | 3 | 13 | 3 | 0 | 9 | 0 | 1 | 0 | 71.70 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `005c207f543640bfa0032bbda183c600:batch:1` | 23 | 8 | 5 | 5 | 3 | 3 | 8 | 3 | 3 | 0 | 6 | 4 | 0.667 | 3.970 | 0.499 | 0.644 | 0.097 | 0.741 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `005c207f543640bfa0032bbda183c600:batch:1` | `first_wave` | True | 3 | 3 | 3 | 24125 | 0 | 3 | 0 | `n3,n4,n6` | True | True | 13 | 5.000 | 7 | 4.000 | 6 | 120500 | 3 |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `005c207f543640bfa0032bbda183c600:batch:1` | `second_wave_nested` | False | 3 | 3 | 0 | 24125 | 24125 | 24125 | 0 | 0 | 13 | 13 | 0.000 | 96500 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `005c207f543640bfa0032bbda183c600:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000 | 7 | 56000 |
| `n6` | `005c207f543640bfa0032bbda183c600:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8125 | 4 | 32500 |
| `n4` | `005c207f543640bfa0032bbda183c600:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000 | 4 | 32000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `005c207f543640bfa0032bbda183c600:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |
| `005c207f543640bfa0032bbda183c600:batch:1:stage:2` | `dag_shared_intermediate` | `___dag_node` | 0 | False | True |
| `005c207f543640bfa0032bbda183c600:batch:1:stage:3` | `dag_shared_intermediate` | `____dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `005c207f543640bfa0032bbda183c600:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `multi_child` | `None` | 1 | 8 | 8 | False | False |
