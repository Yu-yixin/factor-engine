# Stage Lifecycle Benchmark Report

- run_id: `88e4b8004d4241c1912375101f56648b`
- benchmark: `positional_phase_expr_1`
- dataset: `minute_2026_03.parquet`
- rows: `500000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `0.103179`
- peak_rss_mb: `207.99`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `88e4b8004d4241c1912375101f56648b:batch:1` | `ordered_batch` | 1 | 2 | 2 | 12 | 10 | 0 | 207.97 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `88e4b8004d4241c1912375101f56648b:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `88e4b8004d4241c1912375101f56648b:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `88e4b8004d4241c1912375101f56648b:batch:1` | 0 | 0 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 500000 | 5470 | 5 | 11.656 | 3.607 | 10.934 | 0.355 | False | True | True | False |
