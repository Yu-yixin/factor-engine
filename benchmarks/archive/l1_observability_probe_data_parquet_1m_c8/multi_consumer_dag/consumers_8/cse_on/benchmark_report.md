# Stage Lifecycle Benchmark Report

- run_id: `bb1e358ef802491586bd7e34390f1a7b`
- benchmark: `r4_multi_consumer_dag_8_cse_on`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `8`
- total_time_sec: `0.240777`
- peak_rss_mb: `594.36`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `bb1e358ef802491586bd7e34390f1a7b:batch:1` | `ordered_batch` | 8 | 1 | 0 | 18 | 1 | 0 | 10 | 1 | 8 | 0 | 483.84 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `bb1e358ef802491586bd7e34390f1a7b:batch:1` | 40 | 19 | 3 | 3 | 1 | 1 | 8 | 1 | 1 | 0 | 8 | 8 | 0.889 | 62.823 | 7.408 | 28.836 | 0.223 | 29.059 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | peak live bytes est | avg lag steps | max lag steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `bb1e358ef802491586bd7e34390f1a7b:batch:1` | 1 | 1 | 1 | 8000000 | 0.000 | 0 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `bb1e358ef802491586bd7e34390f1a7b:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `bb1e358ef802491586bd7e34390f1a7b:batch:1` | 0 | 0 | 0 | 0 |

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
