# Stage Lifecycle Benchmark Report

- run_id: `1f414f8b2b464574b6696a77f74b5abb`
- benchmark: `r4_repeated_heavy_4_cse_off`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `0.328602`
- peak_rss_mb: `533.11`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `1f414f8b2b464574b6696a77f74b5abb:batch:1` | `ordered_batch` | 1 | 0 | 0 | 10 | 0 | 0 | 9 | 0 | 1 | 0 | 533.11 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `1f414f8b2b464574b6696a77f74b5abb:batch:1` | 15 | 6 | 3 | 3 | 1 | 1 | 4 | 4 | 0 | 4 | 0 | 0 | 0.000 | 0.000 | 201.820 | 17.889 | 0.110 | 18.000 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | peak live bytes est | avg lag steps | max lag steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `1f414f8b2b464574b6696a77f74b5abb:batch:1` | 1 | 0 | 0 | 0 | 0.000 | 0 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `1f414f8b2b464574b6696a77f74b5abb:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `repeated_heavy` | `None` | 1 | 2 | 2 | False | False |
