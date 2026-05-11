# Stage Lifecycle Benchmark Report

- run_id: `5babb57df4ab480eb429e00d8e32c123`
- benchmark: `stage_lifecycle_stage_accumulation_v2`
- dataset: `synthetic_stage_lifecycle`
- rows: `21600`
- groups: `120`
- expressions: `6`
- total_time_sec: `0.070911`
- peak_rss_mb: `79.78`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `5babb57df4ab480eb429e00d8e32c123:batch:1` | `ordered_batch` | 6 | 11 | 11 | 16 | 12 | 0 | 79.78 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `5babb57df4ab480eb429e00d8e32c123:batch:1:stage:1` | `materialized_child` | `__stage_value` | 2 | False | True |
| `5babb57df4ab480eb429e00d8e32c123:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `5babb57df4ab480eb429e00d8e32c123:batch:1:stage:3` | `positional_result` | `____stage_value` | 1 | False | True |
| `5babb57df4ab480eb429e00d8e32c123:batch:1:stage:4` | `materialized_child` | `_____stage_value` | 2 | False | True |
| `5babb57df4ab480eb429e00d8e32c123:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | False | True |
| `5babb57df4ab480eb429e00d8e32c123:batch:1:stage:6` | `materialized_result` | `_______stage_value` | 1 | False | True |
| `5babb57df4ab480eb429e00d8e32c123:batch:1:stage:7` | `materialized_result` | `________stage_value` | 1 | False | True |
| `5babb57df4ab480eb429e00d8e32c123:batch:1:stage:8` | `ordered_helper` | `_________stage_value` | 1 | False | True |
| `5babb57df4ab480eb429e00d8e32c123:batch:1:stage:9` | `staged_prefix` | `__________stage_value` | 1 | False | True |
| `5babb57df4ab480eb429e00d8e32c123:batch:1:stage:10` | `staged_prefix` | `___________stage_value` | 1 | False | True |
| `5babb57df4ab480eb429e00d8e32c123:batch:1:stage:11` | `staged_prefix` | `____________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `5babb57df4ab480eb429e00d8e32c123:batch:1` | 3 | 3 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | to_list ms | scan ms | attach ms | python | native |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `argmax` | 21600 | 120 | 20 | 1.327 | 0.412 | 6.095 | 0.358 | True | False |
| `argmin` | 21600 | 120 | 20 | 0.054 | 0.230 | 5.796 | 0.344 | True | False |
