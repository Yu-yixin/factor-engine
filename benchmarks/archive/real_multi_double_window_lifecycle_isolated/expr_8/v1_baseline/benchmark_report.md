# Stage Lifecycle Benchmark Report

- run_id: `36dc0eb5e0624d268567f120673d8a5b`
- benchmark: `multi_double_window_8_v1`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `8`
- total_time_sec: `79.304972`
- peak_rss_mb: `9859.39`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `36dc0eb5e0624d268567f120673d8a5b:batch:1` | `ordered_batch` | 8 | 15 | 0 | 32 | 32 | 15 | 9859.39 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `36dc0eb5e0624d268567f120673d8a5b:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `36dc0eb5e0624d268567f120673d8a5b:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `36dc0eb5e0624d268567f120673d8a5b:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | True | False |
| `36dc0eb5e0624d268567f120673d8a5b:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |
| `36dc0eb5e0624d268567f120673d8a5b:batch:1:stage:5` | `materialized_child` | `______stage_value` | 1 | True | False |
| `36dc0eb5e0624d268567f120673d8a5b:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | True | False |
| `36dc0eb5e0624d268567f120673d8a5b:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | True | False |
| `36dc0eb5e0624d268567f120673d8a5b:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | True | False |
| `36dc0eb5e0624d268567f120673d8a5b:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | True | False |
| `36dc0eb5e0624d268567f120673d8a5b:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | True | False |
| `36dc0eb5e0624d268567f120673d8a5b:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | True | False |
| `36dc0eb5e0624d268567f120673d8a5b:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | True | False |
| `36dc0eb5e0624d268567f120673d8a5b:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | True | False |
| `36dc0eb5e0624d268567f120673d8a5b:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | True | False |
| `36dc0eb5e0624d268567f120673d8a5b:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | True | False |
