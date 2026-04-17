# Stage Lifecycle Benchmark Report

- run_id: `2f1600c8b1d54abf945b1917dea2ddad`
- benchmark: `m1_native_buffer_4`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `4`
- total_time_sec: `0.044769`
- peak_rss_mb: `73.38`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `2f1600c8b1d54abf945b1917dea2ddad:batch:1` | `ordered_batch` | 4 | 8 | 0 | 14 | 8 | 0 | 14 | 8 | 4 | 20800 | 73.35 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `2f1600c8b1d54abf945b1917dea2ddad:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `2f1600c8b1d54abf945b1917dea2ddad:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `2f1600c8b1d54abf945b1917dea2ddad:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | True | False |
| `2f1600c8b1d54abf945b1917dea2ddad:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |
| `2f1600c8b1d54abf945b1917dea2ddad:batch:1:stage:5` | `materialized_child` | `______stage_value` | 1 | True | False |
| `2f1600c8b1d54abf945b1917dea2ddad:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | True | False |
| `2f1600c8b1d54abf945b1917dea2ddad:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | True | False |
| `2f1600c8b1d54abf945b1917dea2ddad:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `2f1600c8b1d54abf945b1917dea2ddad:batch:1` | 0 | 0 | 0 | 8 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pos_01_argmax_5_5` | `___stage_value` | 10 | 41 | 41 | False | False |
| `pos_02_argmin_10_10` | `_____stage_value` | 20 | 42 | 42 | False | False |
| `pos_03_argmax_20_20` | `_______stage_value` | 30 | 43 | 43 | False | False |
| `pos_04_argmin_30_20` | `_________stage_value` | 40 | 44 | 44 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `2f1600c8b1d54abf945b1917dea2ddad:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 20800 | 4 | 5 | 6 | 0 | True | 8 |
| `2f1600c8b1d54abf945b1917dea2ddad:batch:1:native_buffer:2` | `pos_02_argmin_10_10` | 20800 | 14 | 15 | 16 | 0 | True | 8 |
| `2f1600c8b1d54abf945b1917dea2ddad:batch:1:native_buffer:3` | `pos_03_argmax_20_20` | 20800 | 24 | 25 | 26 | 0 | True | 8 |
| `2f1600c8b1d54abf945b1917dea2ddad:batch:1:native_buffer:4` | `pos_04_argmin_30_20` | 20800 | 34 | 35 | 36 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 2560 | 32 | 5 | 1.587 | 0.434 | 0.129 | 0.229 | False | True | True | True |
| `argmin` | 2560 | 32 | 10 | 1.731 | 0.612 | 0.122 | 0.126 | False | True | True | True |
| `argmax` | 2560 | 32 | 20 | 1.725 | 0.483 | 0.115 | 0.145 | False | True | True | True |
| `argmin` | 2560 | 32 | 20 | 1.821 | 0.504 | 0.141 | 0.148 | False | True | True | True |
