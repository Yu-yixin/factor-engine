# Stage Lifecycle Benchmark Report

- run_id: `37fcefdb0e204aef866136308d5b3cba`
- benchmark: `m1_output_retention_4`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `4`
- total_time_sec: `0.042796`
- peak_rss_mb: `63.23`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `37fcefdb0e204aef866136308d5b3cba:batch:1` | `ordered_batch` | 4 | 6 | 6 | 11 | 5 | 0 | 6 | 0 | 4 | 20800 | 63.20 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `37fcefdb0e204aef866136308d5b3cba:batch:1:stage:1` | `materialized_child` | `__stage_value` | 2 | False | True |
| `37fcefdb0e204aef866136308d5b3cba:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `37fcefdb0e204aef866136308d5b3cba:batch:1:stage:3` | `materialized_child` | `____stage_value` | 2 | False | True |
| `37fcefdb0e204aef866136308d5b3cba:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `37fcefdb0e204aef866136308d5b3cba:batch:1:stage:5` | `positional_result` | `______stage_value` | 1 | False | True |
| `37fcefdb0e204aef866136308d5b3cba:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `37fcefdb0e204aef866136308d5b3cba:batch:1` | 2 | 2 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `out_01` | `___stage_value` | 10 | 43 | 43 | False | False |
| `out_02` | `_____stage_value` | 20 | 44 | 44 | False | False |
| `out_03` | `______stage_value` | 28 | 45 | 45 | False | False |
| `out_04` | `_______stage_value` | 37 | 46 | 46 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `37fcefdb0e204aef866136308d5b3cba:batch:1:native_buffer:1` | `out_01` | 20800 | 4 | 5 | 6 | 0 | True | 8 |
| `37fcefdb0e204aef866136308d5b3cba:batch:1:native_buffer:2` | `out_02` | 20800 | 14 | 15 | 16 | 0 | True | 8 |
| `37fcefdb0e204aef866136308d5b3cba:batch:1:native_buffer:3` | `out_03` | 20800 | 22 | 23 | 24 | 0 | True | 8 |
| `37fcefdb0e204aef866136308d5b3cba:batch:1:native_buffer:4` | `out_04` | 20800 | 31 | 32 | 33 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 2560 | 32 | 4 | 1.485 | 0.496 | 0.111 | 0.129 | False | True | True | True |
| `argmin` | 2560 | 32 | 5 | 1.573 | 0.685 | 0.137 | 0.112 | False | True | True | True |
| `argmax` | 2560 | 32 | 6 | 0.019 | 0.322 | 0.172 | 0.146 | False | True | True | True |
| `argmin` | 2560 | 32 | 7 | 0.056 | 0.298 | 0.114 | 0.120 | False | True | True | True |
