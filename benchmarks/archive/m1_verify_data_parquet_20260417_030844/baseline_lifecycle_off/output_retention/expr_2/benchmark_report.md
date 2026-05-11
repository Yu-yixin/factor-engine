# Stage Lifecycle Benchmark Report

- run_id: `cf58a37b778b47c5aa275f12f4966e07`
- benchmark: `m1_output_retention_2`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `2`
- total_time_sec: `12.324556`
- peak_rss_mb: `14150.77`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `cf58a37b778b47c5aa275f12f4966e07:batch:1` | `ordered_batch` | 2 | 4 | 0 | 13 | 4 | 0 | 13 | 4 | 2 | 236020517 | 14150.70 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `cf58a37b778b47c5aa275f12f4966e07:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `cf58a37b778b47c5aa275f12f4966e07:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `cf58a37b778b47c5aa275f12f4966e07:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | True | False |
| `cf58a37b778b47c5aa275f12f4966e07:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `cf58a37b778b47c5aa275f12f4966e07:batch:1` | 0 | 0 | 0 | 4 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `out_01` | `___stage_value` | 10 | 21 | 21 | False | False |
| `out_02` | `_____stage_value` | 20 | 22 | 22 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `cf58a37b778b47c5aa275f12f4966e07:batch:1:native_buffer:1` | `out_01` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `cf58a37b778b47c5aa275f12f4966e07:batch:1:native_buffer:2` | `out_02` | 236020517 | 14 | 15 | 16 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 4 | 2.314 | 276.635 | 516.134 | 0.723 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 5 | 1.834 | 253.186 | 739.252 | 1.771 | False | True | True | True |
