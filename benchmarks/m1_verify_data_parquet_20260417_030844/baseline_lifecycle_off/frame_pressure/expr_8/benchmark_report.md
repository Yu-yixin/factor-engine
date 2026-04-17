# Stage Lifecycle Benchmark Report

- run_id: `ed2673e50fcd467cb4d2900f00d8b566`
- benchmark: `m1_frame_pressure_8`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `8`
- total_time_sec: `35.768043`
- peak_rss_mb: `21678.54`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1` | `ordered_batch` | 8 | 20 | 0 | 29 | 20 | 0 | 29 | 20 | 8 | 236020517 | 21678.53 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:6` | `materialized_child` | `_______stage_value` | 2 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:7` | `materialized_result` | `________stage_value` | 1 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:8` | `materialized_result` | `_________stage_value` | 1 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:9` | `ordered_helper` | `__________stage_value` | 1 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:10` | `ordered_helper` | `___________stage_value` | 1 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:11` | `ordered_helper` | `____________stage_value` | 1 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:12` | `ordered_helper` | `_____________stage_value` | 1 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:13` | `staged_prefix` | `______________stage_value` | 1 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:14` | `staged_prefix` | `_______________stage_value` | 1 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:15` | `staged_prefix` | `________________stage_value` | 1 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:16` | `staged_prefix` | `_________________stage_value` | 1 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:17` | `staged_prefix` | `__________________stage_value` | 1 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:18` | `staged_prefix` | `___________________stage_value` | 1 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:19` | `staged_prefix` | `____________________stage_value` | 1 | True | False |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:stage:20` | `staged_prefix` | `_____________________stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1` | 2 | 2 | 0 | 12 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `frame_04` | `___stage_value` | 10 | 69 | 69 | False | False |
| `frame_08` | `_____stage_value` | 20 | 70 | 70 | False | False |
| `frame_03` | `________stage_value` | 30 | 71 | 71 | False | False |
| `frame_07` | `_________stage_value` | 36 | 72 | 72 | False | False |
| `frame_01` | `_______________stage_value` | 62 | 73 | 73 | False | False |
| `frame_02` | `_________________stage_value` | 64 | 74 | 74 | False | False |
| `frame_05` | `___________________stage_value` | 66 | 75 | 75 | False | False |
| `frame_06` | `_____________________stage_value` | 68 | 76 | 76 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:native_buffer:1` | `frame_04` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `ed2673e50fcd467cb4d2900f00d8b566:batch:1:native_buffer:2` | `frame_08` | 236020517 | 14 | 15 | 16 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 8 | 650.148 | 163.340 | 453.088 | 0.777 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 6 | 641.435 | 158.512 | 294.610 | 0.660 | False | True | True | True |
