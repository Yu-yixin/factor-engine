# Stage Lifecycle Benchmark Report

- run_id: `8bf89439f0ea4f578a2d1aa0db515d2f`
- benchmark: `m1_frame_pressure_1`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `1`
- total_time_sec: `0.020509`
- peak_rss_mb: `66.44`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `8bf89439f0ea4f578a2d1aa0db515d2f:batch:1` | `ordered_batch` | 1 | 3 | 3 | 9 | 3 | 0 | 6 | 0 | 1 | 0 | 66.44 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `8bf89439f0ea4f578a2d1aa0db515d2f:batch:1:stage:1` | `ordered_helper` | `__stage_value` | 1 | False | True |
| `8bf89439f0ea4f578a2d1aa0db515d2f:batch:1:stage:2` | `staged_prefix` | `___stage_value` | 1 | False | True |
| `8bf89439f0ea4f578a2d1aa0db515d2f:batch:1:stage:3` | `staged_prefix` | `____stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `8bf89439f0ea4f578a2d1aa0db515d2f:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `frame_01` | `____stage_value` | 8 | 12 | 12 | False | False |
