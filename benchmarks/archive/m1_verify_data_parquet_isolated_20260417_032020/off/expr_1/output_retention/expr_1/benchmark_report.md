# Stage Lifecycle Benchmark Report

- run_id: `8dc1cb3bee9845dbbee66a3c4dac5b9e`
- benchmark: `m1_output_retention_1`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `10.815422`
- peak_rss_mb: `7293.25`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `8dc1cb3bee9845dbbee66a3c4dac5b9e:batch:1` | `ordered_batch` | 1 | 2 | 0 | 11 | 2 | 0 | 11 | 2 | 1 | 236020517 | 7293.24 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `8dc1cb3bee9845dbbee66a3c4dac5b9e:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `8dc1cb3bee9845dbbee66a3c4dac5b9e:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `8dc1cb3bee9845dbbee66a3c4dac5b9e:batch:1` | 0 | 0 | 0 | 2 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `out_01` | `___stage_value` | 10 | 11 | 11 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `8dc1cb3bee9845dbbee66a3c4dac5b9e:batch:1:native_buffer:1` | `out_01` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 4 | 4.743 | 197.799 | 509.472 | 0.598 | False | True | True | True |
