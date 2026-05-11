# Stage Lifecycle Benchmark Report

- run_id: `280bbce08a74406bacb2af038e393a1d`
- benchmark: `m1_frame_pressure_4`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `4`
- total_time_sec: `27.834093`
- peak_rss_mb: `21729.02`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `280bbce08a74406bacb2af038e393a1d:batch:1` | `ordered_batch` | 4 | 11 | 0 | 20 | 11 | 0 | 20 | 11 | 4 | 236020517 | 21729.01 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `280bbce08a74406bacb2af038e393a1d:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `280bbce08a74406bacb2af038e393a1d:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `280bbce08a74406bacb2af038e393a1d:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | True | False |
| `280bbce08a74406bacb2af038e393a1d:batch:1:stage:4` | `materialized_child` | `_____stage_value` | 1 | True | False |
| `280bbce08a74406bacb2af038e393a1d:batch:1:stage:5` | `materialized_result` | `______stage_value` | 1 | True | False |
| `280bbce08a74406bacb2af038e393a1d:batch:1:stage:6` | `ordered_helper` | `_______stage_value` | 1 | True | False |
| `280bbce08a74406bacb2af038e393a1d:batch:1:stage:7` | `ordered_helper` | `________stage_value` | 1 | True | False |
| `280bbce08a74406bacb2af038e393a1d:batch:1:stage:8` | `staged_prefix` | `_________stage_value` | 1 | True | False |
| `280bbce08a74406bacb2af038e393a1d:batch:1:stage:9` | `staged_prefix` | `__________stage_value` | 1 | True | False |
| `280bbce08a74406bacb2af038e393a1d:batch:1:stage:10` | `staged_prefix` | `___________stage_value` | 1 | True | False |
| `280bbce08a74406bacb2af038e393a1d:batch:1:stage:11` | `staged_prefix` | `____________stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `280bbce08a74406bacb2af038e393a1d:batch:1` | 0 | 0 | 0 | 7 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `frame_04` | `___stage_value` | 10 | 37 | 37 | False | False |
| `frame_03` | `______stage_value` | 20 | 38 | 38 | False | False |
| `frame_01` | `__________stage_value` | 34 | 39 | 39 | False | False |
| `frame_02` | `____________stage_value` | 36 | 40 | 40 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `280bbce08a74406bacb2af038e393a1d:batch:1:native_buffer:1` | `frame_04` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 8 | 671.233 | 196.873 | 815.183 | 7.282 | False | True | True | True |
