# Stage Lifecycle Benchmark Report

- run_id: `6d4b2738adc448ca8e728b9a16d41d43`
- benchmark: `m1_native_buffer_2`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `2`
- total_time_sec: `10.382600`
- peak_rss_mb: `14442.23`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `6d4b2738adc448ca8e728b9a16d41d43:batch:1` | `ordered_batch` | 2 | 4 | 0 | 13 | 4 | 0 | 13 | 4 | 2 | 236020517 | 14442.23 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `6d4b2738adc448ca8e728b9a16d41d43:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `6d4b2738adc448ca8e728b9a16d41d43:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `6d4b2738adc448ca8e728b9a16d41d43:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | True | False |
| `6d4b2738adc448ca8e728b9a16d41d43:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `6d4b2738adc448ca8e728b9a16d41d43:batch:1` | 0 | 0 | 0 | 4 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pos_01_argmax_5_5` | `___stage_value` | 10 | 21 | 21 | False | False |
| `pos_02_argmin_10_10` | `_____stage_value` | 20 | 22 | 22 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `6d4b2738adc448ca8e728b9a16d41d43:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `6d4b2738adc448ca8e728b9a16d41d43:batch:1:native_buffer:2` | `pos_02_argmin_10_10` | 236020517 | 14 | 15 | 16 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 465.711 | 156.756 | 388.906 | 0.460 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 499.556 | 148.431 | 344.946 | 0.484 | False | True | True | True |
