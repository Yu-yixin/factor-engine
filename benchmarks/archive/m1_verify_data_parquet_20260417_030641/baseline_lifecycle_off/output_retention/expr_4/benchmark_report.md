# Stage Lifecycle Benchmark Report

- run_id: `d33576e0b3f34e9d8d7df30f6ad47b2e`
- benchmark: `m1_output_retention_4`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `4`
- total_time_sec: `15.190589`
- peak_rss_mb: `18445.84`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d33576e0b3f34e9d8d7df30f6ad47b2e:batch:1` | `ordered_batch` | 4 | 6 | 0 | 15 | 6 | 0 | 15 | 6 | 4 | 236020517 | 18445.84 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `d33576e0b3f34e9d8d7df30f6ad47b2e:batch:1:stage:1` | `materialized_child` | `__stage_value` | 2 | True | False |
| `d33576e0b3f34e9d8d7df30f6ad47b2e:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `d33576e0b3f34e9d8d7df30f6ad47b2e:batch:1:stage:3` | `materialized_child` | `____stage_value` | 2 | True | False |
| `d33576e0b3f34e9d8d7df30f6ad47b2e:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |
| `d33576e0b3f34e9d8d7df30f6ad47b2e:batch:1:stage:5` | `positional_result` | `______stage_value` | 1 | True | False |
| `d33576e0b3f34e9d8d7df30f6ad47b2e:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `d33576e0b3f34e9d8d7df30f6ad47b2e:batch:1` | 2 | 2 | 0 | 6 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `out_01` | `___stage_value` | 10 | 37 | 37 | False | False |
| `out_02` | `_____stage_value` | 20 | 38 | 38 | False | False |
| `out_03` | `______stage_value` | 28 | 39 | 39 | False | False |
| `out_04` | `_______stage_value` | 36 | 40 | 40 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `d33576e0b3f34e9d8d7df30f6ad47b2e:batch:1:native_buffer:1` | `out_01` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `d33576e0b3f34e9d8d7df30f6ad47b2e:batch:1:native_buffer:2` | `out_02` | 236020517 | 14 | 15 | 16 | 0 | True | 8 |
| `d33576e0b3f34e9d8d7df30f6ad47b2e:batch:1:native_buffer:3` | `out_03` | 236020517 | 22 | 23 | 24 | 0 | True | 8 |
| `d33576e0b3f34e9d8d7df30f6ad47b2e:batch:1:native_buffer:4` | `out_04` | 236020517 | 30 | 31 | 32 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 4 | 4.059 | 298.108 | 406.025 | 0.801 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 5 | 3.634 | 223.299 | 462.016 | 2.210 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 6 | 0.020 | 176.078 | 399.169 | 0.505 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 7 | 0.082 | 214.552 | 482.293 | 0.610 | False | True | True | True |
