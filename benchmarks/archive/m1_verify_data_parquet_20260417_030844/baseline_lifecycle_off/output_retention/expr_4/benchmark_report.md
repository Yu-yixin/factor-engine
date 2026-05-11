# Stage Lifecycle Benchmark Report

- run_id: `adeae648a4d54134b64bdb3a08f33256`
- benchmark: `m1_output_retention_4`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `4`
- total_time_sec: `15.706175`
- peak_rss_mb: `20187.82`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `adeae648a4d54134b64bdb3a08f33256:batch:1` | `ordered_batch` | 4 | 6 | 0 | 15 | 6 | 0 | 15 | 6 | 4 | 236020517 | 20187.79 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `adeae648a4d54134b64bdb3a08f33256:batch:1:stage:1` | `materialized_child` | `__stage_value` | 2 | True | False |
| `adeae648a4d54134b64bdb3a08f33256:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `adeae648a4d54134b64bdb3a08f33256:batch:1:stage:3` | `materialized_child` | `____stage_value` | 2 | True | False |
| `adeae648a4d54134b64bdb3a08f33256:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |
| `adeae648a4d54134b64bdb3a08f33256:batch:1:stage:5` | `positional_result` | `______stage_value` | 1 | True | False |
| `adeae648a4d54134b64bdb3a08f33256:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `adeae648a4d54134b64bdb3a08f33256:batch:1` | 2 | 2 | 0 | 6 |

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
| `adeae648a4d54134b64bdb3a08f33256:batch:1:native_buffer:1` | `out_01` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `adeae648a4d54134b64bdb3a08f33256:batch:1:native_buffer:2` | `out_02` | 236020517 | 14 | 15 | 16 | 0 | True | 8 |
| `adeae648a4d54134b64bdb3a08f33256:batch:1:native_buffer:3` | `out_03` | 236020517 | 22 | 23 | 24 | 0 | True | 8 |
| `adeae648a4d54134b64bdb3a08f33256:batch:1:native_buffer:4` | `out_04` | 236020517 | 30 | 31 | 32 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 4 | 5.047 | 229.952 | 624.939 | 1.207 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 5 | 1.994 | 263.057 | 481.113 | 0.541 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 6 | 0.025 | 272.158 | 460.277 | 0.413 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 7 | 0.073 | 306.718 | 467.261 | 0.598 | False | True | True | True |
