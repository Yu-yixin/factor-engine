# Stage Lifecycle Benchmark Report

- run_id: `fe4772844b29463e81437f808f93254b`
- benchmark: `isolated_double_window_v2`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `15.118189`
- peak_rss_mb: `5659.73`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fe4772844b29463e81437f808f93254b:batch:1` | `ordered_batch` | 1 | 2 | 2 | 12 | 10 | 0 | 5659.72 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `fe4772844b29463e81437f808f93254b:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `fe4772844b29463e81437f808f93254b:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
