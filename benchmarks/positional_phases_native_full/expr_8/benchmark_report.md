# Stage Lifecycle Benchmark Report

- run_id: `c44aa8d9a49b4977bf9a6589caf657ef`
- benchmark: `positional_phase_expr_8`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `8`
- total_time_sec: `31.475720`
- peak_rss_mb: `12270.62`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `c44aa8d9a49b4977bf9a6589caf657ef:batch:1` | `ordered_batch` | 8 | 15 | 15 | 19 | 17 | 0 | 12270.59 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `c44aa8d9a49b4977bf9a6589caf657ef:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `c44aa8d9a49b4977bf9a6589caf657ef:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `c44aa8d9a49b4977bf9a6589caf657ef:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `c44aa8d9a49b4977bf9a6589caf657ef:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `c44aa8d9a49b4977bf9a6589caf657ef:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | False | True |
| `c44aa8d9a49b4977bf9a6589caf657ef:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `c44aa8d9a49b4977bf9a6589caf657ef:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | False | True |
| `c44aa8d9a49b4977bf9a6589caf657ef:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `c44aa8d9a49b4977bf9a6589caf657ef:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | False | True |
| `c44aa8d9a49b4977bf9a6589caf657ef:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `c44aa8d9a49b4977bf9a6589caf657ef:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | False | True |
| `c44aa8d9a49b4977bf9a6589caf657ef:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `c44aa8d9a49b4977bf9a6589caf657ef:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | False | True |
| `c44aa8d9a49b4977bf9a6589caf657ef:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `c44aa8d9a49b4977bf9a6589caf657ef:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `c44aa8d9a49b4977bf9a6589caf657ef:batch:1` | 1 | 1 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | to_list ms | scan ms | attach ms | python | native |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 403.080 | 1861.548 | 600.205 | 0.129 | False | True |
| `argmin` | 29048679 | 5495 | 10 | 547.801 | 1810.108 | 517.643 | 0.069 | False | True |
| `argmax` | 29048679 | 5495 | 20 | 468.391 | 1358.107 | 455.749 | 0.092 | False | True |
| `argmin` | 29048679 | 5495 | 20 | 382.771 | 1428.311 | 430.440 | 0.115 | False | True |
| `argmax` | 29048679 | 5495 | 20 | 423.370 | 1278.073 | 419.692 | 0.079 | False | True |
| `argmin` | 29048679 | 5495 | 20 | 390.169 | 1195.652 | 351.131 | 0.077 | False | True |
| `argmax` | 29048679 | 5495 | 5 | 458.370 | 1253.582 | 349.690 | 0.079 | False | True |
| `argmin` | 29048679 | 5495 | 10 | 0.076 | 1369.719 | 382.589 | 0.126 | False | True |
