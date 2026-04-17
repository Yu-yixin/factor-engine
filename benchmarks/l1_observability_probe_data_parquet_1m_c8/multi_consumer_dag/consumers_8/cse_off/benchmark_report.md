# Stage Lifecycle Benchmark Report

- run_id: `dea28798dfd1484890e321613765e937`
- benchmark: `r4_multi_consumer_dag_8_cse_off`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `8`
- total_time_sec: `0.695647`
- peak_rss_mb: `537.42`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `dea28798dfd1484890e321613765e937:batch:1` | `ordered_batch` | 8 | 0 | 0 | 17 | 0 | 0 | 9 | 0 | 8 | 0 | 537.42 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `dea28798dfd1484890e321613765e937:batch:1` | 40 | 19 | 3 | 3 | 1 | 1 | 8 | 8 | 0 | 8 | 0 | 0 | 0.000 | 0.000 | 561.228 | 23.025 | 0.195 | 23.220 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | peak live bytes est | avg lag steps | max lag steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `dea28798dfd1484890e321613765e937:batch:1` | 1 | 0 | 0 | 0 | 0.000 | 0 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `dea28798dfd1484890e321613765e937:batch:1` | 0 | 0 | 0 | 0 |

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
