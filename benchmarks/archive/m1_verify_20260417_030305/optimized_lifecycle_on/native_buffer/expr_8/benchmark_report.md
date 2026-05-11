# Stage Lifecycle Benchmark Report

- run_id: `e088934292b24a6fbde87657c304dd1d`
- benchmark: `m1_native_buffer_8`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `8`
- total_time_sec: `0.090445`
- peak_rss_mb: `75.87`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `e088934292b24a6fbde87657c304dd1d:batch:1` | `ordered_batch` | 8 | 15 | 15 | 15 | 9 | 0 | 6 | 0 | 8 | 20800 | 75.81 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `e088934292b24a6fbde87657c304dd1d:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `e088934292b24a6fbde87657c304dd1d:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `e088934292b24a6fbde87657c304dd1d:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `e088934292b24a6fbde87657c304dd1d:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `e088934292b24a6fbde87657c304dd1d:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | False | True |
| `e088934292b24a6fbde87657c304dd1d:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `e088934292b24a6fbde87657c304dd1d:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | False | True |
| `e088934292b24a6fbde87657c304dd1d:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `e088934292b24a6fbde87657c304dd1d:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | False | True |
| `e088934292b24a6fbde87657c304dd1d:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `e088934292b24a6fbde87657c304dd1d:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | False | True |
| `e088934292b24a6fbde87657c304dd1d:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `e088934292b24a6fbde87657c304dd1d:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | False | True |
| `e088934292b24a6fbde87657c304dd1d:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `e088934292b24a6fbde87657c304dd1d:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `e088934292b24a6fbde87657c304dd1d:batch:1` | 1 | 1 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pos_01_argmax_5_5` | `___stage_value` | 10 | 94 | 94 | False | False |
| `pos_02_argmin_10_10` | `_____stage_value` | 21 | 95 | 95 | False | False |
| `pos_03_argmax_20_20` | `_______stage_value` | 32 | 96 | 96 | False | False |
| `pos_04_argmin_30_20` | `_________stage_value` | 42 | 97 | 97 | False | False |
| `pos_05_argmax_40_20` | `___________stage_value` | 53 | 98 | 98 | False | False |
| `pos_06_argmin_60_20` | `_____________stage_value` | 64 | 99 | 99 | False | False |
| `pos_07_argmax_20_5` | `_______________stage_value` | 75 | 100 | 100 | False | False |
| `pos_08_argmin_20_10` | `________________stage_value` | 84 | 101 | 101 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `e088934292b24a6fbde87657c304dd1d:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 20800 | 4 | 5 | 6 | 0 | True | 8 |
| `e088934292b24a6fbde87657c304dd1d:batch:1:native_buffer:2` | `pos_02_argmin_10_10` | 20800 | 15 | 16 | 17 | 0 | True | 8 |
| `e088934292b24a6fbde87657c304dd1d:batch:1:native_buffer:3` | `pos_03_argmax_20_20` | 20800 | 26 | 27 | 28 | 0 | True | 8 |
| `e088934292b24a6fbde87657c304dd1d:batch:1:native_buffer:4` | `pos_04_argmin_30_20` | 20800 | 36 | 37 | 38 | 0 | True | 8 |
| `e088934292b24a6fbde87657c304dd1d:batch:1:native_buffer:5` | `pos_05_argmax_40_20` | 20800 | 47 | 48 | 49 | 0 | True | 8 |
| `e088934292b24a6fbde87657c304dd1d:batch:1:native_buffer:6` | `pos_06_argmin_60_20` | 20800 | 58 | 59 | 60 | 0 | True | 8 |
| `e088934292b24a6fbde87657c304dd1d:batch:1:native_buffer:7` | `pos_07_argmax_20_5` | 20800 | 69 | 70 | 71 | 0 | True | 8 |
| `e088934292b24a6fbde87657c304dd1d:batch:1:native_buffer:8` | `pos_08_argmin_20_10` | 20800 | 78 | 79 | 80 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 2560 | 32 | 5 | 1.833 | 0.678 | 0.139 | 0.117 | False | True | True | True |
| `argmin` | 2560 | 32 | 10 | 1.546 | 0.273 | 0.262 | 0.109 | False | True | True | True |
| `argmax` | 2560 | 32 | 20 | 1.538 | 0.235 | 0.086 | 0.107 | False | True | True | True |
| `argmin` | 2560 | 32 | 20 | 1.602 | 0.240 | 0.110 | 0.101 | False | True | True | True |
| `argmax` | 2560 | 32 | 20 | 1.656 | 0.336 | 0.145 | 0.106 | False | True | True | True |
| `argmin` | 2560 | 32 | 20 | 1.637 | 0.397 | 0.137 | 0.132 | False | True | True | True |
| `argmax` | 2560 | 32 | 5 | 2.837 | 0.390 | 0.151 | 0.215 | False | True | True | True |
| `argmin` | 2560 | 32 | 10 | 0.094 | 0.407 | 0.127 | 0.122 | False | True | True | True |
