# Stage Lifecycle Benchmark Report

- run_id: `b6709fdd567545dc903f35cbecbaf1da`
- benchmark: `multi_double_window_8_v2`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `8`
- total_time_sec: `78.676464`
- peak_rss_mb: `8479.27`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `b6709fdd567545dc903f35cbecbaf1da:batch:1` | `ordered_batch` | 8 | 16 | 16 | 19 | 17 | 0 | 8479.26 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `b6709fdd567545dc903f35cbecbaf1da:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `b6709fdd567545dc903f35cbecbaf1da:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `b6709fdd567545dc903f35cbecbaf1da:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `b6709fdd567545dc903f35cbecbaf1da:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `b6709fdd567545dc903f35cbecbaf1da:batch:1:stage:5` | `materialized_child` | `______stage_value` | 1 | False | True |
| `b6709fdd567545dc903f35cbecbaf1da:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `b6709fdd567545dc903f35cbecbaf1da:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | False | True |
| `b6709fdd567545dc903f35cbecbaf1da:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `b6709fdd567545dc903f35cbecbaf1da:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | False | True |
| `b6709fdd567545dc903f35cbecbaf1da:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `b6709fdd567545dc903f35cbecbaf1da:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | False | True |
| `b6709fdd567545dc903f35cbecbaf1da:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `b6709fdd567545dc903f35cbecbaf1da:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | False | True |
| `b6709fdd567545dc903f35cbecbaf1da:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `b6709fdd567545dc903f35cbecbaf1da:batch:1:stage:15` | `materialized_child` | `________________stage_value` | 1 | False | True |
| `b6709fdd567545dc903f35cbecbaf1da:batch:1:stage:16` | `positional_result` | `_________________stage_value` | 1 | False | True |
