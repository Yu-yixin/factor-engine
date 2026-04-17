# Stage Lifecycle Benchmark Report

- run_id: `e2d8f6a3b8894501a0bbb9dc69c86a5d`
- benchmark: `m1_native_buffer_2`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `2`
- total_time_sec: `0.030514`
- peak_rss_mb: `72.32`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `e2d8f6a3b8894501a0bbb9dc69c86a5d:batch:1` | `ordered_batch` | 2 | 4 | 0 | 10 | 4 | 0 | 10 | 4 | 2 | 20800 | 72.30 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `e2d8f6a3b8894501a0bbb9dc69c86a5d:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `e2d8f6a3b8894501a0bbb9dc69c86a5d:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `e2d8f6a3b8894501a0bbb9dc69c86a5d:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | True | False |
| `e2d8f6a3b8894501a0bbb9dc69c86a5d:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `e2d8f6a3b8894501a0bbb9dc69c86a5d:batch:1` | 0 | 0 | 0 | 4 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pos_01_argmax_5_5` | `___stage_value` | 10 | 21 | 21 | False | False |
| `pos_02_argmin_10_10` | `_____stage_value` | 20 | 22 | 22 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `e2d8f6a3b8894501a0bbb9dc69c86a5d:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 20800 | 4 | 5 | 6 | 0 | True | 8 |
| `e2d8f6a3b8894501a0bbb9dc69c86a5d:batch:1:native_buffer:2` | `pos_02_argmin_10_10` | 20800 | 14 | 15 | 16 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 2560 | 32 | 5 | 2.068 | 2.240 | 0.123 | 0.123 | False | True | True | True |
| `argmin` | 2560 | 32 | 10 | 2.192 | 0.525 | 0.126 | 0.102 | False | True | True | True |
