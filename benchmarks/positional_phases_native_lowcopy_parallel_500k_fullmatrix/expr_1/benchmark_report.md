# Stage Lifecycle Benchmark Report

- run_id: `7e0e80c2ab5b4fba89ef1486198d8d3a`
- benchmark: `positional_phase_expr_1`
- dataset: `minute_2026_03.parquet`
- rows: `500000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `0.111178`
- peak_rss_mb: `207.66`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `7e0e80c2ab5b4fba89ef1486198d8d3a:batch:1` | `ordered_batch` | 1 | 2 | 2 | 12 | 10 | 0 | 207.64 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `7e0e80c2ab5b4fba89ef1486198d8d3a:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `7e0e80c2ab5b4fba89ef1486198d8d3a:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `7e0e80c2ab5b4fba89ef1486198d8d3a:batch:1` | 0 | 0 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 500000 | 5470 | 5 | 12.535 | 3.396 | 7.246 | 0.323 | False | True | True | True |
