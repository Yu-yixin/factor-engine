# Stage Lifecycle Benchmark Report

- run_id: `99aa0e27a0bb481197f0b570dc7c4e01`
- benchmark: `stage_lifecycle_stage_accumulation_v1`
- dataset: `synthetic_stage_lifecycle`
- rows: `21600`
- groups: `120`
- expressions: `6`
- total_time_sec: `0.069626`
- peak_rss_mb: `74.46`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `99aa0e27a0bb481197f0b570dc7c4e01:batch:1` | `ordered_batch` | 6 | 11 | 0 | 23 | 23 | 11 | 74.33 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `99aa0e27a0bb481197f0b570dc7c4e01:batch:1:stage:1` | `materialized_child` | `__stage_value` | 2 | True | False |
| `99aa0e27a0bb481197f0b570dc7c4e01:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `99aa0e27a0bb481197f0b570dc7c4e01:batch:1:stage:3` | `positional_result` | `____stage_value` | 1 | True | False |
| `99aa0e27a0bb481197f0b570dc7c4e01:batch:1:stage:4` | `materialized_child` | `_____stage_value` | 2 | True | False |
| `99aa0e27a0bb481197f0b570dc7c4e01:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | True | False |
| `99aa0e27a0bb481197f0b570dc7c4e01:batch:1:stage:6` | `materialized_result` | `_______stage_value` | 1 | True | False |
| `99aa0e27a0bb481197f0b570dc7c4e01:batch:1:stage:7` | `materialized_result` | `________stage_value` | 1 | True | False |
| `99aa0e27a0bb481197f0b570dc7c4e01:batch:1:stage:8` | `ordered_helper` | `_________stage_value` | 1 | True | False |
| `99aa0e27a0bb481197f0b570dc7c4e01:batch:1:stage:9` | `staged_prefix` | `__________stage_value` | 1 | True | False |
| `99aa0e27a0bb481197f0b570dc7c4e01:batch:1:stage:10` | `staged_prefix` | `___________stage_value` | 1 | True | False |
| `99aa0e27a0bb481197f0b570dc7c4e01:batch:1:stage:11` | `staged_prefix` | `____________stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `99aa0e27a0bb481197f0b570dc7c4e01:batch:1` | 3 | 3 | 0 | 9 |

## Positional Phases

| function | rows | groups | window | child ms | to_list ms | scan ms | attach ms | python | native |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `argmax` | 21600 | 120 | 20 | 2.013 | 0.415 | 6.340 | 0.412 | True | False |
| `argmin` | 21600 | 120 | 20 | 0.055 | 0.219 | 5.573 | 0.448 | True | False |
