# Stage Lifecycle Benchmark Report

- run_id: `55e10446e3944d3e8f3cbca799523477`
- benchmark: `m1_native_buffer_4`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `4`
- total_time_sec: `14.260560`
- peak_rss_mb: `21862.68`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `55e10446e3944d3e8f3cbca799523477:batch:1` | `ordered_batch` | 4 | 8 | 0 | 17 | 8 | 0 | 17 | 8 | 4 | 236020517 | 21862.65 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `55e10446e3944d3e8f3cbca799523477:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `55e10446e3944d3e8f3cbca799523477:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `55e10446e3944d3e8f3cbca799523477:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | True | False |
| `55e10446e3944d3e8f3cbca799523477:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |
| `55e10446e3944d3e8f3cbca799523477:batch:1:stage:5` | `materialized_child` | `______stage_value` | 1 | True | False |
| `55e10446e3944d3e8f3cbca799523477:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | True | False |
| `55e10446e3944d3e8f3cbca799523477:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | True | False |
| `55e10446e3944d3e8f3cbca799523477:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `55e10446e3944d3e8f3cbca799523477:batch:1` | 0 | 0 | 0 | 8 |

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
| `55e10446e3944d3e8f3cbca799523477:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `55e10446e3944d3e8f3cbca799523477:batch:1:native_buffer:2` | `pos_02_argmin_10_10` | 236020517 | 14 | 15 | 16 | 0 | True | 8 |
| `55e10446e3944d3e8f3cbca799523477:batch:1:native_buffer:3` | `pos_03_argmax_20_20` | 236020517 | 24 | 25 | 26 | 0 | True | 8 |
| `55e10446e3944d3e8f3cbca799523477:batch:1:native_buffer:4` | `pos_04_argmin_30_20` | 236020517 | 34 | 35 | 36 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 539.053 | 243.737 | 316.694 | 0.412 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 502.492 | 150.738 | 385.581 | 0.447 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 20 | 440.530 | 146.179 | 392.959 | 0.506 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 410.142 | 220.213 | 327.628 | 0.906 | False | True | True | True |
