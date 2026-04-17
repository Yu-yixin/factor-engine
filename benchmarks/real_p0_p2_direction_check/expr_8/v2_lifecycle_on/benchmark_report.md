# Stage Lifecycle Benchmark Report

- run_id: `ca32b1ed987e44f5a4b1ab54f0c1ea22`
- benchmark: `direction_check_8_v2`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `8`
- total_time_sec: `85.749527`
- peak_rss_mb: `8574.61`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ca32b1ed987e44f5a4b1ab54f0c1ea22:batch:1` | `ordered_batch` | 8 | 15 | 15 | 19 | 17 | 0 | 8574.61 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `ca32b1ed987e44f5a4b1ab54f0c1ea22:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | False | True |
| `ca32b1ed987e44f5a4b1ab54f0c1ea22:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `ca32b1ed987e44f5a4b1ab54f0c1ea22:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | False | True |
| `ca32b1ed987e44f5a4b1ab54f0c1ea22:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `ca32b1ed987e44f5a4b1ab54f0c1ea22:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | False | True |
| `ca32b1ed987e44f5a4b1ab54f0c1ea22:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `ca32b1ed987e44f5a4b1ab54f0c1ea22:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | False | True |
| `ca32b1ed987e44f5a4b1ab54f0c1ea22:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `ca32b1ed987e44f5a4b1ab54f0c1ea22:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | False | True |
| `ca32b1ed987e44f5a4b1ab54f0c1ea22:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `ca32b1ed987e44f5a4b1ab54f0c1ea22:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | False | True |
| `ca32b1ed987e44f5a4b1ab54f0c1ea22:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `ca32b1ed987e44f5a4b1ab54f0c1ea22:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | False | True |
| `ca32b1ed987e44f5a4b1ab54f0c1ea22:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `ca32b1ed987e44f5a4b1ab54f0c1ea22:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |

## Positional Phases

| function | rows | groups | window | child ms | to_list ms | scan ms | attach ms | python kernel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `argmax` | 29048679 | 5495 | 5 | 482.054 | 548.729 | 7611.151 | 191.733 | True |
| `argmin` | 29048679 | 5495 | 10 | 443.357 | 457.987 | 7744.028 | 207.076 | True |
| `argmax` | 29048679 | 5495 | 20 | 476.591 | 477.534 | 8169.867 | 225.091 | True |
| `argmin` | 29048679 | 5495 | 20 | 385.908 | 602.916 | 7540.866 | 157.737 | True |
| `argmax` | 29048679 | 5495 | 20 | 410.743 | 529.991 | 7612.260 | 182.583 | True |
| `argmin` | 29048679 | 5495 | 20 | 379.842 | 553.916 | 7430.313 | 167.290 | True |
| `argmax` | 29048679 | 5495 | 5 | 476.870 | 523.503 | 7480.057 | 190.733 | True |
| `argmin` | 29048679 | 5495 | 10 | 0.079 | 469.430 | 7390.003 | 192.084 | True |
