# Stage Lifecycle Benchmark Report

- run_id: `67b57d5f78814766ba67a8adfab70904`
- benchmark: `positional_phase_expr_1`
- dataset: `minute_2026_03.parquet`
- rows: `500000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `0.286071`
- peak_rss_mb: `207.23`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `67b57d5f78814766ba67a8adfab70904:batch:1` | `ordered_batch` | 1 | 2 | 2 | 12 | 10 | 0 | 207.23 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `67b57d5f78814766ba67a8adfab70904:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `67b57d5f78814766ba67a8adfab70904:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `67b57d5f78814766ba67a8adfab70904:batch:1` | 0 | 0 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | to_list ms | scan ms | attach ms | python | native |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `argmax` | 500000 | 5470 | 5 | 9.895 | 9.326 | 162.397 | 4.158 | True | False |
