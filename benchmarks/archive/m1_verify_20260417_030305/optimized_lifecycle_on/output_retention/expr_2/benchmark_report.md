# Stage Lifecycle Benchmark Report

- run_id: `8922e0e12fbb45f48d6eb23f3f2ee5c7`
- benchmark: `m1_output_retention_2`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `2`
- total_time_sec: `0.025476`
- peak_rss_mb: `61.72`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `8922e0e12fbb45f48d6eb23f3f2ee5c7:batch:1` | `ordered_batch` | 2 | 4 | 4 | 9 | 3 | 0 | 6 | 0 | 2 | 20800 | 61.71 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `8922e0e12fbb45f48d6eb23f3f2ee5c7:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `8922e0e12fbb45f48d6eb23f3f2ee5c7:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `8922e0e12fbb45f48d6eb23f3f2ee5c7:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `8922e0e12fbb45f48d6eb23f3f2ee5c7:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `8922e0e12fbb45f48d6eb23f3f2ee5c7:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `out_01` | `___stage_value` | 10 | 25 | 25 | False | False |
| `out_02` | `_____stage_value` | 21 | 26 | 26 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `8922e0e12fbb45f48d6eb23f3f2ee5c7:batch:1:native_buffer:1` | `out_01` | 20800 | 4 | 5 | 6 | 0 | True | 8 |
| `8922e0e12fbb45f48d6eb23f3f2ee5c7:batch:1:native_buffer:2` | `out_02` | 20800 | 15 | 16 | 17 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 2560 | 32 | 4 | 1.446 | 0.532 | 0.138 | 0.110 | False | True | True | True |
| `argmin` | 2560 | 32 | 5 | 0.980 | 0.353 | 0.155 | 0.164 | False | True | True | True |
