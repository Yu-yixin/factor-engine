# Stage Lifecycle Benchmark Report

- run_id: `084f440c74764c1eb35e9b3c708aad5f`
- benchmark: `positional_phase_expr_8`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `8`
- total_time_sec: `20.930046`
- peak_rss_mb: `13944.23`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `084f440c74764c1eb35e9b3c708aad5f:batch:1` | `ordered_batch` | 8 | 15 | 15 | 19 | 17 | 0 | 13944.11 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `084f440c74764c1eb35e9b3c708aad5f:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `084f440c74764c1eb35e9b3c708aad5f:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `084f440c74764c1eb35e9b3c708aad5f:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `084f440c74764c1eb35e9b3c708aad5f:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `084f440c74764c1eb35e9b3c708aad5f:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | False | True |
| `084f440c74764c1eb35e9b3c708aad5f:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `084f440c74764c1eb35e9b3c708aad5f:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | False | True |
| `084f440c74764c1eb35e9b3c708aad5f:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `084f440c74764c1eb35e9b3c708aad5f:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | False | True |
| `084f440c74764c1eb35e9b3c708aad5f:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `084f440c74764c1eb35e9b3c708aad5f:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | False | True |
| `084f440c74764c1eb35e9b3c708aad5f:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `084f440c74764c1eb35e9b3c708aad5f:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | False | True |
| `084f440c74764c1eb35e9b3c708aad5f:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `084f440c74764c1eb35e9b3c708aad5f:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `084f440c74764c1eb35e9b3c708aad5f:batch:1` | 1 | 1 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 485.679 | 160.858 | 704.770 | 0.456 | False | True | True | False |
| `argmin` | 29048679 | 5495 | 10 | 426.695 | 150.786 | 763.643 | 0.468 | False | True | True | False |
| `argmax` | 29048679 | 5495 | 20 | 408.126 | 157.449 | 646.870 | 0.390 | False | True | True | False |
| `argmin` | 29048679 | 5495 | 20 | 388.770 | 166.034 | 669.385 | 0.433 | False | True | True | False |
| `argmax` | 29048679 | 5495 | 20 | 450.441 | 202.203 | 629.749 | 0.631 | False | True | True | False |
| `argmin` | 29048679 | 5495 | 20 | 442.019 | 170.583 | 601.510 | 0.549 | False | True | True | False |
| `argmax` | 29048679 | 5495 | 5 | 442.184 | 175.706 | 765.443 | 0.438 | False | True | True | False |
| `argmin` | 29048679 | 5495 | 10 | 0.087 | 183.754 | 815.030 | 0.418 | False | True | True | False |
