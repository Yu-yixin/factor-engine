# Stage Lifecycle Benchmark Report

- run_id: `a54c2310d0c04c61affcf345221b375b`
- benchmark: `demo_deep4_factors`
- dataset: `data/data_fe.parquet`
- rows: `500000`
- groups: `5470`
- expressions: `4`
- total_time_sec: `5.065625`
- peak_rss_mb: `1109.66`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a54c2310d0c04c61affcf345221b375b:batch:1` | `ordered_batch` | 4 | 1 | 1 | 14 | 1 | 0 | 9 | 0 | 4 | 0 | 1109.66 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a54c2310d0c04c61affcf345221b375b:batch:1` | 60 | 43 | 9 | 9 | 1 | 10 | 2 | 1 | 1 | 0 | 2 | 1 | 0.667 | 5.983 | 4993.428 | 5.731 | 0.296 | 6.028 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a54c2310d0c04c61affcf345221b375b:batch:1` | `first_wave` | True | 1 | 1 | 1 | 4000000 | 0 | 1 | 0 | `n27` | True | True | 50 | 4.000 | 4 | 3.000 | 3 | 16000000 | 1 |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `a54c2310d0c04c61affcf345221b375b:batch:1` | `off` | False | 1 | 1 | 0 | 4000000 | 4000000 | 4000000 | 0 | 0 | 14 | 14 | 0.000 | 16000000 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n27` | `a54c2310d0c04c61affcf345221b375b:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 4000000 | 4 | 16000000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `a54c2310d0c04c61affcf345221b375b:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `a54c2310d0c04c61affcf345221b375b:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `factor_deep_1` | `None` | 1 | 7 | 7 | False | False |
| `factor_deep_2` | `None` | 2 | 8 | 8 | False | False |
| `factor_deep_3` | `None` | 3 | 9 | 9 | False | False |
| `factor_deep_4` | `None` | 4 | 10 | 10 | False | False |
