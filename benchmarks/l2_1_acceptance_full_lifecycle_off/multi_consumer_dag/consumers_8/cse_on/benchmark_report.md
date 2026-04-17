# Stage Lifecycle Benchmark Report

- run_id: `fcd540d344c341dd9ac02a9b03460051`
- benchmark: `r4_multi_consumer_dag_8_cse_on`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `8`
- total_time_sec: `13.992550`
- peak_rss_mb: `19806.42`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fcd540d344c341dd9ac02a9b03460051:batch:1` | `ordered_batch` | 8 | 1 | 0 | 18 | 1 | 0 | 10 | 1 | 8 | 0 | 19806.41 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fcd540d344c341dd9ac02a9b03460051:batch:1` | 40 | 19 | 3 | 3 | 1 | 1 | 8 | 1 | 1 | 0 | 8 | 8 | 0.889 | 2196.879 | 170.305 | 1431.014 | 0.463 | 1431.478 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fcd540d344c341dd9ac02a9b03460051:batch:1` | 1 | 1 | 1 | 232389432 | 232389432 | 0 | 0 | 31 | 4.000 | 4 | 3.000 | 3 | 929557728 | 1 |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `fcd540d344c341dd9ac02a9b03460051:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 4 | 929557728 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `fcd540d344c341dd9ac02a9b03460051:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `fcd540d344c341dd9ac02a9b03460051:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 10 | 10 | False | False |
| `consumer_02` | `None` | 2 | 11 | 11 | False | False |
| `consumer_03` | `None` | 3 | 12 | 12 | False | False |
| `consumer_04` | `None` | 4 | 13 | 13 | False | False |
| `consumer_05` | `None` | 5 | 14 | 14 | False | False |
| `consumer_06` | `None` | 6 | 15 | 15 | False | False |
| `consumer_07` | `None` | 7 | 16 | 16 | False | False |
| `consumer_08` | `None` | 8 | 17 | 17 | False | False |
