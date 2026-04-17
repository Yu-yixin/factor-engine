# Stage Lifecycle Benchmark Report

- run_id: `8ca6b5f3e5d64e0185ab5cfe112d0535`
- benchmark: `positional_phase_expr_20`
- dataset: `minute_2026_03.parquet`
- rows: `500000`
- groups: `5470`
- expressions: `20`
- total_time_sec: `0.878923`
- peak_rss_mb: `373.83`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1` | `ordered_batch` | 20 | 31 | 31 | 31 | 29 | 0 | 373.82 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:1` | `materialized_child` | `__stage_value` | 2 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:3` | `materialized_child` | `____stage_value` | 2 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:5` | `materialized_child` | `______stage_value` | 4 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:7` | `materialized_child` | `________stage_value` | 2 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 2 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 2 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 2 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:16` | `positional_result` | `_________________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:17` | `positional_result` | `__________________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:18` | `positional_result` | `___________________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:19` | `positional_result` | `____________________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:20` | `positional_result` | `_____________________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:21` | `positional_result` | `______________________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:22` | `positional_result` | `_______________________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:23` | `positional_result` | `________________________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:24` | `materialized_child` | `_________________________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:25` | `positional_result` | `__________________________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:26` | `materialized_child` | `___________________________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:27` | `positional_result` | `____________________________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:28` | `materialized_child` | `_____________________________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:29` | `positional_result` | `______________________________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:30` | `materialized_child` | `_______________________________stage_value` | 1 | False | True |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1:stage:31` | `positional_result` | `________________________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `8ca6b5f3e5d64e0185ab5cfe112d0535:batch:1` | 7 | 9 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 500000 | 5470 | 5 | 13.586 | 3.691 | 5.976 | 0.272 | False | True | True | True |
| `argmin` | 500000 | 5470 | 10 | 17.961 | 3.419 | 6.551 | 0.167 | False | True | True | True |
| `argmax` | 500000 | 5470 | 20 | 11.285 | 3.817 | 5.736 | 0.124 | False | True | True | True |
| `argmin` | 500000 | 5470 | 20 | 15.597 | 3.519 | 6.375 | 0.148 | False | True | True | True |
| `argmax` | 500000 | 5470 | 20 | 10.388 | 3.462 | 6.264 | 0.320 | False | True | True | True |
| `argmin` | 500000 | 5470 | 20 | 10.275 | 3.370 | 6.568 | 0.128 | False | True | True | True |
| `argmax` | 500000 | 5470 | 5 | 14.338 | 5.352 | 5.867 | 0.173 | False | True | True | True |
| `argmin` | 500000 | 5470 | 10 | 0.066 | 4.578 | 6.804 | 0.140 | False | True | True | True |
| `argmax` | 500000 | 5470 | 30 | 0.121 | 4.075 | 6.910 | 0.149 | False | True | True | True |
| `argmin` | 500000 | 5470 | 40 | 0.104 | 4.192 | 7.267 | 0.544 | False | True | True | True |
| `argmax` | 500000 | 5470 | 60 | 0.070 | 3.829 | 7.547 | 0.153 | False | True | True | True |
| `argmin` | 500000 | 5470 | 20 | 0.084 | 4.737 | 6.138 | 0.223 | False | True | True | True |
| `argmax` | 500000 | 5470 | 30 | 0.101 | 4.228 | 6.561 | 0.186 | False | True | True | True |
| `argmin` | 500000 | 5470 | 40 | 0.089 | 4.054 | 7.067 | 0.218 | False | True | True | True |
| `argmax` | 500000 | 5470 | 60 | 0.072 | 5.301 | 6.433 | 0.233 | False | True | True | True |
| `argmin` | 500000 | 5470 | 20 | 0.109 | 4.321 | 6.606 | 0.351 | False | True | True | True |
| `argmax` | 500000 | 5470 | 15 | 17.791 | 3.812 | 6.099 | 0.240 | False | True | True | True |
| `argmin` | 500000 | 5470 | 25 | 16.749 | 3.566 | 6.250 | 0.330 | False | True | True | True |
| `argmax` | 500000 | 5470 | 20 | 16.040 | 4.187 | 8.658 | 0.339 | False | True | True | True |
| `argmin` | 500000 | 5470 | 20 | 19.417 | 5.195 | 8.010 | 0.224 | False | True | True | True |
