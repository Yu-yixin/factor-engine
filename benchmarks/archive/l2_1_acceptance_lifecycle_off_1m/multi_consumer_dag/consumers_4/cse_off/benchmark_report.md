# Stage Lifecycle Benchmark Report

- run_id: `fc2fa04af938409c8028c792a3467688`
- benchmark: `r4_multi_consumer_dag_4_cse_off`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `4`
- total_time_sec: `0.320838`
- peak_rss_mb: `641.00`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fc2fa04af938409c8028c792a3467688:batch:1` | `ordered_batch` | 4 | 0 | 0 | 13 | 0 | 0 | 9 | 0 | 4 | 0 | 641.00 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fc2fa04af938409c8028c792a3467688:batch:1` | 20 | 11 | 3 | 3 | 1 | 1 | 4 | 4 | 0 | 4 | 0 | 0 | 0.000 | 0.000 | 175.181 | 22.333 | 0.235 | 22.568 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fc2fa04af938409c8028c792a3467688:batch:1` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 19 | 0.000 | 0 | 0.000 | 0 | 0 | 0 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `fc2fa04af938409c8028c792a3467688:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 5 | 5 | False | False |
| `consumer_02` | `None` | 2 | 6 | 6 | False | False |
| `consumer_03` | `None` | 3 | 7 | 7 | False | False |
| `consumer_04` | `None` | 4 | 8 | 8 | False | False |
