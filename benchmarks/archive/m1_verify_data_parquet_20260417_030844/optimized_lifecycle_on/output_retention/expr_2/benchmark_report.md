# Stage Lifecycle Benchmark Report

- run_id: `37a24f56099446b28a5227497592b59f`
- benchmark: `m1_output_retention_2`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `2`
- total_time_sec: `11.139269`
- peak_rss_mb: `14148.95`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `37a24f56099446b28a5227497592b59f:batch:1` | `ordered_batch` | 2 | 4 | 4 | 12 | 3 | 0 | 9 | 0 | 2 | 236020517 | 14148.95 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `37a24f56099446b28a5227497592b59f:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `37a24f56099446b28a5227497592b59f:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `37a24f56099446b28a5227497592b59f:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `37a24f56099446b28a5227497592b59f:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `37a24f56099446b28a5227497592b59f:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `out_01` | `___stage_value` | 10 | 25 | 25 | False | False |
| `out_02` | `_____stage_value` | 21 | 26 | 26 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `37a24f56099446b28a5227497592b59f:batch:1:native_buffer:1` | `out_01` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `37a24f56099446b28a5227497592b59f:batch:1:native_buffer:2` | `out_02` | 236020517 | 15 | 16 | 17 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 4 | 3.116 | 184.896 | 452.244 | 0.467 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 5 | 1.275 | 182.701 | 418.585 | 0.881 | False | True | True | True |
