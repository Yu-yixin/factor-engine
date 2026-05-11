# Stage Lifecycle Benchmark Report

- run_id: `0ce958e82a974983bd91faf2309eb4a4`
- benchmark: `m1_output_retention_4`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `4`
- total_time_sec: `13.652268`
- peak_rss_mb: `22117.75`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0ce958e82a974983bd91faf2309eb4a4:batch:1` | `ordered_batch` | 4 | 6 | 6 | 14 | 5 | 0 | 9 | 0 | 4 | 236020517 | 22117.75 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `0ce958e82a974983bd91faf2309eb4a4:batch:1:stage:1` | `materialized_child` | `__stage_value` | 2 | False | True |
| `0ce958e82a974983bd91faf2309eb4a4:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `0ce958e82a974983bd91faf2309eb4a4:batch:1:stage:3` | `materialized_child` | `____stage_value` | 2 | False | True |
| `0ce958e82a974983bd91faf2309eb4a4:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `0ce958e82a974983bd91faf2309eb4a4:batch:1:stage:5` | `positional_result` | `______stage_value` | 1 | False | True |
| `0ce958e82a974983bd91faf2309eb4a4:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `0ce958e82a974983bd91faf2309eb4a4:batch:1` | 2 | 2 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `out_01` | `___stage_value` | 10 | 43 | 43 | False | False |
| `out_02` | `_____stage_value` | 20 | 44 | 44 | False | False |
| `out_03` | `______stage_value` | 28 | 45 | 45 | False | False |
| `out_04` | `_______stage_value` | 37 | 46 | 46 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `0ce958e82a974983bd91faf2309eb4a4:batch:1:native_buffer:1` | `out_01` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `0ce958e82a974983bd91faf2309eb4a4:batch:1:native_buffer:2` | `out_02` | 236020517 | 14 | 15 | 16 | 0 | True | 8 |
| `0ce958e82a974983bd91faf2309eb4a4:batch:1:native_buffer:3` | `out_03` | 236020517 | 22 | 23 | 24 | 0 | True | 8 |
| `0ce958e82a974983bd91faf2309eb4a4:batch:1:native_buffer:4` | `out_04` | 236020517 | 31 | 32 | 33 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 4 | 2.260 | 190.109 | 474.723 | 0.554 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 5 | 1.146 | 188.933 | 381.952 | 0.460 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 6 | 0.021 | 185.521 | 389.805 | 0.582 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 7 | 0.097 | 175.414 | 374.809 | 0.453 | False | True | True | True |
