# Stage Lifecycle Benchmark Report

- run_id: `e1c69f915df84b409f0e8751f4e65d5a`
- benchmark: `positional_phase_expr_8`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `8`
- total_time_sec: `18.282200`
- peak_rss_mb: `12951.78`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `e1c69f915df84b409f0e8751f4e65d5a:batch:1` | `ordered_batch` | 8 | 15 | 15 | 19 | 17 | 0 | 12951.62 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `e1c69f915df84b409f0e8751f4e65d5a:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `e1c69f915df84b409f0e8751f4e65d5a:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `e1c69f915df84b409f0e8751f4e65d5a:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `e1c69f915df84b409f0e8751f4e65d5a:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `e1c69f915df84b409f0e8751f4e65d5a:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | False | True |
| `e1c69f915df84b409f0e8751f4e65d5a:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `e1c69f915df84b409f0e8751f4e65d5a:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | False | True |
| `e1c69f915df84b409f0e8751f4e65d5a:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `e1c69f915df84b409f0e8751f4e65d5a:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | False | True |
| `e1c69f915df84b409f0e8751f4e65d5a:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `e1c69f915df84b409f0e8751f4e65d5a:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | False | True |
| `e1c69f915df84b409f0e8751f4e65d5a:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `e1c69f915df84b409f0e8751f4e65d5a:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | False | True |
| `e1c69f915df84b409f0e8751f4e65d5a:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `e1c69f915df84b409f0e8751f4e65d5a:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `e1c69f915df84b409f0e8751f4e65d5a:batch:1` | 1 | 1 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 797.480 | 171.397 | 366.895 | 0.464 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 469.105 | 168.238 | 330.304 | 0.426 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 20 | 391.727 | 160.750 | 378.843 | 0.424 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 326.322 | 154.519 | 363.686 | 0.439 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 20 | 416.871 | 163.168 | 371.128 | 0.378 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 424.410 | 167.709 | 336.240 | 0.445 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 5 | 430.800 | 164.979 | 326.449 | 0.392 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 0.084 | 195.052 | 327.809 | 0.543 | False | True | True | True |
