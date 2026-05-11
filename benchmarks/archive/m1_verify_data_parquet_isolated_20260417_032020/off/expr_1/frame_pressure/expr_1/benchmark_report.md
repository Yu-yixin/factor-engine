# Stage Lifecycle Benchmark Report

- run_id: `93a9442ced49479fa6933c8cc7e06e40`
- benchmark: `m1_frame_pressure_1`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `13.231909`
- peak_rss_mb: `12655.30`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `93a9442ced49479fa6933c8cc7e06e40:batch:1` | `ordered_batch` | 1 | 3 | 0 | 12 | 3 | 0 | 12 | 3 | 1 | 0 | 12655.30 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `93a9442ced49479fa6933c8cc7e06e40:batch:1:stage:1` | `ordered_helper` | `__stage_value` | 1 | True | False |
| `93a9442ced49479fa6933c8cc7e06e40:batch:1:stage:2` | `staged_prefix` | `___stage_value` | 1 | True | False |
| `93a9442ced49479fa6933c8cc7e06e40:batch:1:stage:3` | `staged_prefix` | `____stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `93a9442ced49479fa6933c8cc7e06e40:batch:1` | 0 | 0 | 0 | 1 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `frame_01` | `____stage_value` | 8 | 9 | 9 | False | False |
