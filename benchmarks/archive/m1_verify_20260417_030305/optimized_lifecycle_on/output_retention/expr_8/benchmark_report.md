# Stage Lifecycle Benchmark Report

- run_id: `ab65b2dc8b4b4082a2f5c74940256897`
- benchmark: `m1_output_retention_8`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `8`
- total_time_sec: `0.130902`
- peak_rss_mb: `65.02`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1` | `ordered_batch` | 8 | 10 | 10 | 15 | 9 | 0 | 6 | 0 | 8 | 20800 | 65.00 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1:stage:1` | `materialized_child` | `__stage_value` | 3 | False | True |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1:stage:3` | `materialized_child` | `____stage_value` | 5 | False | True |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1:stage:5` | `positional_result` | `______stage_value` | 1 | False | True |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1:stage:7` | `positional_result` | `________stage_value` | 1 | False | True |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1:stage:9` | `positional_result` | `__________stage_value` | 1 | False | True |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1` | 2 | 6 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `out_01` | `___stage_value` | 10 | 79 | 79 | False | False |
| `out_02` | `_____stage_value` | 20 | 80 | 80 | False | False |
| `out_03` | `______stage_value` | 28 | 81 | 81 | False | False |
| `out_04` | `_______stage_value` | 36 | 82 | 82 | False | False |
| `out_05` | `________stage_value` | 44 | 83 | 83 | False | False |
| `out_06` | `_________stage_value` | 52 | 84 | 84 | False | False |
| `out_07` | `__________stage_value` | 60 | 85 | 85 | False | False |
| `out_08` | `___________stage_value` | 69 | 86 | 86 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1:native_buffer:1` | `out_01` | 20800 | 4 | 5 | 6 | 0 | True | 8 |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1:native_buffer:2` | `out_02` | 20800 | 14 | 15 | 16 | 0 | True | 8 |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1:native_buffer:3` | `out_03` | 20800 | 22 | 23 | 24 | 0 | True | 8 |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1:native_buffer:4` | `out_04` | 20800 | 30 | 31 | 32 | 0 | True | 8 |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1:native_buffer:5` | `out_05` | 20800 | 38 | 39 | 40 | 0 | True | 8 |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1:native_buffer:6` | `out_06` | 20800 | 46 | 47 | 48 | 0 | True | 8 |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1:native_buffer:7` | `out_07` | 20800 | 54 | 55 | 56 | 0 | True | 8 |
| `ab65b2dc8b4b4082a2f5c74940256897:batch:1:native_buffer:8` | `out_08` | 20800 | 63 | 64 | 65 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 2560 | 32 | 4 | 1.769 | 0.522 | 0.139 | 0.202 | False | True | True | True |
| `argmin` | 2560 | 32 | 5 | 1.696 | 0.364 | 0.122 | 0.126 | False | True | True | True |
| `argmax` | 2560 | 32 | 6 | 0.019 | 0.300 | 0.120 | 0.130 | False | True | True | True |
| `argmin` | 2560 | 32 | 7 | 0.055 | 0.357 | 0.140 | 0.119 | False | True | True | True |
| `argmax` | 2560 | 32 | 8 | 0.020 | 0.348 | 0.134 | 0.126 | False | True | True | True |
| `argmin` | 2560 | 32 | 9 | 0.020 | 0.366 | 0.158 | 0.254 | False | True | True | True |
| `argmax` | 2560 | 32 | 10 | 0.062 | 0.421 | 5.836 | 0.403 | False | True | True | True |
| `argmin` | 2560 | 32 | 4 | 0.027 | 1.618 | 0.383 | 0.113 | False | True | True | True |
