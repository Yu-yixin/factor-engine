# Stage Lifecycle Benchmark Report

- run_id: `3e685087a4034112b897b3332c9ea2c7`
- benchmark: `m1_frame_pressure_2`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `2`
- total_time_sec: `18.915998`
- peak_rss_mb: `21483.29`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `3e685087a4034112b897b3332c9ea2c7:batch:1` | `ordered_batch` | 2 | 6 | 0 | 15 | 6 | 0 | 15 | 6 | 2 | 0 | 21483.24 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `3e685087a4034112b897b3332c9ea2c7:batch:1:stage:1` | `ordered_helper` | `__stage_value` | 1 | True | False |
| `3e685087a4034112b897b3332c9ea2c7:batch:1:stage:2` | `ordered_helper` | `___stage_value` | 1 | True | False |
| `3e685087a4034112b897b3332c9ea2c7:batch:1:stage:3` | `staged_prefix` | `____stage_value` | 1 | True | False |
| `3e685087a4034112b897b3332c9ea2c7:batch:1:stage:4` | `staged_prefix` | `_____stage_value` | 1 | True | False |
| `3e685087a4034112b897b3332c9ea2c7:batch:1:stage:5` | `staged_prefix` | `______stage_value` | 1 | True | False |
| `3e685087a4034112b897b3332c9ea2c7:batch:1:stage:6` | `staged_prefix` | `_______stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `3e685087a4034112b897b3332c9ea2c7:batch:1` | 0 | 0 | 0 | 2 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `frame_01` | `_____stage_value` | 14 | 17 | 17 | False | False |
| `frame_02` | `_______stage_value` | 16 | 18 | 18 | False | False |
