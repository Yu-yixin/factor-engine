# Stage Lifecycle Benchmark Report

- run_id: `ccd8e0e3f2f543e6aa8bd642e4607760`
- benchmark: `m1_native_buffer_1`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `10.816253`
- peak_rss_mb: `13345.84`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ccd8e0e3f2f543e6aa8bd642e4607760:batch:1` | `ordered_batch` | 1 | 2 | 2 | 11 | 2 | 0 | 9 | 0 | 1 | 236020517 | 13345.84 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `ccd8e0e3f2f543e6aa8bd642e4607760:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `ccd8e0e3f2f543e6aa8bd642e4607760:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `ccd8e0e3f2f543e6aa8bd642e4607760:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pos_01_argmax_5_5` | `___stage_value` | 10 | 13 | 13 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `ccd8e0e3f2f543e6aa8bd642e4607760:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 564.201 | 191.039 | 394.011 | 0.661 | False | True | True | True |
