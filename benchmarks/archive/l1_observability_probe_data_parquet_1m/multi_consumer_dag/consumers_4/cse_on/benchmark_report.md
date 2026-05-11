# Stage Lifecycle Benchmark Report

- run_id: `9906ba84c8b04c64a1a82193a6acdc0b`
- benchmark: `r4_multi_consumer_dag_4_cse_on`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `4`
- total_time_sec: `0.226736`
- peak_rss_mb: `632.30`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `9906ba84c8b04c64a1a82193a6acdc0b:batch:1` | `ordered_batch` | 4 | 1 | 0 | 14 | 1 | 0 | 10 | 1 | 4 | 0 | 595.21 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `9906ba84c8b04c64a1a82193a6acdc0b:batch:1` | 20 | 11 | 3 | 3 | 1 | 1 | 4 | 1 | 1 | 0 | 4 | 4 | 0.800 | 51.583 | 7.041 | 21.695 | 0.314 | 22.009 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | peak live bytes est | avg lag steps | max lag steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `9906ba84c8b04c64a1a82193a6acdc0b:batch:1` | 1 | 1 | 1 | 8000000 | 0.000 | 0 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `9906ba84c8b04c64a1a82193a6acdc0b:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `9906ba84c8b04c64a1a82193a6acdc0b:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 6 | 6 | False | False |
| `consumer_02` | `None` | 2 | 7 | 7 | False | False |
| `consumer_03` | `None` | 3 | 8 | 8 | False | False |
| `consumer_04` | `None` | 4 | 9 | 9 | False | False |
