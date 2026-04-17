# Stage Lifecycle Benchmark Report

- run_id: `9b4925e8d495447196a024e7182366a4`
- benchmark: `positional_phase_expr_1`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `9.288744`
- peak_rss_mb: `5763.41`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `9b4925e8d495447196a024e7182366a4:batch:1` | `ordered_batch` | 1 | 2 | 2 | 12 | 10 | 0 | 5763.40 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `9b4925e8d495447196a024e7182366a4:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `9b4925e8d495447196a024e7182366a4:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `9b4925e8d495447196a024e7182366a4:batch:1` | 0 | 0 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 585.209 | 164.177 | 373.428 | 0.599 | False | True | True | True |
