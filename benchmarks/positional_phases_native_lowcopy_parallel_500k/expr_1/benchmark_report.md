# Stage Lifecycle Benchmark Report

- run_id: `0bcce730f12d4260ad78f1c0e9c9e9ad`
- benchmark: `positional_phase_expr_1`
- dataset: `minute_2026_03.parquet`
- rows: `500000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `0.174705`
- peak_rss_mb: `212.49`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0bcce730f12d4260ad78f1c0e9c9e9ad:batch:1` | `ordered_batch` | 1 | 2 | 2 | 12 | 10 | 0 | 212.44 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `0bcce730f12d4260ad78f1c0e9c9e9ad:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `0bcce730f12d4260ad78f1c0e9c9e9ad:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `0bcce730f12d4260ad78f1c0e9c9e9ad:batch:1` | 0 | 0 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 500000 | 5470 | 5 | 13.046 | 14.071 | 30.665 | 0.354 | False | True | True | True |
