# Stage Lifecycle Benchmark Report

- run_id: `b3c4be2274eb41a98edf0e6408535f18`
- benchmark: `r4_multi_consumer_dag_8_cse_off`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `8`
- total_time_sec: `24.388996`
- peak_rss_mb: `19617.81`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `b3c4be2274eb41a98edf0e6408535f18:batch:1` | `ordered_batch` | 8 | 0 | 0 | 17 | 0 | 0 | 9 | 0 | 8 | 0 | 19617.81 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `b3c4be2274eb41a98edf0e6408535f18:batch:1` | 40 | 19 | 3 | 3 | 1 | 1 | 8 | 8 | 0 | 8 | 0 | 0 | 0.000 | 0.000 | 15678.904 | 1120.912 | 0.340 | 1121.252 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `b3c4be2274eb41a98edf0e6408535f18:batch:1` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 31 | 0.000 | 0 | 0.000 | 0 | 0 | 0 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `b3c4be2274eb41a98edf0e6408535f18:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 9 | 9 | False | False |
| `consumer_02` | `None` | 2 | 10 | 10 | False | False |
| `consumer_03` | `None` | 3 | 11 | 11 | False | False |
| `consumer_04` | `None` | 4 | 12 | 12 | False | False |
| `consumer_05` | `None` | 5 | 13 | 13 | False | False |
| `consumer_06` | `None` | 6 | 14 | 14 | False | False |
| `consumer_07` | `None` | 7 | 15 | 15 | False | False |
| `consumer_08` | `None` | 8 | 16 | 16 | False | False |
