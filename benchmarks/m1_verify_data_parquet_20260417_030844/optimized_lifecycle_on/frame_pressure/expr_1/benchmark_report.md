# Stage Lifecycle Benchmark Report

- run_id: `c806a49e03c34969964ab614ed286458`
- benchmark: `m1_frame_pressure_1`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `14.921135`
- peak_rss_mb: `22261.68`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `c806a49e03c34969964ab614ed286458:batch:1` | `ordered_batch` | 1 | 3 | 3 | 12 | 3 | 0 | 9 | 0 | 1 | 0 | 22261.67 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `c806a49e03c34969964ab614ed286458:batch:1:stage:1` | `ordered_helper` | `__stage_value` | 1 | False | True |
| `c806a49e03c34969964ab614ed286458:batch:1:stage:2` | `staged_prefix` | `___stage_value` | 1 | False | True |
| `c806a49e03c34969964ab614ed286458:batch:1:stage:3` | `staged_prefix` | `____stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `c806a49e03c34969964ab614ed286458:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `frame_01` | `____stage_value` | 8 | 12 | 12 | False | False |
