# Stage Lifecycle Benchmark Report

- run_id: `d5df575d4344447eb80c59632946bf5d`
- benchmark: `multi_double_window_16_v2`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `16`
- total_time_sec: `149.762532`
- peak_rss_mb: `12061.11`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d5df575d4344447eb80c59632946bf5d:batch:1` | `ordered_batch` | 16 | 32 | 32 | 27 | 25 | 0 | 12061.03 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:5` | `materialized_child` | `______stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:15` | `materialized_child` | `________________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:16` | `positional_result` | `_________________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:17` | `materialized_child` | `__________________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:18` | `positional_result` | `___________________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:19` | `materialized_child` | `____________________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:20` | `positional_result` | `_____________________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:21` | `materialized_child` | `______________________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:22` | `positional_result` | `_______________________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:23` | `materialized_child` | `________________________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:24` | `positional_result` | `_________________________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:25` | `materialized_child` | `__________________________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:26` | `positional_result` | `___________________________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:27` | `materialized_child` | `____________________________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:28` | `positional_result` | `_____________________________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:29` | `materialized_child` | `______________________________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:30` | `positional_result` | `_______________________________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:31` | `materialized_child` | `________________________________stage_value` | 1 | False | True |
| `d5df575d4344447eb80c59632946bf5d:batch:1:stage:32` | `positional_result` | `_________________________________stage_value` | 1 | False | True |
