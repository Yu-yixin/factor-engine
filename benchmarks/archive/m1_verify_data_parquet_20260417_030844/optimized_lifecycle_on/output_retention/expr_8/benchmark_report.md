# Stage Lifecycle Benchmark Report

- run_id: `8d0699a769784944862eb42ee1dc86fd`
- benchmark: `m1_output_retention_8`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `8`
- total_time_sec: `20.565877`
- peak_rss_mb: `22190.41`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `8d0699a769784944862eb42ee1dc86fd:batch:1` | `ordered_batch` | 8 | 10 | 10 | 18 | 9 | 0 | 9 | 0 | 8 | 236020517 | 22190.41 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `8d0699a769784944862eb42ee1dc86fd:batch:1:stage:1` | `materialized_child` | `__stage_value` | 3 | False | True |
| `8d0699a769784944862eb42ee1dc86fd:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `8d0699a769784944862eb42ee1dc86fd:batch:1:stage:3` | `materialized_child` | `____stage_value` | 5 | False | True |
| `8d0699a769784944862eb42ee1dc86fd:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `8d0699a769784944862eb42ee1dc86fd:batch:1:stage:5` | `positional_result` | `______stage_value` | 1 | False | True |
| `8d0699a769784944862eb42ee1dc86fd:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `8d0699a769784944862eb42ee1dc86fd:batch:1:stage:7` | `positional_result` | `________stage_value` | 1 | False | True |
| `8d0699a769784944862eb42ee1dc86fd:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `8d0699a769784944862eb42ee1dc86fd:batch:1:stage:9` | `positional_result` | `__________stage_value` | 1 | False | True |
| `8d0699a769784944862eb42ee1dc86fd:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `8d0699a769784944862eb42ee1dc86fd:batch:1` | 2 | 6 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `out_01` | `___stage_value` | 10 | 79 | 79 | False | False |
| `out_02` | `_____stage_value` | 20 | 80 | 80 | False | False |
| `out_03` | `______stage_value` | 28 | 81 | 81 | False | False |
| `out_04` | `_______stage_value` | 36 | 82 | 82 | False | False |
| `out_05` | `________stage_value` | 44 | 83 | 83 | False | False |
| `out_06` | `_________stage_value` | 52 | 84 | 84 | False | False |
| `out_07` | `__________stage_value` | 60 | 85 | 85 | False | False |
| `out_08` | `___________stage_value` | 69 | 86 | 86 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `8d0699a769784944862eb42ee1dc86fd:batch:1:native_buffer:1` | `out_01` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `8d0699a769784944862eb42ee1dc86fd:batch:1:native_buffer:2` | `out_02` | 236020517 | 14 | 15 | 16 | 0 | True | 8 |
| `8d0699a769784944862eb42ee1dc86fd:batch:1:native_buffer:3` | `out_03` | 236020517 | 22 | 23 | 24 | 0 | True | 8 |
| `8d0699a769784944862eb42ee1dc86fd:batch:1:native_buffer:4` | `out_04` | 236020517 | 30 | 31 | 32 | 0 | True | 8 |
| `8d0699a769784944862eb42ee1dc86fd:batch:1:native_buffer:5` | `out_05` | 236020517 | 38 | 39 | 40 | 0 | True | 8 |
| `8d0699a769784944862eb42ee1dc86fd:batch:1:native_buffer:6` | `out_06` | 236020517 | 46 | 47 | 48 | 0 | True | 8 |
| `8d0699a769784944862eb42ee1dc86fd:batch:1:native_buffer:7` | `out_07` | 236020517 | 54 | 55 | 56 | 0 | True | 8 |
| `8d0699a769784944862eb42ee1dc86fd:batch:1:native_buffer:8` | `out_08` | 236020517 | 63 | 64 | 65 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 4 | 3.334 | 222.434 | 454.738 | 0.685 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 5 | 2.300 | 179.470 | 442.833 | 0.620 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 6 | 0.021 | 162.450 | 430.183 | 0.650 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 7 | 0.060 | 189.785 | 534.097 | 0.439 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 8 | 0.021 | 238.397 | 348.461 | 0.461 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 9 | 0.019 | 228.313 | 341.682 | 0.512 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 10 | 0.061 | 157.986 | 383.601 | 0.420 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 4 | 0.018 | 155.543 | 307.847 | 0.390 | False | True | True | True |
