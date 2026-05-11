# Stage Lifecycle Benchmark Report

- run_id: `0d7501560fea4b06b26bae1d549f91fc`
- benchmark: `positional_phase_expr_8`
- dataset: `minute_2026_03.parquet`
- rows: `500000`
- groups: `5470`
- expressions: `8`
- total_time_sec: `0.350027`
- peak_rss_mb: `276.63`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0d7501560fea4b06b26bae1d549f91fc:batch:1` | `ordered_batch` | 8 | 15 | 15 | 19 | 17 | 0 | 276.61 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `0d7501560fea4b06b26bae1d549f91fc:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `0d7501560fea4b06b26bae1d549f91fc:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `0d7501560fea4b06b26bae1d549f91fc:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `0d7501560fea4b06b26bae1d549f91fc:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `0d7501560fea4b06b26bae1d549f91fc:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | False | True |
| `0d7501560fea4b06b26bae1d549f91fc:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `0d7501560fea4b06b26bae1d549f91fc:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | False | True |
| `0d7501560fea4b06b26bae1d549f91fc:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `0d7501560fea4b06b26bae1d549f91fc:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | False | True |
| `0d7501560fea4b06b26bae1d549f91fc:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `0d7501560fea4b06b26bae1d549f91fc:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | False | True |
| `0d7501560fea4b06b26bae1d549f91fc:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `0d7501560fea4b06b26bae1d549f91fc:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | False | True |
| `0d7501560fea4b06b26bae1d549f91fc:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `0d7501560fea4b06b26bae1d549f91fc:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `0d7501560fea4b06b26bae1d549f91fc:batch:1` | 1 | 1 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 500000 | 5470 | 5 | 9.582 | 5.858 | 6.560 | 0.163 | False | True | True | True |
| `argmin` | 500000 | 5470 | 10 | 9.518 | 3.215 | 18.712 | 0.185 | False | True | True | True |
| `argmax` | 500000 | 5470 | 20 | 19.658 | 3.074 | 5.913 | 0.149 | False | True | True | True |
| `argmin` | 500000 | 5470 | 20 | 11.270 | 3.222 | 6.581 | 0.159 | False | True | True | True |
| `argmax` | 500000 | 5470 | 20 | 7.908 | 3.367 | 4.848 | 0.145 | False | True | True | True |
| `argmin` | 500000 | 5470 | 20 | 10.134 | 3.298 | 5.281 | 0.148 | False | True | True | True |
| `argmax` | 500000 | 5470 | 5 | 8.408 | 3.393 | 4.849 | 0.139 | False | True | True | True |
| `argmin` | 500000 | 5470 | 10 | 0.064 | 3.112 | 5.760 | 0.144 | False | True | True | True |
