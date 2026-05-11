# Stage Lifecycle Benchmark Report

- run_id: `069e9e484a774e1bbc750e610220f469`
- benchmark: `r4_native_heavy_multi_read_2_cse_on`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `71.879247`
- peak_rss_mb: `19142.27`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `069e9e484a774e1bbc750e610220f469:batch:1` | `ordered_batch` | 1 | 1 | 0 | 11 | 1 | 0 | 10 | 1 | 1 | 0 | 19142.25 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `069e9e484a774e1bbc750e610220f469:batch:1` | 7 | 4 | 3 | 3 | 1 | 1 | 2 | 1 | 1 | 0 | 2 | 1 | 0.667 | 63726.643 | 33.865 | 316.505 | 0.104 | 316.609 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `069e9e484a774e1bbc750e610220f469:batch:1` | `off` | False | 1 | 1 | 1 | 232389432 | 232389432 | 0 | 0 | `` | True | True | 9 | 4.000 | 4 | 3.000 | 3 | 929557728 | 0 |

## L3A Native-Heavy Lifecycle Observability

| batch | native nodes | forbidden | observable only | candidate future | native compute ms | path normalization ms | storage bytes | store reads | logical consumers | effective uses | fallback evals | rewrites | helper patterns |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `069e9e484a774e1bbc750e610220f469:batch:1` | 1 | 0 | 1 | 0 | 63726.643 | 0.000 | 232389432 | 2 | 1 | 2 | 0 | 1 | `single_consumer_multi_read` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `069e9e484a774e1bbc750e610220f469:batch:1` | `native_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 4 | 929557728 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `069e9e484a774e1bbc750e610220f469:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `069e9e484a774e1bbc750e610220f469:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `native_heavy_multi_read` | `None` | 1 | 3 | 3 | False | False |
