# Stage Lifecycle Benchmark Report

- run_id: `d337d33314de4d538655672b074c3e65`
- benchmark: `real_smoke_v2`
- dataset: `minute_2026_03.parquet`
- rows: `500000`
- groups: `5470`
- expressions: `5`
- total_time_sec: `0.789077`
- peak_rss_mb: `379.77`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d337d33314de4d538655672b074c3e65:batch:1` | `ordered_batch` | 5 | 13 | 13 | 17 | 14 | 0 | 379.77 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `d337d33314de4d538655672b074c3e65:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `d337d33314de4d538655672b074c3e65:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `d337d33314de4d538655672b074c3e65:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `d337d33314de4d538655672b074c3e65:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `d337d33314de4d538655672b074c3e65:batch:1:stage:5` | `ordered_helper` | `______stage_value` | 1 | False | True |
| `d337d33314de4d538655672b074c3e65:batch:1:stage:6` | `staged_prefix` | `_______stage_value` | 1 | False | True |
| `d337d33314de4d538655672b074c3e65:batch:1:stage:7` | `materialized_result` | `________stage_value` | 1 | False | True |
| `d337d33314de4d538655672b074c3e65:batch:1:stage:8` | `materialized_child` | `_________stage_value` | 1 | False | True |
| `d337d33314de4d538655672b074c3e65:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | False | True |
| `d337d33314de4d538655672b074c3e65:batch:1:stage:10` | `materialized_result` | `___________stage_value` | 1 | False | True |
| `d337d33314de4d538655672b074c3e65:batch:1:stage:11` | `ordered_helper` | `____________stage_value` | 1 | False | True |
| `d337d33314de4d538655672b074c3e65:batch:1:stage:12` | `staged_prefix` | `_____________stage_value` | 1 | False | True |
| `d337d33314de4d538655672b074c3e65:batch:1:stage:13` | `staged_prefix` | `______________stage_value` | 1 | False | True |
