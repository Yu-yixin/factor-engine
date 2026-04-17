# Stage Lifecycle Benchmark Report

- run_id: `2e5551b76d8c4dad8b89328280f018c7`
- benchmark: `m1_frame_pressure_4`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `4`
- total_time_sec: `0.044243`
- peak_rss_mb: `68.88`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `2e5551b76d8c4dad8b89328280f018c7:batch:1` | `ordered_batch` | 4 | 11 | 0 | 17 | 11 | 0 | 17 | 11 | 4 | 20800 | 68.87 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `2e5551b76d8c4dad8b89328280f018c7:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `2e5551b76d8c4dad8b89328280f018c7:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `2e5551b76d8c4dad8b89328280f018c7:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | True | False |
| `2e5551b76d8c4dad8b89328280f018c7:batch:1:stage:4` | `materialized_child` | `_____stage_value` | 1 | True | False |
| `2e5551b76d8c4dad8b89328280f018c7:batch:1:stage:5` | `materialized_result` | `______stage_value` | 1 | True | False |
| `2e5551b76d8c4dad8b89328280f018c7:batch:1:stage:6` | `ordered_helper` | `_______stage_value` | 1 | True | False |
| `2e5551b76d8c4dad8b89328280f018c7:batch:1:stage:7` | `ordered_helper` | `________stage_value` | 1 | True | False |
| `2e5551b76d8c4dad8b89328280f018c7:batch:1:stage:8` | `staged_prefix` | `_________stage_value` | 1 | True | False |
| `2e5551b76d8c4dad8b89328280f018c7:batch:1:stage:9` | `staged_prefix` | `__________stage_value` | 1 | True | False |
| `2e5551b76d8c4dad8b89328280f018c7:batch:1:stage:10` | `staged_prefix` | `___________stage_value` | 1 | True | False |
| `2e5551b76d8c4dad8b89328280f018c7:batch:1:stage:11` | `staged_prefix` | `____________stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `2e5551b76d8c4dad8b89328280f018c7:batch:1` | 0 | 0 | 0 | 7 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `frame_04` | `___stage_value` | 10 | 37 | 37 | False | False |
| `frame_03` | `______stage_value` | 20 | 38 | 38 | False | False |
| `frame_01` | `__________stage_value` | 34 | 39 | 39 | False | False |
| `frame_02` | `____________stage_value` | 36 | 40 | 40 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `2e5551b76d8c4dad8b89328280f018c7:batch:1:native_buffer:1` | `frame_04` | 20800 | 4 | 5 | 6 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 2560 | 32 | 8 | 1.748 | 0.619 | 0.168 | 0.158 | False | True | True | True |
