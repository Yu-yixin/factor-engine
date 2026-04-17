# Stage Lifecycle Benchmark Report

- run_id: `40752f2b23ec47549da12066cd691ef4`
- benchmark: `m1_native_buffer_4`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `4`
- total_time_sec: `0.048830`
- peak_rss_mb: `74.29`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `40752f2b23ec47549da12066cd691ef4:batch:1` | `ordered_batch` | 4 | 8 | 8 | 11 | 5 | 0 | 6 | 0 | 4 | 20800 | 73.75 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `40752f2b23ec47549da12066cd691ef4:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `40752f2b23ec47549da12066cd691ef4:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `40752f2b23ec47549da12066cd691ef4:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `40752f2b23ec47549da12066cd691ef4:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `40752f2b23ec47549da12066cd691ef4:batch:1:stage:5` | `materialized_child` | `______stage_value` | 1 | False | True |
| `40752f2b23ec47549da12066cd691ef4:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `40752f2b23ec47549da12066cd691ef4:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | False | True |
| `40752f2b23ec47549da12066cd691ef4:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `40752f2b23ec47549da12066cd691ef4:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pos_01_argmax_5_5` | `___stage_value` | 10 | 49 | 49 | False | False |
| `pos_02_argmin_10_10` | `_____stage_value` | 21 | 50 | 50 | False | False |
| `pos_03_argmax_20_20` | `_______stage_value` | 32 | 51 | 51 | False | False |
| `pos_04_argmin_30_20` | `_________stage_value` | 43 | 52 | 52 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `40752f2b23ec47549da12066cd691ef4:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 20800 | 4 | 5 | 6 | 0 | True | 8 |
| `40752f2b23ec47549da12066cd691ef4:batch:1:native_buffer:2` | `pos_02_argmin_10_10` | 20800 | 15 | 16 | 17 | 0 | True | 8 |
| `40752f2b23ec47549da12066cd691ef4:batch:1:native_buffer:3` | `pos_03_argmax_20_20` | 20800 | 26 | 27 | 28 | 0 | True | 8 |
| `40752f2b23ec47549da12066cd691ef4:batch:1:native_buffer:4` | `pos_04_argmin_30_20` | 20800 | 37 | 38 | 39 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 2560 | 32 | 5 | 2.215 | 0.496 | 0.133 | 0.124 | False | True | True | True |
| `argmin` | 2560 | 32 | 10 | 1.466 | 0.451 | 0.158 | 0.125 | False | True | True | True |
| `argmax` | 2560 | 32 | 20 | 1.635 | 0.320 | 0.181 | 0.114 | False | True | True | True |
| `argmin` | 2560 | 32 | 20 | 1.617 | 0.251 | 0.246 | 0.116 | False | True | True | True |
