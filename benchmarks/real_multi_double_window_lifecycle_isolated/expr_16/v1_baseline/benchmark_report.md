# Stage Lifecycle Benchmark Report

- run_id: `7789ea8e51c6485899a3c52eef9f9cbc`
- benchmark: `multi_double_window_16_v1`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `16`
- total_time_sec: `145.547837`
- peak_rss_mb: `13393.20`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1` | `ordered_batch` | 16 | 23 | 0 | 48 | 48 | 23 | 13393.19 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:5` | `materialized_child` | `______stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:16` | `positional_result` | `_________________stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:17` | `positional_result` | `__________________stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:18` | `positional_result` | `___________________stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:19` | `positional_result` | `____________________stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:20` | `positional_result` | `_____________________stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:21` | `positional_result` | `______________________stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:22` | `positional_result` | `_______________________stage_value` | 1 | True | False |
| `7789ea8e51c6485899a3c52eef9f9cbc:batch:1:stage:23` | `positional_result` | `________________________stage_value` | 1 | True | False |
