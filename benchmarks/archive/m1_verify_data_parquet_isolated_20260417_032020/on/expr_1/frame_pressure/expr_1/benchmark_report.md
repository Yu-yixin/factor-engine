# Stage Lifecycle Benchmark Report

- run_id: `1362539f26d0428a927f7b5609cdbf52`
- benchmark: `m1_frame_pressure_1`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `12.699432`
- peak_rss_mb: `12679.97`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `1362539f26d0428a927f7b5609cdbf52:batch:1` | `ordered_batch` | 1 | 3 | 3 | 12 | 3 | 0 | 9 | 0 | 1 | 0 | 12679.91 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `1362539f26d0428a927f7b5609cdbf52:batch:1:stage:1` | `ordered_helper` | `__stage_value` | 1 | False | True |
| `1362539f26d0428a927f7b5609cdbf52:batch:1:stage:2` | `staged_prefix` | `___stage_value` | 1 | False | True |
| `1362539f26d0428a927f7b5609cdbf52:batch:1:stage:3` | `staged_prefix` | `____stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `1362539f26d0428a927f7b5609cdbf52:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `frame_01` | `____stage_value` | 8 | 12 | 12 | False | False |
