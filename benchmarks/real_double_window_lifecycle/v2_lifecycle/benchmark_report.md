# Stage Lifecycle Benchmark Report

- run_id: `0c41a7f2e27648c990836fbd2e53bca7`
- benchmark: `real_double_window_v2_lifecycle`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `16.261483`
- peak_rss_mb: `10876.55`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0c41a7f2e27648c990836fbd2e53bca7:batch:1` | `ordered_batch` | 1 | 2 | 2 | 12 | 10 | 0 | 10876.55 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `0c41a7f2e27648c990836fbd2e53bca7:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `0c41a7f2e27648c990836fbd2e53bca7:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
