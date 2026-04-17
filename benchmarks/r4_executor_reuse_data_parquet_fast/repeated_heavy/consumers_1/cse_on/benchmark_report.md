# Stage Lifecycle Benchmark Report

- run_id: `b1cbf3a38a3e432983a191c2391e6bb5`
- benchmark: `r4_repeated_heavy_1_cse_on`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `10.998332`
- peak_rss_mb: `11502.99`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `b1cbf3a38a3e432983a191c2391e6bb5:batch:1` | `ordered_batch` | 1 | 0 | 0 | 9 | 0 | 0 | 9 | 0 | 1 | 0 | 11502.99 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | compute calls | store hits | hit rate | compute ms | store write ms | store hit ms | result store peak | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `b1cbf3a38a3e432983a191c2391e6bb5:batch:1` | 3 | 3 | 0 | 0 | 0 | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 1 | 2690.831 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `b1cbf3a38a3e432983a191c2391e6bb5:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `repeated_heavy` | `None` | 1 | 2 | 2 | False | False |
