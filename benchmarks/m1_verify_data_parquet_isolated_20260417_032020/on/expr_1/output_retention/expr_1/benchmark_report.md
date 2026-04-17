# Stage Lifecycle Benchmark Report

- run_id: `696ce02d19e0417fa0e186996b3fefd3`
- benchmark: `m1_output_retention_1`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `10.433744`
- peak_rss_mb: `7278.77`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `696ce02d19e0417fa0e186996b3fefd3:batch:1` | `ordered_batch` | 1 | 2 | 2 | 11 | 2 | 0 | 9 | 0 | 1 | 236020517 | 7278.75 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `696ce02d19e0417fa0e186996b3fefd3:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `696ce02d19e0417fa0e186996b3fefd3:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `696ce02d19e0417fa0e186996b3fefd3:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `out_01` | `___stage_value` | 10 | 13 | 13 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `696ce02d19e0417fa0e186996b3fefd3:batch:1:native_buffer:1` | `out_01` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 4 | 3.655 | 261.433 | 702.345 | 0.728 | False | True | True | True |
