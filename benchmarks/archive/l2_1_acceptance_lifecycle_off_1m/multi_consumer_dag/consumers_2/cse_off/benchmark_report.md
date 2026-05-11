# Stage Lifecycle Benchmark Report

- run_id: `33c17dc0e753480caef24d551dae4074`
- benchmark: `r4_multi_consumer_dag_2_cse_off`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `2`
- total_time_sec: `0.310155`
- peak_rss_mb: `602.66`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `33c17dc0e753480caef24d551dae4074:batch:1` | `ordered_batch` | 2 | 0 | 0 | 11 | 0 | 0 | 9 | 0 | 2 | 0 | 602.66 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `33c17dc0e753480caef24d551dae4074:batch:1` | 10 | 7 | 3 | 3 | 1 | 1 | 2 | 2 | 0 | 2 | 0 | 0 | 0.000 | 0.000 | 142.545 | 26.872 | 0.318 | 27.190 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `33c17dc0e753480caef24d551dae4074:batch:1` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 13 | 0.000 | 0 | 0.000 | 0 | 0 | 0 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `33c17dc0e753480caef24d551dae4074:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 3 | 3 | False | False |
| `consumer_02` | `None` | 2 | 4 | 4 | False | False |
