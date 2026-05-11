# Stage Lifecycle Benchmark Report

- run_id: `5f047f5745964f71b58f09ff077505b8`
- benchmark: `m1_native_buffer_2`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `2`
- total_time_sec: `13.803478`
- peak_rss_mb: `14567.29`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `5f047f5745964f71b58f09ff077505b8:batch:1` | `ordered_batch` | 2 | 4 | 4 | 12 | 3 | 0 | 9 | 0 | 2 | 236020517 | 14546.03 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `5f047f5745964f71b58f09ff077505b8:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `5f047f5745964f71b58f09ff077505b8:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `5f047f5745964f71b58f09ff077505b8:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `5f047f5745964f71b58f09ff077505b8:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `5f047f5745964f71b58f09ff077505b8:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pos_01_argmax_5_5` | `___stage_value` | 10 | 25 | 25 | False | False |
| `pos_02_argmin_10_10` | `_____stage_value` | 21 | 26 | 26 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `5f047f5745964f71b58f09ff077505b8:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `5f047f5745964f71b58f09ff077505b8:batch:1:native_buffer:2` | `pos_02_argmin_10_10` | 236020517 | 15 | 16 | 17 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 567.107 | 164.683 | 439.211 | 0.894 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 609.814 | 195.877 | 499.994 | 0.655 | False | True | True | True |
