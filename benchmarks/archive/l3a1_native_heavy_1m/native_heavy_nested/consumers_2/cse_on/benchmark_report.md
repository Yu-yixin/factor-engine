# Stage Lifecycle Benchmark Report

- run_id: `634ddba1ab6c4c3ab1133ed556459c91`
- benchmark: `r4_native_heavy_nested_2_cse_on`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `2.591859`
- peak_rss_mb: `720.99`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `634ddba1ab6c4c3ab1133ed556459c91:batch:1` | `ordered_batch` | 1 | 2 | 0 | 12 | 2 | 0 | 11 | 2 | 1 | 0 | 682.40 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `634ddba1ab6c4c3ab1133ed556459c91:batch:1` | 11 | 5 | 4 | 4 | 2 | 2 | 4 | 2 | 2 | 0 | 3 | 2 | 0.600 | 2408.778 | 3.354 | 20.778 | 0.134 | 20.912 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `634ddba1ab6c4c3ab1133ed556459c91:batch:1` | `off` | False | 2 | 2 | 2 | 16000000 | 16000000 | 0 | 0 | `` | True | True | 10 | 5.000 | 6 | 4.000 | 5 | 80000000 | 1 |

## L3A Native-Heavy Lifecycle Observability

| batch | native nodes | forbidden | observable only | candidate future | native compute ms | path normalization ms | storage bytes | store reads | logical consumers | effective uses | fallback evals | rewrites | helper patterns |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `634ddba1ab6c4c3ab1133ed556459c91:batch:1` | 1 | 0 | 1 | 0 | 2378.887 | 0.000 | 8000000 | 2 | 1 | 2 | 0 | 1 | `single_consumer_multi_read` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `634ddba1ab6c4c3ab1133ed556459c91:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000000 | 6 | 48000000 |
| `n4` | `634ddba1ab6c4c3ab1133ed556459c91:batch:1` | `native_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000000 | 4 | 32000000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `634ddba1ab6c4c3ab1133ed556459c91:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |
| `634ddba1ab6c4c3ab1133ed556459c91:batch:1:stage:2` | `dag_shared_intermediate` | `___dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `634ddba1ab6c4c3ab1133ed556459c91:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `native_heavy_nested` | `None` | 1 | 4 | 4 | False | False |
