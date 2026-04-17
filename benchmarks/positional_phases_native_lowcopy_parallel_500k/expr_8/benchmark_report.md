# Stage Lifecycle Benchmark Report

- run_id: `cab5d3a914a045f5a44eeaf605817214`
- benchmark: `positional_phase_expr_8`
- dataset: `minute_2026_03.parquet`
- rows: `500000`
- groups: `5470`
- expressions: `8`
- total_time_sec: `0.337476`
- peak_rss_mb: `302.73`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `cab5d3a914a045f5a44eeaf605817214:batch:1` | `ordered_batch` | 8 | 15 | 15 | 19 | 17 | 0 | 302.73 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `cab5d3a914a045f5a44eeaf605817214:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `cab5d3a914a045f5a44eeaf605817214:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `cab5d3a914a045f5a44eeaf605817214:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `cab5d3a914a045f5a44eeaf605817214:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `cab5d3a914a045f5a44eeaf605817214:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | False | True |
| `cab5d3a914a045f5a44eeaf605817214:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `cab5d3a914a045f5a44eeaf605817214:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | False | True |
| `cab5d3a914a045f5a44eeaf605817214:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `cab5d3a914a045f5a44eeaf605817214:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | False | True |
| `cab5d3a914a045f5a44eeaf605817214:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `cab5d3a914a045f5a44eeaf605817214:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | False | True |
| `cab5d3a914a045f5a44eeaf605817214:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `cab5d3a914a045f5a44eeaf605817214:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | False | True |
| `cab5d3a914a045f5a44eeaf605817214:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `cab5d3a914a045f5a44eeaf605817214:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `cab5d3a914a045f5a44eeaf605817214:batch:1` | 1 | 1 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 500000 | 5470 | 5 | 9.329 | 3.563 | 6.321 | 0.236 | False | True | True | True |
| `argmin` | 500000 | 5470 | 10 | 15.400 | 3.356 | 7.624 | 0.269 | False | True | True | True |
| `argmax` | 500000 | 5470 | 20 | 9.572 | 3.113 | 5.256 | 0.149 | False | True | True | True |
| `argmin` | 500000 | 5470 | 20 | 12.730 | 3.907 | 4.935 | 0.144 | False | True | True | True |
| `argmax` | 500000 | 5470 | 20 | 10.092 | 3.229 | 5.298 | 0.208 | False | True | True | True |
| `argmin` | 500000 | 5470 | 20 | 12.712 | 4.001 | 7.730 | 0.157 | False | True | True | True |
| `argmax` | 500000 | 5470 | 5 | 8.534 | 3.117 | 6.178 | 0.150 | False | True | True | True |
| `argmin` | 500000 | 5470 | 10 | 0.069 | 3.886 | 5.355 | 0.151 | False | True | True | True |
