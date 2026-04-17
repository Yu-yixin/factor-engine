# Stage Lifecycle Benchmark Report

- run_id: `7826edb85e2a4f289b96b956cb8fc126`
- benchmark: `m1_native_buffer_4`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `4`
- total_time_sec: `15.273554`
- peak_rss_mb: `17679.65`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `7826edb85e2a4f289b96b956cb8fc126:batch:1` | `ordered_batch` | 4 | 8 | 8 | 14 | 5 | 0 | 9 | 0 | 4 | 236020517 | 17679.63 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `7826edb85e2a4f289b96b956cb8fc126:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `7826edb85e2a4f289b96b956cb8fc126:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `7826edb85e2a4f289b96b956cb8fc126:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `7826edb85e2a4f289b96b956cb8fc126:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `7826edb85e2a4f289b96b956cb8fc126:batch:1:stage:5` | `materialized_child` | `______stage_value` | 1 | False | True |
| `7826edb85e2a4f289b96b956cb8fc126:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `7826edb85e2a4f289b96b956cb8fc126:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | False | True |
| `7826edb85e2a4f289b96b956cb8fc126:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `7826edb85e2a4f289b96b956cb8fc126:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pos_01_argmax_5_5` | `___stage_value` | 10 | 49 | 49 | False | False |
| `pos_02_argmin_10_10` | `_____stage_value` | 21 | 50 | 50 | False | False |
| `pos_03_argmax_20_20` | `_______stage_value` | 32 | 51 | 51 | False | False |
| `pos_04_argmin_30_20` | `_________stage_value` | 43 | 52 | 52 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `7826edb85e2a4f289b96b956cb8fc126:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `7826edb85e2a4f289b96b956cb8fc126:batch:1:native_buffer:2` | `pos_02_argmin_10_10` | 236020517 | 15 | 16 | 17 | 0 | True | 8 |
| `7826edb85e2a4f289b96b956cb8fc126:batch:1:native_buffer:3` | `pos_03_argmax_20_20` | 236020517 | 26 | 27 | 28 | 0 | True | 8 |
| `7826edb85e2a4f289b96b956cb8fc126:batch:1:native_buffer:4` | `pos_04_argmin_30_20` | 236020517 | 37 | 38 | 39 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 455.390 | 237.707 | 421.484 | 0.527 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 671.494 | 193.017 | 407.421 | 1.585 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 20 | 480.108 | 163.862 | 323.687 | 0.503 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 397.561 | 160.848 | 419.640 | 0.489 | False | True | True | True |
