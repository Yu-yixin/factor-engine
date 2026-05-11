# Stage Lifecycle Benchmark Report

- run_id: `ca6c616933724e2dbc3fc88a981a7003`
- benchmark: `positional_phase_expr_8`
- dataset: `minute_2026_03.parquet`
- rows: `500000`
- groups: `5470`
- expressions: `8`
- total_time_sec: `0.380464`
- peak_rss_mb: `320.79`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ca6c616933724e2dbc3fc88a981a7003:batch:1` | `ordered_batch` | 8 | 15 | 15 | 19 | 17 | 0 | 320.77 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `ca6c616933724e2dbc3fc88a981a7003:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `ca6c616933724e2dbc3fc88a981a7003:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `ca6c616933724e2dbc3fc88a981a7003:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `ca6c616933724e2dbc3fc88a981a7003:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `ca6c616933724e2dbc3fc88a981a7003:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | False | True |
| `ca6c616933724e2dbc3fc88a981a7003:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `ca6c616933724e2dbc3fc88a981a7003:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | False | True |
| `ca6c616933724e2dbc3fc88a981a7003:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `ca6c616933724e2dbc3fc88a981a7003:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | False | True |
| `ca6c616933724e2dbc3fc88a981a7003:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `ca6c616933724e2dbc3fc88a981a7003:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | False | True |
| `ca6c616933724e2dbc3fc88a981a7003:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `ca6c616933724e2dbc3fc88a981a7003:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | False | True |
| `ca6c616933724e2dbc3fc88a981a7003:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `ca6c616933724e2dbc3fc88a981a7003:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `ca6c616933724e2dbc3fc88a981a7003:batch:1` | 1 | 1 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 500000 | 5470 | 5 | 10.064 | 3.211 | 6.841 | 0.170 | False | True | True | True |
| `argmin` | 500000 | 5470 | 10 | 11.887 | 3.685 | 5.282 | 0.137 | False | True | True | True |
| `argmax` | 500000 | 5470 | 20 | 13.451 | 3.516 | 5.465 | 0.142 | False | True | True | True |
| `argmin` | 500000 | 5470 | 20 | 13.969 | 3.339 | 5.741 | 0.142 | False | True | True | True |
| `argmax` | 500000 | 5470 | 20 | 11.183 | 3.336 | 5.744 | 0.146 | False | True | True | True |
| `argmin` | 500000 | 5470 | 20 | 8.907 | 3.415 | 5.612 | 0.134 | False | True | True | True |
| `argmax` | 500000 | 5470 | 5 | 11.294 | 4.007 | 5.480 | 0.150 | False | True | True | True |
| `argmin` | 500000 | 5470 | 10 | 0.068 | 3.930 | 6.357 | 0.141 | False | True | True | True |
