# Stage Lifecycle Benchmark Report

- run_id: `6406d2ce6202451f8f3f9cb2d956b489`
- benchmark: `m1_output_retention_8`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `8`
- total_time_sec: `0.063979`
- peak_rss_mb: `65.06`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1` | `ordered_batch` | 8 | 10 | 0 | 16 | 10 | 0 | 16 | 10 | 8 | 20800 | 65.00 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1:stage:1` | `materialized_child` | `__stage_value` | 3 | True | False |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1:stage:3` | `materialized_child` | `____stage_value` | 5 | True | False |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1:stage:5` | `positional_result` | `______stage_value` | 1 | True | False |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | True | False |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1:stage:7` | `positional_result` | `________stage_value` | 1 | True | False |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | True | False |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1:stage:9` | `positional_result` | `__________stage_value` | 1 | True | False |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1` | 2 | 6 | 0 | 10 |

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
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1:native_buffer:1` | `out_01` | 20800 | 4 | 5 | 6 | 0 | True | 8 |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1:native_buffer:2` | `out_02` | 20800 | 14 | 15 | 16 | 0 | True | 8 |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1:native_buffer:3` | `out_03` | 20800 | 22 | 23 | 24 | 0 | True | 8 |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1:native_buffer:4` | `out_04` | 20800 | 30 | 31 | 32 | 0 | True | 8 |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1:native_buffer:5` | `out_05` | 20800 | 38 | 39 | 40 | 0 | True | 8 |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1:native_buffer:6` | `out_06` | 20800 | 46 | 47 | 48 | 0 | True | 8 |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1:native_buffer:7` | `out_07` | 20800 | 54 | 55 | 56 | 0 | True | 8 |
| `6406d2ce6202451f8f3f9cb2d956b489:batch:1:native_buffer:8` | `out_08` | 20800 | 62 | 63 | 64 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 2560 | 32 | 4 | 1.313 | 0.611 | 0.143 | 0.160 | False | True | True | True |
| `argmin` | 2560 | 32 | 5 | 1.478 | 0.429 | 0.115 | 0.119 | False | True | True | True |
| `argmax` | 2560 | 32 | 6 | 0.020 | 0.272 | 0.129 | 0.097 | False | True | True | True |
| `argmin` | 2560 | 32 | 7 | 0.062 | 0.381 | 0.102 | 0.180 | False | True | True | True |
| `argmax` | 2560 | 32 | 8 | 0.018 | 0.415 | 0.128 | 0.120 | False | True | True | True |
| `argmin` | 2560 | 32 | 9 | 0.016 | 0.311 | 0.168 | 0.111 | False | True | True | True |
| `argmax` | 2560 | 32 | 10 | 0.052 | 0.337 | 0.133 | 0.116 | False | True | True | True |
| `argmin` | 2560 | 32 | 4 | 0.024 | 0.265 | 0.116 | 0.113 | False | True | True | True |
