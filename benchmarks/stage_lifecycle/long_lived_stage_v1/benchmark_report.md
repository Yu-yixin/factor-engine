# Stage Lifecycle Benchmark Report

- run_id: `e3be3bf6a0624341967d71f36ffc426b`
- benchmark: `stage_lifecycle_long_lived_stage_v1`
- dataset: `synthetic_stage_lifecycle`
- rows: `21600`
- groups: `120`
- expressions: `4`
- total_time_sec: `0.043182`
- peak_rss_mb: `83.79`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `e3be3bf6a0624341967d71f36ffc426b:batch:1` | `ordered_batch` | 4 | 9 | 0 | 19 | 19 | 9 | 83.61 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `e3be3bf6a0624341967d71f36ffc426b:batch:1:stage:1` | `ordered_helper` | `__stage_value` | 1 | True | False |
| `e3be3bf6a0624341967d71f36ffc426b:batch:1:stage:2` | `staged_prefix` | `___stage_value` | 1 | True | False |
| `e3be3bf6a0624341967d71f36ffc426b:batch:1:stage:3` | `materialized_result` | `____stage_value` | 1 | True | False |
| `e3be3bf6a0624341967d71f36ffc426b:batch:1:stage:4` | `ordered_helper` | `_____stage_value` | 1 | True | False |
| `e3be3bf6a0624341967d71f36ffc426b:batch:1:stage:5` | `staged_prefix` | `______stage_value` | 1 | True | False |
| `e3be3bf6a0624341967d71f36ffc426b:batch:1:stage:6` | `staged_prefix` | `_______stage_value` | 1 | True | False |
| `e3be3bf6a0624341967d71f36ffc426b:batch:1:stage:7` | `staged_prefix` | `________stage_value` | 1 | True | False |
| `e3be3bf6a0624341967d71f36ffc426b:batch:1:stage:8` | `staged_prefix` | `_________stage_value` | 1 | True | False |
| `e3be3bf6a0624341967d71f36ffc426b:batch:1:stage:9` | `staged_prefix` | `__________stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `e3be3bf6a0624341967d71f36ffc426b:batch:1` | 0 | 0 | 0 | 5 |

## Positional Phases

| function | rows | groups | window | child ms | to_list ms | scan ms | attach ms | python | native |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `argmax` | 21600 | 120 | 20 | 0.000 | 0.466 | 5.136 | 0.325 | True | False |
