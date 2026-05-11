# Stage Lifecycle Benchmark Report

- run_id: `0947c9f1dfa1470ca9dc3b199f480c28`
- benchmark: `positional_phase_expr_1`
- dataset: `minute_2026_03.parquet`
- rows: `10000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `0.025562`
- peak_rss_mb: `71.52`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0947c9f1dfa1470ca9dc3b199f480c28:batch:1` | `ordered_batch` | 1 | 2 | 2 | 12 | 10 | 0 | 71.52 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `0947c9f1dfa1470ca9dc3b199f480c28:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `0947c9f1dfa1470ca9dc3b199f480c28:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `0947c9f1dfa1470ca9dc3b199f480c28:batch:1` | 0 | 0 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | to_list ms | scan ms | attach ms | python | native |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `argmax` | 10000 | 5470 | 5 | 4.784 | 0.228 | 4.266 | 0.408 | True | False |
