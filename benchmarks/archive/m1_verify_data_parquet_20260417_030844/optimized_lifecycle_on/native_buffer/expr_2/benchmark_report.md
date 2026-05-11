# Stage Lifecycle Benchmark Report

- run_id: `6d6b47a06c1c40e68f26a2faa52f05a4`
- benchmark: `m1_native_buffer_2`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `2`
- total_time_sec: `11.387769`
- peak_rss_mb: `21581.11`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `6d6b47a06c1c40e68f26a2faa52f05a4:batch:1` | `ordered_batch` | 2 | 4 | 4 | 12 | 3 | 0 | 9 | 0 | 2 | 236020517 | 21581.11 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `6d6b47a06c1c40e68f26a2faa52f05a4:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `6d6b47a06c1c40e68f26a2faa52f05a4:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `6d6b47a06c1c40e68f26a2faa52f05a4:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `6d6b47a06c1c40e68f26a2faa52f05a4:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `6d6b47a06c1c40e68f26a2faa52f05a4:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pos_01_argmax_5_5` | `___stage_value` | 10 | 25 | 25 | False | False |
| `pos_02_argmin_10_10` | `_____stage_value` | 21 | 26 | 26 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `6d6b47a06c1c40e68f26a2faa52f05a4:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `6d6b47a06c1c40e68f26a2faa52f05a4:batch:1:native_buffer:2` | `pos_02_argmin_10_10` | 236020517 | 15 | 16 | 17 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 552.655 | 164.896 | 389.108 | 0.429 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 589.103 | 153.824 | 459.227 | 0.560 | False | True | True | True |
