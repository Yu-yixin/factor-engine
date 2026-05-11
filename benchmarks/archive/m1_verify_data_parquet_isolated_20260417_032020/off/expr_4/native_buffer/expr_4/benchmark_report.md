# Stage Lifecycle Benchmark Report

- run_id: `10edfd136a824da68bf9a2443fa31d54`
- benchmark: `m1_native_buffer_4`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `4`
- total_time_sec: `14.202545`
- peak_rss_mb: `17025.39`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `10edfd136a824da68bf9a2443fa31d54:batch:1` | `ordered_batch` | 4 | 8 | 0 | 17 | 8 | 0 | 17 | 8 | 4 | 236020517 | 17025.37 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `10edfd136a824da68bf9a2443fa31d54:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `10edfd136a824da68bf9a2443fa31d54:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `10edfd136a824da68bf9a2443fa31d54:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | True | False |
| `10edfd136a824da68bf9a2443fa31d54:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |
| `10edfd136a824da68bf9a2443fa31d54:batch:1:stage:5` | `materialized_child` | `______stage_value` | 1 | True | False |
| `10edfd136a824da68bf9a2443fa31d54:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | True | False |
| `10edfd136a824da68bf9a2443fa31d54:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | True | False |
| `10edfd136a824da68bf9a2443fa31d54:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `10edfd136a824da68bf9a2443fa31d54:batch:1` | 0 | 0 | 0 | 8 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pos_01_argmax_5_5` | `___stage_value` | 10 | 41 | 41 | False | False |
| `pos_02_argmin_10_10` | `_____stage_value` | 20 | 42 | 42 | False | False |
| `pos_03_argmax_20_20` | `_______stage_value` | 30 | 43 | 43 | False | False |
| `pos_04_argmin_30_20` | `_________stage_value` | 40 | 44 | 44 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `10edfd136a824da68bf9a2443fa31d54:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `10edfd136a824da68bf9a2443fa31d54:batch:1:native_buffer:2` | `pos_02_argmin_10_10` | 236020517 | 14 | 15 | 16 | 0 | True | 8 |
| `10edfd136a824da68bf9a2443fa31d54:batch:1:native_buffer:3` | `pos_03_argmax_20_20` | 236020517 | 24 | 25 | 26 | 0 | True | 8 |
| `10edfd136a824da68bf9a2443fa31d54:batch:1:native_buffer:4` | `pos_04_argmin_30_20` | 236020517 | 34 | 35 | 36 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 715.284 | 157.122 | 380.942 | 0.388 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 390.621 | 149.758 | 348.630 | 0.438 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 20 | 354.918 | 194.012 | 292.717 | 0.513 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 389.292 | 158.486 | 379.821 | 0.465 | False | True | True | True |
