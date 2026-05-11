# Stage Lifecycle Benchmark Report

- run_id: `d9e53b3ed7bd4340a7a05950d3ed5925`
- benchmark: `r4_multi_consumer_dag_2_cse_off`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `2`
- total_time_sec: `0.330278`
- peak_rss_mb: `538.38`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d9e53b3ed7bd4340a7a05950d3ed5925:batch:1` | `ordered_batch` | 2 | 0 | 0 | 11 | 0 | 0 | 9 | 0 | 2 | 0 | 538.38 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d9e53b3ed7bd4340a7a05950d3ed5925:batch:1` | 10 | 7 | 3 | 3 | 1 | 1 | 2 | 2 | 0 | 2 | 0 | 0 | 0.000 | 0.000 | 160.269 | 26.041 | 0.197 | 26.238 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | peak live bytes est | avg lag steps | max lag steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `d9e53b3ed7bd4340a7a05950d3ed5925:batch:1` | 1 | 0 | 0 | 0 | 0.000 | 0 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `d9e53b3ed7bd4340a7a05950d3ed5925:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 3 | 3 | False | False |
| `consumer_02` | `None` | 2 | 4 | 4 | False | False |
