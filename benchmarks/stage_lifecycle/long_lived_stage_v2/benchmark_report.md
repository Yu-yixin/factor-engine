# Stage Lifecycle Benchmark Report

- run_id: `d45ff3bdee5446798e75a50a4a46ca5a`
- benchmark: `stage_lifecycle_long_lived_stage_v2`
- dataset: `synthetic_stage_lifecycle`
- rows: `21600`
- groups: `120`
- expressions: `4`
- total_time_sec: `0.051083`
- peak_rss_mb: `86.09`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d45ff3bdee5446798e75a50a4a46ca5a:batch:1` | `ordered_batch` | 4 | 10 | 10 | 17 | 10 | 0 | 86.09 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `d45ff3bdee5446798e75a50a4a46ca5a:batch:1:stage:1` | `ordered_helper` | `__stage_value` | 1 | False | True |
| `d45ff3bdee5446798e75a50a4a46ca5a:batch:1:stage:2` | `staged_prefix` | `___stage_value` | 1 | False | True |
| `d45ff3bdee5446798e75a50a4a46ca5a:batch:1:stage:3` | `materialized_result` | `____stage_value` | 1 | False | True |
| `d45ff3bdee5446798e75a50a4a46ca5a:batch:1:stage:4` | `ordered_helper` | `_____stage_value` | 1 | False | True |
| `d45ff3bdee5446798e75a50a4a46ca5a:batch:1:stage:5` | `ordered_helper` | `______stage_value` | 1 | False | True |
| `d45ff3bdee5446798e75a50a4a46ca5a:batch:1:stage:6` | `staged_prefix` | `_______stage_value` | 1 | False | True |
| `d45ff3bdee5446798e75a50a4a46ca5a:batch:1:stage:7` | `staged_prefix` | `________stage_value` | 1 | False | True |
| `d45ff3bdee5446798e75a50a4a46ca5a:batch:1:stage:8` | `staged_prefix` | `_________stage_value` | 1 | False | True |
| `d45ff3bdee5446798e75a50a4a46ca5a:batch:1:stage:9` | `staged_prefix` | `__________stage_value` | 1 | False | True |
| `d45ff3bdee5446798e75a50a4a46ca5a:batch:1:stage:10` | `staged_prefix` | `___________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `d45ff3bdee5446798e75a50a4a46ca5a:batch:1` | 0 | 0 | 1 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | to_list ms | scan ms | attach ms | python | native |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `argmax` | 21600 | 120 | 20 | 0.000 | 0.360 | 5.458 | 0.337 | True | False |
