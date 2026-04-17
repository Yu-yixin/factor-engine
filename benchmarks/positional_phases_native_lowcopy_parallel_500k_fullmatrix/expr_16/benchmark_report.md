# Stage Lifecycle Benchmark Report

- run_id: `3ffc6a4389b14be49926168c9772e935`
- benchmark: `positional_phase_expr_16`
- dataset: `minute_2026_03.parquet`
- rows: `500000`
- groups: `5470`
- expressions: `16`
- total_time_sec: `0.554929`
- peak_rss_mb: `360.42`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `3ffc6a4389b14be49926168c9772e935:batch:1` | `ordered_batch` | 16 | 23 | 23 | 27 | 25 | 0 | 360.00 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:1` | `materialized_child` | `__stage_value` | 2 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:3` | `materialized_child` | `____stage_value` | 2 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:5` | `materialized_child` | `______stage_value` | 4 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:7` | `materialized_child` | `________stage_value` | 2 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 2 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 2 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 2 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:16` | `positional_result` | `_________________stage_value` | 1 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:17` | `positional_result` | `__________________stage_value` | 1 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:18` | `positional_result` | `___________________stage_value` | 1 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:19` | `positional_result` | `____________________stage_value` | 1 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:20` | `positional_result` | `_____________________stage_value` | 1 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:21` | `positional_result` | `______________________stage_value` | 1 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:22` | `positional_result` | `_______________________stage_value` | 1 | False | True |
| `3ffc6a4389b14be49926168c9772e935:batch:1:stage:23` | `positional_result` | `________________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `3ffc6a4389b14be49926168c9772e935:batch:1` | 7 | 9 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 500000 | 5470 | 5 | 10.747 | 3.463 | 6.295 | 0.154 | False | True | True | True |
| `argmin` | 500000 | 5470 | 10 | 15.026 | 3.701 | 5.891 | 0.148 | False | True | True | True |
| `argmax` | 500000 | 5470 | 20 | 14.621 | 3.847 | 7.008 | 0.177 | False | True | True | True |
| `argmin` | 500000 | 5470 | 20 | 11.796 | 3.462 | 6.324 | 0.176 | False | True | True | True |
| `argmax` | 500000 | 5470 | 20 | 11.519 | 3.166 | 5.650 | 0.159 | False | True | True | True |
| `argmin` | 500000 | 5470 | 20 | 11.508 | 3.480 | 6.213 | 0.192 | False | True | True | True |
| `argmax` | 500000 | 5470 | 5 | 10.368 | 3.259 | 6.014 | 0.146 | False | True | True | True |
| `argmin` | 500000 | 5470 | 10 | 0.066 | 3.765 | 6.221 | 0.131 | False | True | True | True |
| `argmax` | 500000 | 5470 | 30 | 0.069 | 3.656 | 6.342 | 0.292 | False | True | True | True |
| `argmin` | 500000 | 5470 | 40 | 0.112 | 3.600 | 6.995 | 0.157 | False | True | True | True |
| `argmax` | 500000 | 5470 | 60 | 0.273 | 3.481 | 6.139 | 0.150 | False | True | True | True |
| `argmin` | 500000 | 5470 | 20 | 0.065 | 3.949 | 5.357 | 0.301 | False | True | True | True |
| `argmax` | 500000 | 5470 | 30 | 0.090 | 3.726 | 5.725 | 0.183 | False | True | True | True |
| `argmin` | 500000 | 5470 | 40 | 0.067 | 3.528 | 6.569 | 0.212 | False | True | True | True |
| `argmax` | 500000 | 5470 | 60 | 0.068 | 3.887 | 5.561 | 0.290 | False | True | True | True |
| `argmin` | 500000 | 5470 | 20 | 0.104 | 3.901 | 5.788 | 0.144 | False | True | True | True |
