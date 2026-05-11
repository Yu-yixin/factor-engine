# Stage Lifecycle Benchmark Report

- run_id: `852f3e1e05354183b9bdb7436866d0dd`
- benchmark: `m1_frame_pressure_8`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `8`
- total_time_sec: `43.308632`
- peak_rss_mb: `13984.25`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1` | `ordered_batch` | 8 | 20 | 20 | 25 | 16 | 0 | 9 | 0 | 8 | 236020517 | 13984.18 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:6` | `materialized_child` | `_______stage_value` | 2 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:7` | `materialized_result` | `________stage_value` | 1 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:8` | `materialized_result` | `_________stage_value` | 1 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:9` | `ordered_helper` | `__________stage_value` | 1 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:10` | `ordered_helper` | `___________stage_value` | 1 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:11` | `ordered_helper` | `____________stage_value` | 1 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:12` | `ordered_helper` | `_____________stage_value` | 1 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:13` | `staged_prefix` | `______________stage_value` | 1 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:14` | `staged_prefix` | `_______________stage_value` | 1 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:15` | `staged_prefix` | `________________stage_value` | 1 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:16` | `staged_prefix` | `_________________stage_value` | 1 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:17` | `staged_prefix` | `__________________stage_value` | 1 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:18` | `staged_prefix` | `___________________stage_value` | 1 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:19` | `staged_prefix` | `____________________stage_value` | 1 | False | True |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:stage:20` | `staged_prefix` | `_____________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1` | 2 | 2 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `frame_04` | `___stage_value` | 10 | 89 | 89 | False | False |
| `frame_08` | `_____stage_value` | 21 | 90 | 90 | False | False |
| `frame_03` | `________stage_value` | 32 | 91 | 91 | False | False |
| `frame_07` | `_________stage_value` | 38 | 92 | 92 | False | False |
| `frame_01` | `_______________stage_value` | 66 | 93 | 93 | False | False |
| `frame_02` | `_________________stage_value` | 68 | 94 | 94 | False | False |
| `frame_05` | `___________________stage_value` | 70 | 95 | 95 | False | False |
| `frame_06` | `_____________________stage_value` | 72 | 96 | 96 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:native_buffer:1` | `frame_04` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `852f3e1e05354183b9bdb7436866d0dd:batch:1:native_buffer:2` | `frame_08` | 236020517 | 15 | 16 | 17 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 8 | 997.114 | 238.661 | 724.485 | 0.646 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 6 | 831.114 | 279.832 | 645.042 | 0.566 | False | True | True | True |
