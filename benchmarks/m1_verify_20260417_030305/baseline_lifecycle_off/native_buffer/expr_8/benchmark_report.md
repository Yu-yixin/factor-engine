# Stage Lifecycle Benchmark Report

- run_id: `d6a0dc90b03a43269d706625875e2a1b`
- benchmark: `m1_native_buffer_8`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `8`
- total_time_sec: `0.079421`
- peak_rss_mb: `75.07`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1` | `ordered_batch` | 8 | 15 | 0 | 21 | 15 | 0 | 21 | 15 | 8 | 20800 | 75.02 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | True | False |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | True | False |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | True | False |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | True | False |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | True | False |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | True | False |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | True | False |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | True | False |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | True | False |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | True | False |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | True | False |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1` | 1 | 1 | 0 | 15 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pos_01_argmax_5_5` | `___stage_value` | 10 | 79 | 79 | False | False |
| `pos_02_argmin_10_10` | `_____stage_value` | 20 | 80 | 80 | False | False |
| `pos_03_argmax_20_20` | `_______stage_value` | 30 | 81 | 81 | False | False |
| `pos_04_argmin_30_20` | `_________stage_value` | 40 | 82 | 82 | False | False |
| `pos_05_argmax_40_20` | `___________stage_value` | 50 | 83 | 83 | False | False |
| `pos_06_argmin_60_20` | `_____________stage_value` | 60 | 84 | 84 | False | False |
| `pos_07_argmax_20_5` | `_______________stage_value` | 70 | 85 | 85 | False | False |
| `pos_08_argmin_20_10` | `________________stage_value` | 78 | 86 | 86 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 20800 | 4 | 5 | 6 | 0 | True | 8 |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:native_buffer:2` | `pos_02_argmin_10_10` | 20800 | 14 | 15 | 16 | 0 | True | 8 |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:native_buffer:3` | `pos_03_argmax_20_20` | 20800 | 24 | 25 | 26 | 0 | True | 8 |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:native_buffer:4` | `pos_04_argmin_30_20` | 20800 | 34 | 35 | 36 | 0 | True | 8 |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:native_buffer:5` | `pos_05_argmax_40_20` | 20800 | 44 | 45 | 46 | 0 | True | 8 |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:native_buffer:6` | `pos_06_argmin_60_20` | 20800 | 54 | 55 | 56 | 0 | True | 8 |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:native_buffer:7` | `pos_07_argmax_20_5` | 20800 | 64 | 65 | 66 | 0 | True | 8 |
| `d6a0dc90b03a43269d706625875e2a1b:batch:1:native_buffer:8` | `pos_08_argmin_20_10` | 20800 | 72 | 73 | 74 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 2560 | 32 | 5 | 2.005 | 0.702 | 0.192 | 0.150 | False | True | True | True |
| `argmin` | 2560 | 32 | 10 | 1.776 | 0.504 | 0.165 | 0.141 | False | True | True | True |
| `argmax` | 2560 | 32 | 20 | 1.813 | 0.501 | 0.104 | 0.113 | False | True | True | True |
| `argmin` | 2560 | 32 | 20 | 1.626 | 0.618 | 0.100 | 0.103 | False | True | True | True |
| `argmax` | 2560 | 32 | 20 | 1.886 | 0.536 | 0.144 | 0.210 | False | True | True | True |
| `argmin` | 2560 | 32 | 20 | 1.643 | 0.491 | 0.146 | 0.131 | False | True | True | True |
| `argmax` | 2560 | 32 | 5 | 1.456 | 0.545 | 0.163 | 0.115 | False | True | True | True |
| `argmin` | 2560 | 32 | 10 | 0.054 | 0.492 | 0.112 | 0.099 | False | True | True | True |
