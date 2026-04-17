# Stage Lifecycle Benchmark Report

- run_id: `73b8ad1851e841a4af8afc54e0b3e1f7`
- benchmark: `positional_phase_expr_20`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `20`
- total_time_sec: `34.231298`
- peak_rss_mb: `22245.18`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1` | `ordered_batch` | 20 | 31 | 31 | 31 | 29 | 0 | 22245.18 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:1` | `materialized_child` | `__stage_value` | 2 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:3` | `materialized_child` | `____stage_value` | 2 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:5` | `materialized_child` | `______stage_value` | 4 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:7` | `materialized_child` | `________stage_value` | 2 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 2 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 2 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 2 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:16` | `positional_result` | `_________________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:17` | `positional_result` | `__________________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:18` | `positional_result` | `___________________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:19` | `positional_result` | `____________________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:20` | `positional_result` | `_____________________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:21` | `positional_result` | `______________________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:22` | `positional_result` | `_______________________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:23` | `positional_result` | `________________________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:24` | `materialized_child` | `_________________________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:25` | `positional_result` | `__________________________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:26` | `materialized_child` | `___________________________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:27` | `positional_result` | `____________________________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:28` | `materialized_child` | `_____________________________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:29` | `positional_result` | `______________________________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:30` | `materialized_child` | `_______________________________stage_value` | 1 | False | True |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1:stage:31` | `positional_result` | `________________________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `73b8ad1851e841a4af8afc54e0b3e1f7:batch:1` | 7 | 9 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 750.777 | 280.712 | 474.665 | 0.563 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 550.643 | 165.949 | 369.070 | 0.517 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 20 | 421.057 | 162.425 | 277.602 | 0.369 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 398.819 | 159.249 | 293.746 | 0.433 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 20 | 440.532 | 226.826 | 285.803 | 0.679 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 391.884 | 144.380 | 311.589 | 0.414 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 5 | 389.229 | 286.651 | 501.294 | 0.451 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 0.066 | 153.585 | 348.539 | 0.414 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 30 | 0.097 | 168.189 | 362.460 | 0.576 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 40 | 0.087 | 199.480 | 949.706 | 0.559 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 60 | 0.096 | 150.545 | 273.383 | 0.412 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 0.092 | 201.756 | 329.880 | 0.402 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 30 | 0.099 | 152.875 | 320.875 | 0.428 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 40 | 0.078 | 140.056 | 357.428 | 0.424 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 60 | 0.073 | 219.054 | 288.383 | 0.524 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 0.114 | 154.012 | 323.957 | 0.364 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 15 | 603.090 | 268.573 | 433.277 | 0.419 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 25 | 439.291 | 178.803 | 359.652 | 0.439 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 20 | 403.376 | 164.217 | 404.841 | 0.465 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 488.939 | 179.999 | 434.106 | 0.384 | False | True | True | True |
