# Stage Lifecycle Benchmark Report

- run_id: `d142b1a54e8b42209fb6520e56a01f7a`
- benchmark: `m1_output_retention_2`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `2`
- total_time_sec: `0.023514`
- peak_rss_mb: `61.52`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d142b1a54e8b42209fb6520e56a01f7a:batch:1` | `ordered_batch` | 2 | 4 | 0 | 10 | 4 | 0 | 10 | 4 | 2 | 20800 | 61.51 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `d142b1a54e8b42209fb6520e56a01f7a:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `d142b1a54e8b42209fb6520e56a01f7a:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `d142b1a54e8b42209fb6520e56a01f7a:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | True | False |
| `d142b1a54e8b42209fb6520e56a01f7a:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `d142b1a54e8b42209fb6520e56a01f7a:batch:1` | 0 | 0 | 0 | 4 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `out_01` | `___stage_value` | 10 | 21 | 21 | False | False |
| `out_02` | `_____stage_value` | 20 | 22 | 22 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `d142b1a54e8b42209fb6520e56a01f7a:batch:1:native_buffer:1` | `out_01` | 20800 | 4 | 5 | 6 | 0 | True | 8 |
| `d142b1a54e8b42209fb6520e56a01f7a:batch:1:native_buffer:2` | `out_02` | 20800 | 14 | 15 | 16 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 2560 | 32 | 4 | 1.362 | 0.477 | 0.268 | 0.212 | False | True | True | True |
| `argmin` | 2560 | 32 | 5 | 1.358 | 0.288 | 0.244 | 0.132 | False | True | True | True |
