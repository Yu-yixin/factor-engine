# Stage Lifecycle Benchmark Report

- run_id: `20048baa86b042eaad8835fd5ccb6f45`
- benchmark: `real_smoke_v1`
- dataset: `minute_2026_03.parquet`
- rows: `500000`
- groups: `5470`
- expressions: `5`
- total_time_sec: `0.834113`
- peak_rss_mb: `266.62`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `20048baa86b042eaad8835fd5ccb6f45:batch:1` | `ordered_batch` | 5 | 11 | 0 | 25 | 25 | 11 | 266.62 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `20048baa86b042eaad8835fd5ccb6f45:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `20048baa86b042eaad8835fd5ccb6f45:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `20048baa86b042eaad8835fd5ccb6f45:batch:1:stage:3` | `positional_result` | `____stage_value` | 1 | True | False |
| `20048baa86b042eaad8835fd5ccb6f45:batch:1:stage:4` | `ordered_helper` | `_____stage_value` | 1 | True | False |
| `20048baa86b042eaad8835fd5ccb6f45:batch:1:stage:5` | `staged_prefix` | `______stage_value` | 1 | True | False |
| `20048baa86b042eaad8835fd5ccb6f45:batch:1:stage:6` | `materialized_result` | `_______stage_value` | 1 | True | False |
| `20048baa86b042eaad8835fd5ccb6f45:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | True | False |
| `20048baa86b042eaad8835fd5ccb6f45:batch:1:stage:8` | `materialized_child` | `_________stage_value` | 1 | True | False |
| `20048baa86b042eaad8835fd5ccb6f45:batch:1:stage:9` | `materialized_result` | `__________stage_value` | 1 | True | False |
| `20048baa86b042eaad8835fd5ccb6f45:batch:1:stage:10` | `staged_prefix` | `___________stage_value` | 1 | True | False |
| `20048baa86b042eaad8835fd5ccb6f45:batch:1:stage:11` | `staged_prefix` | `____________stage_value` | 1 | True | False |
