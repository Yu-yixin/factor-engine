# Stage Lifecycle Benchmark Report

- run_id: `f88a8e7604234b6eb00e583e069fca99`
- benchmark: `positional_phase_expr_1`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `11.398303`
- peak_rss_mb: `5632.33`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `f88a8e7604234b6eb00e583e069fca99:batch:1` | `ordered_batch` | 1 | 2 | 2 | 12 | 10 | 0 | 5632.33 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `f88a8e7604234b6eb00e583e069fca99:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `f88a8e7604234b6eb00e583e069fca99:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `f88a8e7604234b6eb00e583e069fca99:batch:1` | 0 | 0 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | to_list ms | scan ms | attach ms | python | native |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 548.383 | 1519.572 | 580.253 | 0.145 | False | True |
