# Stage Lifecycle Benchmark Report

- run_id: `26d2d9f162cb4c93b05fdab1abac35aa`
- benchmark: `direction_check_16_v2`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `16`
- total_time_sec: `165.769241`
- peak_rss_mb: `13376.92`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1` | `ordered_batch` | 16 | 23 | 23 | 27 | 25 | 0 | 13376.84 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:1` | `materialized_child` | `__stage_value` | 2 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:3` | `materialized_child` | `____stage_value` | 2 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:5` | `materialized_child` | `______stage_value` | 4 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:7` | `materialized_child` | `________stage_value` | 2 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 2 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 2 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 2 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:16` | `positional_result` | `_________________stage_value` | 1 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:17` | `positional_result` | `__________________stage_value` | 1 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:18` | `positional_result` | `___________________stage_value` | 1 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:19` | `positional_result` | `____________________stage_value` | 1 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:20` | `positional_result` | `_____________________stage_value` | 1 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:21` | `positional_result` | `______________________stage_value` | 1 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:22` | `positional_result` | `_______________________stage_value` | 1 | False | True |
| `26d2d9f162cb4c93b05fdab1abac35aa:batch:1:stage:23` | `positional_result` | `________________________stage_value` | 1 | False | True |

## Positional Phases

| function | rows | groups | window | child ms | to_list ms | scan ms | attach ms | python kernel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `argmax` | 29048679 | 5495 | 5 | 506.587 | 499.603 | 7908.273 | 217.752 | True |
| `argmin` | 29048679 | 5495 | 10 | 318.245 | 537.133 | 7775.366 | 194.012 | True |
| `argmax` | 29048679 | 5495 | 20 | 346.456 | 548.622 | 7942.123 | 188.676 | True |
| `argmin` | 29048679 | 5495 | 20 | 363.467 | 503.944 | 7569.886 | 171.029 | True |
| `argmax` | 29048679 | 5495 | 20 | 333.549 | 551.763 | 7617.725 | 153.089 | True |
| `argmin` | 29048679 | 5495 | 20 | 352.865 | 541.680 | 7530.717 | 190.919 | True |
| `argmax` | 29048679 | 5495 | 5 | 332.267 | 539.416 | 7505.763 | 188.960 | True |
| `argmin` | 29048679 | 5495 | 10 | 0.059 | 499.871 | 7648.095 | 228.019 | True |
| `argmax` | 29048679 | 5495 | 30 | 0.078 | 516.878 | 7810.843 | 228.241 | True |
| `argmin` | 29048679 | 5495 | 40 | 0.108 | 525.946 | 7778.205 | 252.891 | True |
| `argmax` | 29048679 | 5495 | 60 | 0.087 | 507.916 | 8168.476 | 227.092 | True |
| `argmin` | 29048679 | 5495 | 20 | 0.076 | 489.947 | 7808.551 | 218.890 | True |
| `argmax` | 29048679 | 5495 | 30 | 0.098 | 484.762 | 7938.791 | 189.314 | True |
| `argmin` | 29048679 | 5495 | 40 | 0.072 | 498.608 | 7890.311 | 218.476 | True |
| `argmax` | 29048679 | 5495 | 60 | 0.084 | 511.784 | 7814.224 | 262.338 | True |
| `argmin` | 29048679 | 5495 | 20 | 0.112 | 628.185 | 9236.638 | 231.857 | True |
