# Stage Lifecycle Benchmark Report

- run_id: `a49ace6cdeb7476d9277b069c37ab342`
- benchmark: `m1_frame_pressure_1`
- dataset: `synthetic`
- rows: `2560`
- groups: `32`
- expressions: `1`
- total_time_sec: `0.015054`
- peak_rss_mb: `66.46`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a49ace6cdeb7476d9277b069c37ab342:batch:1` | `ordered_batch` | 1 | 3 | 0 | 9 | 3 | 0 | 9 | 3 | 1 | 0 | 66.46 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `a49ace6cdeb7476d9277b069c37ab342:batch:1:stage:1` | `ordered_helper` | `__stage_value` | 1 | True | False |
| `a49ace6cdeb7476d9277b069c37ab342:batch:1:stage:2` | `staged_prefix` | `___stage_value` | 1 | True | False |
| `a49ace6cdeb7476d9277b069c37ab342:batch:1:stage:3` | `staged_prefix` | `____stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `a49ace6cdeb7476d9277b069c37ab342:batch:1` | 0 | 0 | 0 | 1 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `frame_01` | `____stage_value` | 8 | 9 | 9 | False | False |
