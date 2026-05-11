# Stage Lifecycle Benchmark Report

- run_id: `f45978f963464f079b8debebdb99b34d`
- benchmark: `r4_repeated_heavy_2_cse_off`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `13.003021`
- peak_rss_mb: `14101.67`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `f45978f963464f079b8debebdb99b34d:batch:1` | `ordered_batch` | 1 | 0 | 0 | 9 | 0 | 0 | 9 | 0 | 1 | 0 | 14101.67 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | compute calls | store hits | hit rate | compute ms | store write ms | store hit ms | result store peak | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `f45978f963464f079b8debebdb99b34d:batch:1` | 7 | 4 | 3 | 3 | 1 | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 1 | 4405.421 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `f45978f963464f079b8debebdb99b34d:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `repeated_heavy` | `None` | 1 | 2 | 2 | False | False |
