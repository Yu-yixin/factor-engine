# Stage Lifecycle Benchmark Report

- run_id: `1974b9e57ac94f88afa2f4f2121e46f9`
- benchmark: `m1_native_buffer_4`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `4`
- total_time_sec: `14.883589`
- peak_rss_mb: `21698.95`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `1974b9e57ac94f88afa2f4f2121e46f9:batch:1` | `ordered_batch` | 4 | 8 | 8 | 14 | 5 | 0 | 9 | 0 | 4 | 236020517 | 21698.35 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `1974b9e57ac94f88afa2f4f2121e46f9:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `1974b9e57ac94f88afa2f4f2121e46f9:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `1974b9e57ac94f88afa2f4f2121e46f9:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `1974b9e57ac94f88afa2f4f2121e46f9:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `1974b9e57ac94f88afa2f4f2121e46f9:batch:1:stage:5` | `materialized_child` | `______stage_value` | 1 | False | True |
| `1974b9e57ac94f88afa2f4f2121e46f9:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `1974b9e57ac94f88afa2f4f2121e46f9:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | False | True |
| `1974b9e57ac94f88afa2f4f2121e46f9:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `1974b9e57ac94f88afa2f4f2121e46f9:batch:1` | 0 | 0 | 0 | 0 |

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
| `1974b9e57ac94f88afa2f4f2121e46f9:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `1974b9e57ac94f88afa2f4f2121e46f9:batch:1:native_buffer:2` | `pos_02_argmin_10_10` | 236020517 | 15 | 16 | 17 | 0 | True | 8 |
| `1974b9e57ac94f88afa2f4f2121e46f9:batch:1:native_buffer:3` | `pos_03_argmax_20_20` | 236020517 | 26 | 27 | 28 | 0 | True | 8 |
| `1974b9e57ac94f88afa2f4f2121e46f9:batch:1:native_buffer:4` | `pos_04_argmin_30_20` | 236020517 | 37 | 38 | 39 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 554.352 | 165.253 | 309.462 | 1.474 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 547.401 | 236.351 | 357.853 | 1.208 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 20 | 440.555 | 186.731 | 422.088 | 0.482 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 576.357 | 340.712 | 545.288 | 1.006 | False | True | True | True |
