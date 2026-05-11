# Stage Lifecycle Benchmark Report

- run_id: `3fc8abf9f44d4299a204d40505f3b7a6`
- benchmark: `m1_output_retention_8`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `8`
- total_time_sec: `24.463756`
- peak_rss_mb: `20552.73`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1` | `ordered_batch` | 8 | 10 | 0 | 19 | 10 | 0 | 19 | 10 | 8 | 236020517 | 20552.71 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1:stage:1` | `materialized_child` | `__stage_value` | 3 | True | False |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1:stage:3` | `materialized_child` | `____stage_value` | 5 | True | False |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1:stage:5` | `positional_result` | `______stage_value` | 1 | True | False |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | True | False |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1:stage:7` | `positional_result` | `________stage_value` | 1 | True | False |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | True | False |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1:stage:9` | `positional_result` | `__________stage_value` | 1 | True | False |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1` | 2 | 6 | 0 | 10 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `out_01` | `___stage_value` | 10 | 69 | 69 | False | False |
| `out_02` | `_____stage_value` | 20 | 70 | 70 | False | False |
| `out_03` | `______stage_value` | 28 | 71 | 71 | False | False |
| `out_04` | `_______stage_value` | 36 | 72 | 72 | False | False |
| `out_05` | `________stage_value` | 44 | 73 | 73 | False | False |
| `out_06` | `_________stage_value` | 52 | 74 | 74 | False | False |
| `out_07` | `__________stage_value` | 60 | 75 | 75 | False | False |
| `out_08` | `___________stage_value` | 68 | 76 | 76 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1:native_buffer:1` | `out_01` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1:native_buffer:2` | `out_02` | 236020517 | 14 | 15 | 16 | 0 | True | 8 |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1:native_buffer:3` | `out_03` | 236020517 | 22 | 23 | 24 | 0 | True | 8 |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1:native_buffer:4` | `out_04` | 236020517 | 30 | 31 | 32 | 0 | True | 8 |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1:native_buffer:5` | `out_05` | 236020517 | 38 | 39 | 40 | 0 | True | 8 |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1:native_buffer:6` | `out_06` | 236020517 | 46 | 47 | 48 | 0 | True | 8 |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1:native_buffer:7` | `out_07` | 236020517 | 54 | 55 | 56 | 0 | True | 8 |
| `3fc8abf9f44d4299a204d40505f3b7a6:batch:1:native_buffer:8` | `out_08` | 236020517 | 62 | 63 | 64 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 4 | 4.100 | 247.217 | 619.810 | 1.371 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 5 | 1.178 | 249.607 | 735.950 | 0.658 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 6 | 0.024 | 221.653 | 758.598 | 2.370 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 7 | 0.102 | 235.806 | 443.321 | 0.783 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 8 | 0.039 | 227.345 | 576.438 | 0.475 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 9 | 0.026 | 226.934 | 547.990 | 0.689 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 10 | 0.087 | 189.544 | 834.517 | 1.772 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 4 | 0.024 | 237.729 | 645.972 | 0.575 | False | True | True | True |
