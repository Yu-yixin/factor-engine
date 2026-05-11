# Stage Lifecycle Benchmark Report

- run_id: `9cea29ec1e8b4c638d49d74558af981e`
- benchmark: `positional_phase_expr_1`
- dataset: `minute_2026_03.parquet`
- rows: `500000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `0.127759`
- peak_rss_mb: `204.11`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `9cea29ec1e8b4c638d49d74558af981e:batch:1` | `ordered_batch` | 1 | 2 | 2 | 12 | 10 | 0 | 204.11 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `9cea29ec1e8b4c638d49d74558af981e:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `9cea29ec1e8b4c638d49d74558af981e:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `9cea29ec1e8b4c638d49d74558af981e:batch:1` | 0 | 0 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | to_list ms | scan ms | attach ms | python | native |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `argmax` | 500000 | 5470 | 5 | 11.903 | 24.238 | 8.495 | 0.122 | False | True |
