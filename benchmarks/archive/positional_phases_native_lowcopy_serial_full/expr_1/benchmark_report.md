# Stage Lifecycle Benchmark Report

- run_id: `cf71d47d3bb84b30a77a974542252674`
- benchmark: `positional_phase_expr_1`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `9.450280`
- peak_rss_mb: `5728.92`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `cf71d47d3bb84b30a77a974542252674:batch:1` | `ordered_batch` | 1 | 2 | 2 | 12 | 10 | 0 | 5728.92 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `cf71d47d3bb84b30a77a974542252674:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `cf71d47d3bb84b30a77a974542252674:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `cf71d47d3bb84b30a77a974542252674:batch:1` | 0 | 0 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 594.625 | 197.599 | 768.188 | 0.526 | False | True | True | False |
