# Stage Lifecycle Benchmark Report

- run_id: `dd63f483d4954a9cb5c15cc7122ac989`
- benchmark: `m1_native_buffer_1`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `1`
- total_time_sec: `0.013997`
- peak_rss_mb: `71.61`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `dd63f483d4954a9cb5c15cc7122ac989:batch:1` | `ordered_batch` | 1 | 2 | 0 | 8 | 2 | 0 | 8 | 2 | 1 | 20800 | 71.60 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `dd63f483d4954a9cb5c15cc7122ac989:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `dd63f483d4954a9cb5c15cc7122ac989:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `dd63f483d4954a9cb5c15cc7122ac989:batch:1` | 0 | 0 | 0 | 2 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pos_01_argmax_5_5` | `___stage_value` | 10 | 11 | 11 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `dd63f483d4954a9cb5c15cc7122ac989:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 20800 | 4 | 5 | 6 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 2560 | 32 | 5 | 1.904 | 0.522 | 0.129 | 0.099 | False | True | True | True |
