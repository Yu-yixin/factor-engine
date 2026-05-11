# Stage Lifecycle Benchmark Report

- run_id: `2ac6ce84323747dfb0b4b92512343da0`
- benchmark: `m1_output_retention_1`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `10.298963`
- peak_rss_mb: `7329.42`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `2ac6ce84323747dfb0b4b92512343da0:batch:1` | `ordered_batch` | 1 | 2 | 0 | 11 | 2 | 0 | 11 | 2 | 1 | 236020517 | 7329.41 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `2ac6ce84323747dfb0b4b92512343da0:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `2ac6ce84323747dfb0b4b92512343da0:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `2ac6ce84323747dfb0b4b92512343da0:batch:1` | 0 | 0 | 0 | 2 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `out_01` | `___stage_value` | 10 | 11 | 11 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `2ac6ce84323747dfb0b4b92512343da0:batch:1:native_buffer:1` | `out_01` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 4 | 2.911 | 207.928 | 640.969 | 0.923 | False | True | True | True |
