# Stage Lifecycle Benchmark Report

- run_id: `84c501fe6b294189aa4e6db611cc80a6`
- benchmark: `m1_output_retention_1`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `1`
- total_time_sec: `0.018133`
- peak_rss_mb: `59.90`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `84c501fe6b294189aa4e6db611cc80a6:batch:1` | `ordered_batch` | 1 | 2 | 0 | 8 | 2 | 0 | 8 | 2 | 1 | 20800 | 59.89 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `84c501fe6b294189aa4e6db611cc80a6:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `84c501fe6b294189aa4e6db611cc80a6:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `84c501fe6b294189aa4e6db611cc80a6:batch:1` | 0 | 0 | 0 | 2 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `out_01` | `___stage_value` | 10 | 11 | 11 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `84c501fe6b294189aa4e6db611cc80a6:batch:1:native_buffer:1` | `out_01` | 20800 | 4 | 5 | 6 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 2560 | 32 | 4 | 1.407 | 1.103 | 0.573 | 0.207 | False | True | True | True |
