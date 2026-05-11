# Stage Lifecycle Benchmark Report

- run_id: `4e5c8c050b6d4d2b984674ed4f495803`
- benchmark: `positional_phase_expr_8`
- dataset: `minute_2026_03.parquet`
- rows: `500000`
- groups: `5470`
- expressions: `8`
- total_time_sec: `0.398851`
- peak_rss_mb: `316.31`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `4e5c8c050b6d4d2b984674ed4f495803:batch:1` | `ordered_batch` | 8 | 15 | 15 | 19 | 17 | 0 | 316.31 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `4e5c8c050b6d4d2b984674ed4f495803:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `4e5c8c050b6d4d2b984674ed4f495803:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `4e5c8c050b6d4d2b984674ed4f495803:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `4e5c8c050b6d4d2b984674ed4f495803:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `4e5c8c050b6d4d2b984674ed4f495803:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | False | True |
| `4e5c8c050b6d4d2b984674ed4f495803:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `4e5c8c050b6d4d2b984674ed4f495803:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | False | True |
| `4e5c8c050b6d4d2b984674ed4f495803:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `4e5c8c050b6d4d2b984674ed4f495803:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | False | True |
| `4e5c8c050b6d4d2b984674ed4f495803:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `4e5c8c050b6d4d2b984674ed4f495803:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | False | True |
| `4e5c8c050b6d4d2b984674ed4f495803:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `4e5c8c050b6d4d2b984674ed4f495803:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | False | True |
| `4e5c8c050b6d4d2b984674ed4f495803:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `4e5c8c050b6d4d2b984674ed4f495803:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `4e5c8c050b6d4d2b984674ed4f495803:batch:1` | 1 | 1 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 500000 | 5470 | 5 | 9.536 | 3.222 | 12.119 | 0.170 | False | True | True | False |
| `argmin` | 500000 | 5470 | 10 | 32.826 | 3.542 | 11.802 | 0.246 | False | True | True | False |
| `argmax` | 500000 | 5470 | 20 | 9.550 | 3.407 | 12.175 | 0.150 | False | True | True | False |
| `argmin` | 500000 | 5470 | 20 | 11.683 | 3.308 | 10.999 | 0.157 | False | True | True | False |
| `argmax` | 500000 | 5470 | 20 | 11.775 | 3.085 | 11.409 | 0.244 | False | True | True | False |
| `argmin` | 500000 | 5470 | 20 | 11.218 | 3.557 | 12.804 | 0.269 | False | True | True | False |
| `argmax` | 500000 | 5470 | 5 | 11.102 | 3.695 | 11.067 | 0.139 | False | True | True | False |
| `argmin` | 500000 | 5470 | 10 | 0.064 | 3.986 | 10.686 | 0.184 | False | True | True | False |
