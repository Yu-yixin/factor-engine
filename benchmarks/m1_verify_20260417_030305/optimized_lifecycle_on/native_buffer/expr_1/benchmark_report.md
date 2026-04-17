# Stage Lifecycle Benchmark Report

- run_id: `c09de0b8d38545c98f6fe64135a31c4d`
- benchmark: `m1_native_buffer_1`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `1`
- total_time_sec: `0.021529`
- peak_rss_mb: `72.25`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `c09de0b8d38545c98f6fe64135a31c4d:batch:1` | `ordered_batch` | 1 | 2 | 2 | 8 | 2 | 0 | 6 | 0 | 1 | 20800 | 72.25 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `c09de0b8d38545c98f6fe64135a31c4d:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `c09de0b8d38545c98f6fe64135a31c4d:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `c09de0b8d38545c98f6fe64135a31c4d:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pos_01_argmax_5_5` | `___stage_value` | 10 | 13 | 13 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `c09de0b8d38545c98f6fe64135a31c4d:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 20800 | 4 | 5 | 6 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 2560 | 32 | 5 | 2.392 | 0.510 | 0.236 | 0.178 | False | True | True | True |
