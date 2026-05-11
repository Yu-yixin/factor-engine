# Stage Lifecycle Benchmark Report

- run_id: `e02ac24fdfde4a19bc666bf8ba5e80f3`
- benchmark: `r4_repeated_heavy_8_cse_on`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `0.174878`
- peak_rss_mb: `513.39`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `e02ac24fdfde4a19bc666bf8ba5e80f3:batch:1` | `ordered_batch` | 1 | 1 | 0 | 11 | 1 | 0 | 10 | 1 | 1 | 0 | 483.22 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `e02ac24fdfde4a19bc666bf8ba5e80f3:batch:1` | 31 | 10 | 3 | 3 | 1 | 1 | 8 | 1 | 1 | 0 | 8 | 1 | 0.889 | 41.268 | 5.598 | 13.846 | 0.104 | 13.950 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | peak live bytes est | avg lag steps | max lag steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `e02ac24fdfde4a19bc666bf8ba5e80f3:batch:1` | 1 | 1 | 1 | 8000000 | 0.000 | 0 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `e02ac24fdfde4a19bc666bf8ba5e80f3:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `e02ac24fdfde4a19bc666bf8ba5e80f3:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `repeated_heavy` | `None` | 1 | 3 | 3 | False | False |
