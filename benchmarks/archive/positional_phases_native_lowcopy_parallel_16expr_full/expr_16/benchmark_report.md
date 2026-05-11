# Stage Lifecycle Benchmark Report

- run_id: `7a21ee233a8f4be69969f3954c31f60d`
- benchmark: `positional_phase_expr_16`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `16`
- total_time_sec: `22.965138`
- peak_rss_mb: `12754.71`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1` | `ordered_batch` | 16 | 23 | 23 | 27 | 25 | 0 | 12754.71 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:1` | `materialized_child` | `__stage_value` | 2 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:3` | `materialized_child` | `____stage_value` | 2 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:5` | `materialized_child` | `______stage_value` | 4 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:7` | `materialized_child` | `________stage_value` | 2 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 2 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 2 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 2 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:16` | `positional_result` | `_________________stage_value` | 1 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:17` | `positional_result` | `__________________stage_value` | 1 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:18` | `positional_result` | `___________________stage_value` | 1 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:19` | `positional_result` | `____________________stage_value` | 1 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:20` | `positional_result` | `_____________________stage_value` | 1 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:21` | `positional_result` | `______________________stage_value` | 1 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:22` | `positional_result` | `_______________________stage_value` | 1 | False | True |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1:stage:23` | `positional_result` | `________________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `7a21ee233a8f4be69969f3954c31f60d:batch:1` | 7 | 9 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 509.672 | 188.547 | 359.050 | 0.681 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 336.790 | 158.547 | 364.937 | 0.451 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 20 | 339.599 | 210.658 | 323.326 | 0.385 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 424.733 | 170.682 | 344.350 | 0.407 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 20 | 410.767 | 174.276 | 318.053 | 0.498 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 365.252 | 154.478 | 287.788 | 0.334 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 5 | 310.926 | 148.050 | 335.485 | 0.448 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 0.072 | 147.839 | 329.028 | 0.352 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 30 | 0.064 | 156.500 | 300.223 | 0.335 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 40 | 0.080 | 174.605 | 391.281 | 0.429 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 60 | 0.085 | 150.220 | 341.052 | 0.437 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 0.077 | 153.494 | 315.809 | 0.421 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 30 | 0.100 | 149.728 | 263.166 | 0.512 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 40 | 0.072 | 178.371 | 276.316 | 0.382 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 60 | 0.074 | 146.435 | 261.220 | 0.343 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 0.099 | 148.143 | 300.553 | 0.345 | False | True | True | True |
