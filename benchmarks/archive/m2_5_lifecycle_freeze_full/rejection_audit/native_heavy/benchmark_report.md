# Stage Lifecycle Benchmark Report

- run_id: `5e4a25bd75bd4b6da5eda3593b622264`
- benchmark: `m2_5_reject_native_heavy`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `75.969084`
- peak_rss_mb: `21370.54`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `5e4a25bd75bd4b6da5eda3593b622264:batch:1` | `ordered_batch` | 1 | 1 | 1 | 11 | 1 | 0 | 9 | 0 | 1 | 0 | 21370.54 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `5e4a25bd75bd4b6da5eda3593b622264:batch:1` | 7 | 4 | 3 | 3 | 1 | 1 | 2 | 1 | 1 | 0 | 2 | 1 | 0.667 | 67226.293 | 35.452 | 565.723 | 0.120 | 565.843 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `5e4a25bd75bd4b6da5eda3593b622264:batch:1` | `first_wave` | False | 1 | 1 | 1 | 232389432 | 232389432 | 0 | 0 | `` | True | True | 9 | 4.000 | 4 | 3.000 | 3 | 929557728 | 0 |

## L3A Native-Heavy Lifecycle Observability

| batch | native nodes | forbidden | observable only | candidate future | native compute ms | path normalization ms | storage bytes | store reads | logical consumers | effective uses | fallback evals | rewrites | helper patterns |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `5e4a25bd75bd4b6da5eda3593b622264:batch:1` | 1 | 0 | 1 | 0 | 67226.293 | 0.000 | 232389432 | 2 | 1 | 2 | 0 | 1 | `single_consumer_multi_read` |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `5e4a25bd75bd4b6da5eda3593b622264:batch:1` | `second_wave_nested` | False | 1 | 1 | 0 | 232389432 | 232389432 | 232389432 | 0 | 0 | 11 | 11 | 0.000 | 929557728 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `5e4a25bd75bd4b6da5eda3593b622264:batch:1` | `native_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 4 | 929557728 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `5e4a25bd75bd4b6da5eda3593b622264:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `5e4a25bd75bd4b6da5eda3593b622264:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `native_heavy` | `None` | 1 | 4 | 4 | False | False |
