# Stage Lifecycle Benchmark Report

- run_id: `53f4103806504ab8be7f0cac83149240`
- benchmark: `m1_output_retention_8`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `8`
- total_time_sec: `16.947360`
- peak_rss_mb: `10278.78`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `53f4103806504ab8be7f0cac83149240:batch:1` | `ordered_batch` | 8 | 10 | 0 | 19 | 10 | 0 | 19 | 10 | 8 | 236020517 | 10278.75 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `53f4103806504ab8be7f0cac83149240:batch:1:stage:1` | `materialized_child` | `__stage_value` | 3 | True | False |
| `53f4103806504ab8be7f0cac83149240:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `53f4103806504ab8be7f0cac83149240:batch:1:stage:3` | `materialized_child` | `____stage_value` | 5 | True | False |
| `53f4103806504ab8be7f0cac83149240:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |
| `53f4103806504ab8be7f0cac83149240:batch:1:stage:5` | `positional_result` | `______stage_value` | 1 | True | False |
| `53f4103806504ab8be7f0cac83149240:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | True | False |
| `53f4103806504ab8be7f0cac83149240:batch:1:stage:7` | `positional_result` | `________stage_value` | 1 | True | False |
| `53f4103806504ab8be7f0cac83149240:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | True | False |
| `53f4103806504ab8be7f0cac83149240:batch:1:stage:9` | `positional_result` | `__________stage_value` | 1 | True | False |
| `53f4103806504ab8be7f0cac83149240:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `53f4103806504ab8be7f0cac83149240:batch:1` | 2 | 6 | 0 | 10 |

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
| `53f4103806504ab8be7f0cac83149240:batch:1:native_buffer:1` | `out_01` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `53f4103806504ab8be7f0cac83149240:batch:1:native_buffer:2` | `out_02` | 236020517 | 14 | 15 | 16 | 0 | True | 8 |
| `53f4103806504ab8be7f0cac83149240:batch:1:native_buffer:3` | `out_03` | 236020517 | 22 | 23 | 24 | 0 | True | 8 |
| `53f4103806504ab8be7f0cac83149240:batch:1:native_buffer:4` | `out_04` | 236020517 | 30 | 31 | 32 | 0 | True | 8 |
| `53f4103806504ab8be7f0cac83149240:batch:1:native_buffer:5` | `out_05` | 236020517 | 38 | 39 | 40 | 0 | True | 8 |
| `53f4103806504ab8be7f0cac83149240:batch:1:native_buffer:6` | `out_06` | 236020517 | 46 | 47 | 48 | 0 | True | 8 |
| `53f4103806504ab8be7f0cac83149240:batch:1:native_buffer:7` | `out_07` | 236020517 | 54 | 55 | 56 | 0 | True | 8 |
| `53f4103806504ab8be7f0cac83149240:batch:1:native_buffer:8` | `out_08` | 236020517 | 62 | 63 | 64 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 4 | 2.545 | 176.797 | 464.978 | 0.589 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 5 | 1.963 | 171.692 | 510.367 | 0.515 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 6 | 0.034 | 169.556 | 560.306 | 0.593 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 7 | 0.109 | 159.552 | 505.054 | 0.465 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 8 | 0.019 | 178.480 | 478.223 | 0.474 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 9 | 0.047 | 174.813 | 363.832 | 0.404 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 10 | 0.065 | 182.557 | 482.714 | 0.630 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 4 | 0.022 | 254.235 | 431.520 | 0.657 | False | True | True | True |
