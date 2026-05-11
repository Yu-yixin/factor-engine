# Stage Lifecycle Benchmark Report

- run_id: `be0d508647764ab5bac81bda53eb0759`
- benchmark: `positional_phase_expr_8`
- dataset: `minute_2026_03.parquet`
- rows: `500000`
- groups: `5470`
- expressions: `8`
- total_time_sec: `1.477901`
- peak_rss_mb: `292.47`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `be0d508647764ab5bac81bda53eb0759:batch:1` | `ordered_batch` | 8 | 15 | 15 | 19 | 17 | 0 | 292.47 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `be0d508647764ab5bac81bda53eb0759:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `be0d508647764ab5bac81bda53eb0759:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `be0d508647764ab5bac81bda53eb0759:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `be0d508647764ab5bac81bda53eb0759:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `be0d508647764ab5bac81bda53eb0759:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | False | True |
| `be0d508647764ab5bac81bda53eb0759:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `be0d508647764ab5bac81bda53eb0759:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | False | True |
| `be0d508647764ab5bac81bda53eb0759:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `be0d508647764ab5bac81bda53eb0759:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | False | True |
| `be0d508647764ab5bac81bda53eb0759:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `be0d508647764ab5bac81bda53eb0759:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | False | True |
| `be0d508647764ab5bac81bda53eb0759:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `be0d508647764ab5bac81bda53eb0759:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | False | True |
| `be0d508647764ab5bac81bda53eb0759:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `be0d508647764ab5bac81bda53eb0759:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `be0d508647764ab5bac81bda53eb0759:batch:1` | 1 | 1 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | to_list ms | scan ms | attach ms | python | native |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `argmax` | 500000 | 5470 | 5 | 8.071 | 9.212 | 126.388 | 3.861 | True | False |
| `argmin` | 500000 | 5470 | 10 | 14.227 | 9.528 | 122.503 | 4.429 | True | False |
| `argmax` | 500000 | 5470 | 20 | 10.453 | 7.620 | 121.589 | 5.598 | True | False |
| `argmin` | 500000 | 5470 | 20 | 10.836 | 7.715 | 147.199 | 4.068 | True | False |
| `argmax` | 500000 | 5470 | 20 | 7.897 | 7.745 | 124.139 | 4.127 | True | False |
| `argmin` | 500000 | 5470 | 20 | 8.808 | 7.714 | 117.819 | 4.926 | True | False |
| `argmax` | 500000 | 5470 | 5 | 9.863 | 7.575 | 141.306 | 3.817 | True | False |
| `argmin` | 500000 | 5470 | 10 | 0.063 | 8.060 | 131.022 | 4.040 | True | False |
