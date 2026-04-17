# Stage Lifecycle Benchmark Report

- run_id: `c4ec207ce2d14cab9fa022215b6f12a5`
- benchmark: `m1_output_retention_4`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `4`
- total_time_sec: `0.047534`
- peak_rss_mb: `63.01`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `c4ec207ce2d14cab9fa022215b6f12a5:batch:1` | `ordered_batch` | 4 | 6 | 0 | 12 | 6 | 0 | 12 | 6 | 4 | 20800 | 62.98 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `c4ec207ce2d14cab9fa022215b6f12a5:batch:1:stage:1` | `materialized_child` | `__stage_value` | 2 | True | False |
| `c4ec207ce2d14cab9fa022215b6f12a5:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `c4ec207ce2d14cab9fa022215b6f12a5:batch:1:stage:3` | `materialized_child` | `____stage_value` | 2 | True | False |
| `c4ec207ce2d14cab9fa022215b6f12a5:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |
| `c4ec207ce2d14cab9fa022215b6f12a5:batch:1:stage:5` | `positional_result` | `______stage_value` | 1 | True | False |
| `c4ec207ce2d14cab9fa022215b6f12a5:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `c4ec207ce2d14cab9fa022215b6f12a5:batch:1` | 2 | 2 | 0 | 6 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `out_01` | `___stage_value` | 10 | 37 | 37 | False | False |
| `out_02` | `_____stage_value` | 20 | 38 | 38 | False | False |
| `out_03` | `______stage_value` | 28 | 39 | 39 | False | False |
| `out_04` | `_______stage_value` | 36 | 40 | 40 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `c4ec207ce2d14cab9fa022215b6f12a5:batch:1:native_buffer:1` | `out_01` | 20800 | 4 | 5 | 6 | 0 | True | 8 |
| `c4ec207ce2d14cab9fa022215b6f12a5:batch:1:native_buffer:2` | `out_02` | 20800 | 14 | 15 | 16 | 0 | True | 8 |
| `c4ec207ce2d14cab9fa022215b6f12a5:batch:1:native_buffer:3` | `out_03` | 20800 | 22 | 23 | 24 | 0 | True | 8 |
| `c4ec207ce2d14cab9fa022215b6f12a5:batch:1:native_buffer:4` | `out_04` | 20800 | 30 | 31 | 32 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 2560 | 32 | 4 | 1.547 | 9.943 | 0.085 | 0.145 | False | True | True | True |
| `argmin` | 2560 | 32 | 5 | 1.414 | 0.371 | 0.130 | 0.119 | False | True | True | True |
| `argmax` | 2560 | 32 | 6 | 0.017 | 0.400 | 0.129 | 0.106 | False | True | True | True |
| `argmin` | 2560 | 32 | 7 | 0.059 | 0.331 | 0.126 | 0.105 | False | True | True | True |
