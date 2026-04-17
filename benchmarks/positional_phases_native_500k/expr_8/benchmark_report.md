# Stage Lifecycle Benchmark Report

- run_id: `03f080054efb46fbb1f42d010f2ae3f5`
- benchmark: `positional_phase_expr_8`
- dataset: `minute_2026_03.parquet`
- rows: `500000`
- groups: `5470`
- expressions: `8`
- total_time_sec: `0.545144`
- peak_rss_mb: `311.88`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `03f080054efb46fbb1f42d010f2ae3f5:batch:1` | `ordered_batch` | 8 | 15 | 15 | 19 | 17 | 0 | 311.88 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `03f080054efb46fbb1f42d010f2ae3f5:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `03f080054efb46fbb1f42d010f2ae3f5:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `03f080054efb46fbb1f42d010f2ae3f5:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `03f080054efb46fbb1f42d010f2ae3f5:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `03f080054efb46fbb1f42d010f2ae3f5:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | False | True |
| `03f080054efb46fbb1f42d010f2ae3f5:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `03f080054efb46fbb1f42d010f2ae3f5:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | False | True |
| `03f080054efb46fbb1f42d010f2ae3f5:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `03f080054efb46fbb1f42d010f2ae3f5:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | False | True |
| `03f080054efb46fbb1f42d010f2ae3f5:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `03f080054efb46fbb1f42d010f2ae3f5:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | False | True |
| `03f080054efb46fbb1f42d010f2ae3f5:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `03f080054efb46fbb1f42d010f2ae3f5:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | False | True |
| `03f080054efb46fbb1f42d010f2ae3f5:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `03f080054efb46fbb1f42d010f2ae3f5:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `03f080054efb46fbb1f42d010f2ae3f5:batch:1` | 1 | 1 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | to_list ms | scan ms | attach ms | python | native |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `argmax` | 500000 | 5470 | 5 | 8.966 | 23.385 | 8.491 | 0.063 | False | True |
| `argmin` | 500000 | 5470 | 10 | 9.389 | 21.598 | 8.527 | 0.052 | False | True |
| `argmax` | 500000 | 5470 | 20 | 7.621 | 41.245 | 13.678 | 0.062 | False | True |
| `argmin` | 500000 | 5470 | 20 | 16.059 | 21.476 | 8.090 | 0.059 | False | True |
| `argmax` | 500000 | 5470 | 20 | 8.504 | 21.864 | 8.476 | 0.060 | False | True |
| `argmin` | 500000 | 5470 | 20 | 12.167 | 24.777 | 7.270 | 0.143 | False | True |
| `argmax` | 500000 | 5470 | 5 | 9.845 | 20.529 | 6.810 | 0.056 | False | True |
| `argmin` | 500000 | 5470 | 10 | 0.061 | 20.273 | 8.141 | 0.121 | False | True |
