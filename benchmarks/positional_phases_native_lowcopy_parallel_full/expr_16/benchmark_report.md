# Stage Lifecycle Benchmark Report

- run_id: `dae24f8550e24bd4bc0c4b4c40744cb7`
- benchmark: `positional_phase_expr_16`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `16`
- total_time_sec: `26.828467`
- peak_rss_mb: `18993.60`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1` | `ordered_batch` | 16 | 23 | 23 | 27 | 25 | 0 | 18993.43 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:1` | `materialized_child` | `__stage_value` | 2 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:3` | `materialized_child` | `____stage_value` | 2 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:5` | `materialized_child` | `______stage_value` | 4 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:7` | `materialized_child` | `________stage_value` | 2 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 2 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 2 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 2 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:16` | `positional_result` | `_________________stage_value` | 1 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:17` | `positional_result` | `__________________stage_value` | 1 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:18` | `positional_result` | `___________________stage_value` | 1 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:19` | `positional_result` | `____________________stage_value` | 1 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:20` | `positional_result` | `_____________________stage_value` | 1 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:21` | `positional_result` | `______________________stage_value` | 1 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:22` | `positional_result` | `_______________________stage_value` | 1 | False | True |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1:stage:23` | `positional_result` | `________________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `dae24f8550e24bd4bc0c4b4c40744cb7:batch:1` | 7 | 9 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 613.481 | 201.761 | 385.783 | 0.501 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 574.503 | 191.925 | 331.221 | 0.477 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 20 | 453.162 | 161.631 | 315.840 | 0.462 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 395.796 | 159.203 | 334.968 | 0.648 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 20 | 384.258 | 225.624 | 348.869 | 0.509 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 423.052 | 165.816 | 387.957 | 0.602 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 5 | 369.899 | 142.063 | 304.981 | 0.354 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 0.060 | 139.894 | 285.699 | 0.375 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 30 | 0.273 | 144.930 | 367.042 | 0.434 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 40 | 0.087 | 158.002 | 313.029 | 0.490 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 60 | 0.085 | 167.105 | 376.807 | 0.368 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 0.077 | 213.605 | 472.981 | 0.620 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 30 | 0.131 | 189.395 | 354.461 | 0.414 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 40 | 0.079 | 147.888 | 382.368 | 0.426 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 60 | 0.106 | 158.085 | 292.853 | 0.434 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 0.105 | 164.005 | 412.497 | 0.588 | False | True | True | True |
