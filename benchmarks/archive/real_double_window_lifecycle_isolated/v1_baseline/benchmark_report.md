# Stage Lifecycle Benchmark Report

- run_id: `56ea595ffbf647a5ad952304f2cde7bc`
- benchmark: `isolated_double_window_v1`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `16.411643`
- peak_rss_mb: `5736.39`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `56ea595ffbf647a5ad952304f2cde7bc:batch:1` | `ordered_batch` | 1 | 2 | 0 | 12 | 12 | 2 | 5736.39 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `56ea595ffbf647a5ad952304f2cde7bc:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `56ea595ffbf647a5ad952304f2cde7bc:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
