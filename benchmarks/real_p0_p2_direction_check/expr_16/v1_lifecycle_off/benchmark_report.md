# Stage Lifecycle Benchmark Report

- run_id: `a7d3aad10f634e4fbe0c949ed9e8029a`
- benchmark: `direction_check_16_v1`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `16`
- total_time_sec: `168.133897`
- peak_rss_mb: `13375.12`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1` | `ordered_batch` | 16 | 23 | 0 | 48 | 48 | 23 | 13375.03 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:1` | `materialized_child` | `__stage_value` | 2 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:3` | `materialized_child` | `____stage_value` | 2 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:5` | `materialized_child` | `______stage_value` | 4 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:7` | `materialized_child` | `________stage_value` | 2 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 2 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 2 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 2 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:16` | `positional_result` | `_________________stage_value` | 1 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:17` | `positional_result` | `__________________stage_value` | 1 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:18` | `positional_result` | `___________________stage_value` | 1 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:19` | `positional_result` | `____________________stage_value` | 1 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:20` | `positional_result` | `_____________________stage_value` | 1 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:21` | `positional_result` | `______________________stage_value` | 1 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:22` | `positional_result` | `_______________________stage_value` | 1 | True | False |
| `a7d3aad10f634e4fbe0c949ed9e8029a:batch:1:stage:23` | `positional_result` | `________________________stage_value` | 1 | True | False |

## Positional Phases

| function | rows | groups | window | child ms | to_list ms | scan ms | attach ms | python kernel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `argmax` | 29048679 | 5495 | 5 | 511.143 | 568.708 | 7833.917 | 206.438 | True |
| `argmin` | 29048679 | 5495 | 10 | 378.634 | 495.583 | 7777.121 | 169.103 | True |
| `argmax` | 29048679 | 5495 | 20 | 368.379 | 551.117 | 9833.344 | 206.579 | True |
| `argmin` | 29048679 | 5495 | 20 | 437.000 | 594.038 | 8207.650 | 186.579 | True |
| `argmax` | 29048679 | 5495 | 20 | 415.758 | 598.083 | 8292.716 | 184.917 | True |
| `argmin` | 29048679 | 5495 | 20 | 534.667 | 731.605 | 7724.368 | 190.596 | True |
| `argmax` | 29048679 | 5495 | 5 | 416.279 | 518.873 | 7401.251 | 187.687 | True |
| `argmin` | 29048679 | 5495 | 10 | 0.064 | 514.289 | 7302.779 | 194.967 | True |
| `argmax` | 29048679 | 5495 | 30 | 0.058 | 523.964 | 7962.814 | 206.129 | True |
| `argmin` | 29048679 | 5495 | 40 | 0.149 | 536.247 | 7756.017 | 196.007 | True |
| `argmax` | 29048679 | 5495 | 60 | 0.057 | 540.017 | 8239.221 | 193.364 | True |
| `argmin` | 29048679 | 5495 | 20 | 0.058 | 519.444 | 7909.915 | 191.724 | True |
| `argmax` | 29048679 | 5495 | 30 | 0.080 | 583.327 | 8380.811 | 256.618 | True |
| `argmin` | 29048679 | 5495 | 40 | 0.060 | 529.554 | 8261.433 | 206.701 | True |
| `argmax` | 29048679 | 5495 | 60 | 0.057 | 514.278 | 7635.608 | 195.179 | True |
| `argmin` | 29048679 | 5495 | 20 | 0.073 | 513.193 | 8084.479 | 226.569 | True |
