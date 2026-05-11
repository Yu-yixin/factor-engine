# Stage Lifecycle Benchmark Report

- run_id: `91356cee701645f7be1899f5caaf1fe9`
- benchmark: `m1_output_retention_2`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `2`
- total_time_sec: `10.056489`
- peak_rss_mb: `7740.51`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `91356cee701645f7be1899f5caaf1fe9:batch:1` | `ordered_batch` | 2 | 4 | 0 | 13 | 4 | 0 | 13 | 4 | 2 | 236020517 | 7740.51 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `91356cee701645f7be1899f5caaf1fe9:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `91356cee701645f7be1899f5caaf1fe9:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `91356cee701645f7be1899f5caaf1fe9:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | True | False |
| `91356cee701645f7be1899f5caaf1fe9:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `91356cee701645f7be1899f5caaf1fe9:batch:1` | 0 | 0 | 0 | 4 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `out_01` | `___stage_value` | 10 | 21 | 21 | False | False |
| `out_02` | `_____stage_value` | 20 | 22 | 22 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `91356cee701645f7be1899f5caaf1fe9:batch:1:native_buffer:1` | `out_01` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `91356cee701645f7be1899f5caaf1fe9:batch:1:native_buffer:2` | `out_02` | 236020517 | 14 | 15 | 16 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 4 | 3.531 | 209.104 | 346.639 | 0.599 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 5 | 1.056 | 167.411 | 376.588 | 0.405 | False | True | True | True |
