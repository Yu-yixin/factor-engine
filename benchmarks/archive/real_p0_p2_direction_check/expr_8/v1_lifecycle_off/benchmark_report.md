# Stage Lifecycle Benchmark Report

- run_id: `3b5c3adeb0c24ffcba28cf009dc44776`
- benchmark: `direction_check_8_v1`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `8`
- total_time_sec: `89.720127`
- peak_rss_mb: `9883.10`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `3b5c3adeb0c24ffcba28cf009dc44776:batch:1` | `ordered_batch` | 8 | 15 | 0 | 32 | 32 | 15 | 9883.09 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `3b5c3adeb0c24ffcba28cf009dc44776:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `3b5c3adeb0c24ffcba28cf009dc44776:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `3b5c3adeb0c24ffcba28cf009dc44776:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | True | False |
| `3b5c3adeb0c24ffcba28cf009dc44776:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |
| `3b5c3adeb0c24ffcba28cf009dc44776:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | True | False |
| `3b5c3adeb0c24ffcba28cf009dc44776:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | True | False |
| `3b5c3adeb0c24ffcba28cf009dc44776:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | True | False |
| `3b5c3adeb0c24ffcba28cf009dc44776:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | True | False |
| `3b5c3adeb0c24ffcba28cf009dc44776:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | True | False |
| `3b5c3adeb0c24ffcba28cf009dc44776:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | True | False |
| `3b5c3adeb0c24ffcba28cf009dc44776:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | True | False |
| `3b5c3adeb0c24ffcba28cf009dc44776:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | True | False |
| `3b5c3adeb0c24ffcba28cf009dc44776:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | True | False |
| `3b5c3adeb0c24ffcba28cf009dc44776:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | True | False |
| `3b5c3adeb0c24ffcba28cf009dc44776:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | True | False |

## Positional Phases

| function | rows | groups | window | child ms | to_list ms | scan ms | attach ms | python kernel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `argmax` | 29048679 | 5495 | 5 | 510.891 | 516.499 | 8393.433 | 206.169 | True |
| `argmin` | 29048679 | 5495 | 10 | 379.290 | 563.602 | 8226.823 | 164.889 | True |
| `argmax` | 29048679 | 5495 | 20 | 381.701 | 505.996 | 8310.396 | 234.225 | True |
| `argmin` | 29048679 | 5495 | 20 | 442.150 | 551.356 | 7973.517 | 167.995 | True |
| `argmax` | 29048679 | 5495 | 20 | 384.714 | 545.811 | 8037.509 | 191.448 | True |
| `argmin` | 29048679 | 5495 | 20 | 421.532 | 554.324 | 7598.065 | 183.141 | True |
| `argmax` | 29048679 | 5495 | 5 | 360.465 | 592.479 | 8631.772 | 175.556 | True |
| `argmin` | 29048679 | 5495 | 10 | 0.091 | 534.284 | 7472.416 | 225.232 | True |
