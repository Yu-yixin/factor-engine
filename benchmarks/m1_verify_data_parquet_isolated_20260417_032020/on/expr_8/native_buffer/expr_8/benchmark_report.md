# Stage Lifecycle Benchmark Report

- run_id: `4294e5897b6441b09c08e046c56a2fd0`
- benchmark: `m1_native_buffer_8`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `8`
- total_time_sec: `24.451340`
- peak_rss_mb: `20157.99`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1` | `ordered_batch` | 8 | 15 | 15 | 18 | 9 | 0 | 9 | 0 | 8 | 236020517 | 20157.99 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | False | True |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | False | True |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | False | True |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | False | True |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | False | True |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1` | 1 | 1 | 0 | 0 |

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
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:native_buffer:2` | `pos_02_argmin_10_10` | 236020517 | 15 | 16 | 17 | 0 | True | 8 |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:native_buffer:3` | `pos_03_argmax_20_20` | 236020517 | 26 | 27 | 28 | 0 | True | 8 |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:native_buffer:4` | `pos_04_argmin_30_20` | 236020517 | 36 | 37 | 38 | 0 | True | 8 |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:native_buffer:5` | `pos_05_argmax_40_20` | 236020517 | 47 | 48 | 49 | 0 | True | 8 |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:native_buffer:6` | `pos_06_argmin_60_20` | 236020517 | 58 | 59 | 60 | 0 | True | 8 |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:native_buffer:7` | `pos_07_argmax_20_5` | 236020517 | 69 | 70 | 71 | 0 | True | 8 |
| `4294e5897b6441b09c08e046c56a2fd0:batch:1:native_buffer:8` | `pos_08_argmin_20_10` | 236020517 | 78 | 79 | 80 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 528.767 | 199.036 | 478.043 | 1.059 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 461.401 | 550.025 | 421.852 | 0.531 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 20 | 442.449 | 164.793 | 485.755 | 0.819 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 288.764 | 175.800 | 337.666 | 0.610 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 20 | 403.530 | 223.891 | 413.757 | 0.443 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 552.268 | 193.649 | 628.264 | 0.620 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 5 | 584.770 | 203.693 | 675.640 | 0.478 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 0.088 | 203.217 | 410.140 | 0.564 | False | True | True | True |
