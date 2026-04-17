# Stage Lifecycle Benchmark Report

- run_id: `98ea1282506242c1907835c5bd2ee51c`
- benchmark: `m1_output_retention_1`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `1`
- total_time_sec: `0.020567`
- peak_rss_mb: `60.09`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `98ea1282506242c1907835c5bd2ee51c:batch:1` | `ordered_batch` | 1 | 2 | 2 | 8 | 2 | 0 | 6 | 0 | 1 | 20800 | 60.07 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `98ea1282506242c1907835c5bd2ee51c:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `98ea1282506242c1907835c5bd2ee51c:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `98ea1282506242c1907835c5bd2ee51c:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `out_01` | `___stage_value` | 10 | 13 | 13 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `98ea1282506242c1907835c5bd2ee51c:batch:1:native_buffer:1` | `out_01` | 20800 | 4 | 5 | 6 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 2560 | 32 | 4 | 1.524 | 1.056 | 0.544 | 0.294 | False | True | True | True |
