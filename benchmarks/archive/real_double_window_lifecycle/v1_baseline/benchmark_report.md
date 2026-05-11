# Stage Lifecycle Benchmark Report

- run_id: `e8e13462bcc743a6b84df694ac346c40`
- benchmark: `real_double_window_v1_baseline`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `16.974941`
- peak_rss_mb: `5708.41`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `e8e13462bcc743a6b84df694ac346c40:batch:1` | `ordered_batch` | 1 | 2 | 0 | 12 | 12 | 2 | 5708.40 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `e8e13462bcc743a6b84df694ac346c40:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `e8e13462bcc743a6b84df694ac346c40:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
