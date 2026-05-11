# Stage Lifecycle Benchmark Report

- run_id: `0e29c28045e34b7785e740975c705ea0`
- benchmark: `direction_check_1_v2`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `18.092760`
- peak_rss_mb: `5734.60`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0e29c28045e34b7785e740975c705ea0:batch:1` | `ordered_batch` | 1 | 2 | 2 | 12 | 10 | 0 | 5734.60 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `0e29c28045e34b7785e740975c705ea0:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `0e29c28045e34b7785e740975c705ea0:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |

## Positional Phases

| function | rows | groups | window | child ms | to_list ms | scan ms | attach ms | python kernel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `argmax` | 29048679 | 5495 | 5 | 535.173 | 568.378 | 8218.925 | 438.502 | True |
