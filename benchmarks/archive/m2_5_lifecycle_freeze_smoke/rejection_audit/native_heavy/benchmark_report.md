# Stage Lifecycle Benchmark Report

- run_id: `8109fd061464480a88c784a738b6d0cd`
- benchmark: `m2_5_reject_native_heavy`
- dataset: `data.parquet`
- rows: `1000`
- groups: `1000`
- expressions: `1`
- total_time_sec: `0.015384`
- peak_rss_mb: `71.45`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `8109fd061464480a88c784a738b6d0cd:batch:1` | `ordered_batch` | 1 | 1 | 1 | 11 | 1 | 0 | 9 | 0 | 1 | 0 | 71.45 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `8109fd061464480a88c784a738b6d0cd:batch:1` | 7 | 4 | 3 | 3 | 1 | 1 | 2 | 1 | 1 | 0 | 2 | 1 | 0.667 | 4.821 | 0.244 | 0.738 | 0.082 | 0.820 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `8109fd061464480a88c784a738b6d0cd:batch:1` | `first_wave` | False | 1 | 1 | 1 | 8000 | 8000 | 0 | 0 | `` | True | True | 9 | 4.000 | 4 | 3.000 | 3 | 32000 | 0 |

## L3A Native-Heavy Lifecycle Observability

| batch | native nodes | forbidden | observable only | candidate future | native compute ms | path normalization ms | storage bytes | store reads | logical consumers | effective uses | fallback evals | rewrites | helper patterns |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `8109fd061464480a88c784a738b6d0cd:batch:1` | 1 | 0 | 1 | 0 | 4.821 | 0.000 | 8000 | 2 | 1 | 2 | 0 | 1 | `single_consumer_multi_read` |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `8109fd061464480a88c784a738b6d0cd:batch:1` | `second_wave_nested` | False | 1 | 1 | 0 | 8000 | 8000 | 8000 | 0 | 0 | 11 | 11 | 0.000 | 32000 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `8109fd061464480a88c784a738b6d0cd:batch:1` | `native_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000 | 4 | 32000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `8109fd061464480a88c784a738b6d0cd:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `8109fd061464480a88c784a738b6d0cd:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `native_heavy` | `None` | 1 | 4 | 4 | False | False |
