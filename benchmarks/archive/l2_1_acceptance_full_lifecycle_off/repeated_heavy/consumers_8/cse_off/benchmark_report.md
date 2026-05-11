# Stage Lifecycle Benchmark Report

- run_id: `a58b607e624c462d9ac774774cdecd6f`
- benchmark: `r4_repeated_heavy_8_cse_off`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `18.389307`
- peak_rss_mb: `14345.34`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a58b607e624c462d9ac774774cdecd6f:batch:1` | `ordered_batch` | 1 | 0 | 0 | 10 | 0 | 0 | 9 | 0 | 1 | 0 | 14345.34 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a58b607e624c462d9ac774774cdecd6f:batch:1` | 31 | 10 | 3 | 3 | 1 | 1 | 8 | 8 | 0 | 8 | 0 | 0 | 0.000 | 0.000 | 11251.394 | 365.898 | 0.104 | 366.002 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a58b607e624c462d9ac774774cdecd6f:batch:1` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 15 | 0.000 | 0 | 0.000 | 0 | 0 | 0 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `a58b607e624c462d9ac774774cdecd6f:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `repeated_heavy` | `None` | 1 | 2 | 2 | False | False |
