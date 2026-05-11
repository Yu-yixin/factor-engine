# Stage Lifecycle Benchmark Report

- run_id: `bd0def058344439b90d8025468a0007b`
- benchmark: `m1_native_buffer_2`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `2`
- total_time_sec: `12.157818`
- peak_rss_mb: `21317.43`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `bd0def058344439b90d8025468a0007b:batch:1` | `ordered_batch` | 2 | 4 | 0 | 13 | 4 | 0 | 13 | 4 | 2 | 236020517 | 21317.24 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `bd0def058344439b90d8025468a0007b:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `bd0def058344439b90d8025468a0007b:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `bd0def058344439b90d8025468a0007b:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | True | False |
| `bd0def058344439b90d8025468a0007b:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `bd0def058344439b90d8025468a0007b:batch:1` | 0 | 0 | 0 | 4 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pos_01_argmax_5_5` | `___stage_value` | 10 | 21 | 21 | False | False |
| `pos_02_argmin_10_10` | `_____stage_value` | 20 | 22 | 22 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `bd0def058344439b90d8025468a0007b:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `bd0def058344439b90d8025468a0007b:batch:1:native_buffer:2` | `pos_02_argmin_10_10` | 236020517 | 14 | 15 | 16 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 671.590 | 181.518 | 479.304 | 0.726 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 747.366 | 327.138 | 394.423 | 0.584 | False | True | True | True |
