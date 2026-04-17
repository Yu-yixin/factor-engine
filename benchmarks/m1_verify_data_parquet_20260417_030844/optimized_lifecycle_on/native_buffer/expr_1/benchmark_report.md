# Stage Lifecycle Benchmark Report

- run_id: `8c1a7e7113d046b698d2f2fa3d3ceeb9`
- benchmark: `m1_native_buffer_1`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `9.903377`
- peak_rss_mb: `21774.24`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `8c1a7e7113d046b698d2f2fa3d3ceeb9:batch:1` | `ordered_batch` | 1 | 2 | 2 | 11 | 2 | 0 | 9 | 0 | 1 | 236020517 | 21774.23 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `8c1a7e7113d046b698d2f2fa3d3ceeb9:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `8c1a7e7113d046b698d2f2fa3d3ceeb9:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `8c1a7e7113d046b698d2f2fa3d3ceeb9:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pos_01_argmax_5_5` | `___stage_value` | 10 | 13 | 13 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `8c1a7e7113d046b698d2f2fa3d3ceeb9:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 531.086 | 263.210 | 395.796 | 0.498 | False | True | True | True |
