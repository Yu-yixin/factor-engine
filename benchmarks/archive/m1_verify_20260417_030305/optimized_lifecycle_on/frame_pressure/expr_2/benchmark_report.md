# Stage Lifecycle Benchmark Report

- run_id: `e2769ae7dbd94cf6aa4267458181ef57`
- benchmark: `m1_frame_pressure_2`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `2`
- total_time_sec: `0.033620`
- peak_rss_mb: `67.19`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `e2769ae7dbd94cf6aa4267458181ef57:batch:1` | `ordered_batch` | 2 | 6 | 6 | 12 | 6 | 0 | 6 | 0 | 2 | 0 | 67.16 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `e2769ae7dbd94cf6aa4267458181ef57:batch:1:stage:1` | `ordered_helper` | `__stage_value` | 1 | False | True |
| `e2769ae7dbd94cf6aa4267458181ef57:batch:1:stage:2` | `ordered_helper` | `___stage_value` | 1 | False | True |
| `e2769ae7dbd94cf6aa4267458181ef57:batch:1:stage:3` | `staged_prefix` | `____stage_value` | 1 | False | True |
| `e2769ae7dbd94cf6aa4267458181ef57:batch:1:stage:4` | `staged_prefix` | `_____stage_value` | 1 | False | True |
| `e2769ae7dbd94cf6aa4267458181ef57:batch:1:stage:5` | `staged_prefix` | `______stage_value` | 1 | False | True |
| `e2769ae7dbd94cf6aa4267458181ef57:batch:1:stage:6` | `staged_prefix` | `_______stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `e2769ae7dbd94cf6aa4267458181ef57:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `frame_01` | `_____stage_value` | 14 | 23 | 23 | False | False |
| `frame_02` | `_______stage_value` | 16 | 24 | 24 | False | False |
