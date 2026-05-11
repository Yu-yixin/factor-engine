# Stage Lifecycle Benchmark Report

- run_id: `0931b3a1122d40aba8065cbd49345f05`
- benchmark: `m1_frame_pressure_4`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `4`
- total_time_sec: `0.077622`
- peak_rss_mb: `69.04`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0931b3a1122d40aba8065cbd49345f05:batch:1` | `ordered_batch` | 4 | 11 | 11 | 14 | 8 | 0 | 6 | 0 | 4 | 20800 | 69.02 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `0931b3a1122d40aba8065cbd49345f05:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `0931b3a1122d40aba8065cbd49345f05:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `0931b3a1122d40aba8065cbd49345f05:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `0931b3a1122d40aba8065cbd49345f05:batch:1:stage:4` | `materialized_child` | `_____stage_value` | 1 | False | True |
| `0931b3a1122d40aba8065cbd49345f05:batch:1:stage:5` | `materialized_result` | `______stage_value` | 1 | False | True |
| `0931b3a1122d40aba8065cbd49345f05:batch:1:stage:6` | `ordered_helper` | `_______stage_value` | 1 | False | True |
| `0931b3a1122d40aba8065cbd49345f05:batch:1:stage:7` | `ordered_helper` | `________stage_value` | 1 | False | True |
| `0931b3a1122d40aba8065cbd49345f05:batch:1:stage:8` | `staged_prefix` | `_________stage_value` | 1 | False | True |
| `0931b3a1122d40aba8065cbd49345f05:batch:1:stage:9` | `staged_prefix` | `__________stage_value` | 1 | False | True |
| `0931b3a1122d40aba8065cbd49345f05:batch:1:stage:10` | `staged_prefix` | `___________stage_value` | 1 | False | True |
| `0931b3a1122d40aba8065cbd49345f05:batch:1:stage:11` | `staged_prefix` | `____________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `0931b3a1122d40aba8065cbd49345f05:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `frame_04` | `___stage_value` | 10 | 48 | 48 | False | False |
| `frame_03` | `______stage_value` | 21 | 49 | 49 | False | False |
| `frame_01` | `__________stage_value` | 37 | 50 | 50 | False | False |
| `frame_02` | `____________stage_value` | 39 | 51 | 51 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `0931b3a1122d40aba8065cbd49345f05:batch:1:native_buffer:1` | `frame_04` | 20800 | 4 | 5 | 6 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 2560 | 32 | 8 | 3.152 | 0.641 | 0.147 | 0.125 | False | True | True | True |
