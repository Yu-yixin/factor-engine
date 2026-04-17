# Stage Lifecycle Benchmark Report

- run_id: `516eb18a7ed2452d91c7a3084178375a`
- benchmark: `m1_native_buffer_2`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `2`
- total_time_sec: `0.035693`
- peak_rss_mb: `73.11`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `516eb18a7ed2452d91c7a3084178375a:batch:1` | `ordered_batch` | 2 | 4 | 4 | 9 | 3 | 0 | 6 | 0 | 2 | 20800 | 73.08 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `516eb18a7ed2452d91c7a3084178375a:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `516eb18a7ed2452d91c7a3084178375a:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `516eb18a7ed2452d91c7a3084178375a:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `516eb18a7ed2452d91c7a3084178375a:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `516eb18a7ed2452d91c7a3084178375a:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pos_01_argmax_5_5` | `___stage_value` | 10 | 25 | 25 | False | False |
| `pos_02_argmin_10_10` | `_____stage_value` | 21 | 26 | 26 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `516eb18a7ed2452d91c7a3084178375a:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 20800 | 4 | 5 | 6 | 0 | True | 8 |
| `516eb18a7ed2452d91c7a3084178375a:batch:1:native_buffer:2` | `pos_02_argmin_10_10` | 20800 | 15 | 16 | 17 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 2560 | 32 | 5 | 1.951 | 0.744 | 0.132 | 0.223 | False | True | True | True |
| `argmin` | 2560 | 32 | 10 | 2.209 | 0.339 | 0.183 | 0.132 | False | True | True | True |
