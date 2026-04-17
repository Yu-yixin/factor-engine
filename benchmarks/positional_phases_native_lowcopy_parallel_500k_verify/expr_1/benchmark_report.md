# Stage Lifecycle Benchmark Report

- run_id: `2735e93d63194fb99178efe9117552a3`
- benchmark: `positional_phase_expr_1`
- dataset: `minute_2026_03.parquet`
- rows: `500000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `0.114362`
- peak_rss_mb: `200.59`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `2735e93d63194fb99178efe9117552a3:batch:1` | `ordered_batch` | 1 | 2 | 2 | 12 | 10 | 0 | 200.57 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `2735e93d63194fb99178efe9117552a3:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `2735e93d63194fb99178efe9117552a3:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `2735e93d63194fb99178efe9117552a3:batch:1` | 0 | 0 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 500000 | 5470 | 5 | 12.723 | 3.796 | 7.354 | 0.295 | False | True | True | True |
