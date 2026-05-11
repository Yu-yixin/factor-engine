# Stage Lifecycle Benchmark Report

- run_id: `13de3f6e7340431e9df92e081bc46268`
- benchmark: `positional_phase_expr_16`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `16`
- total_time_sec: `51.838994`
- peak_rss_mb: `15991.62`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `13de3f6e7340431e9df92e081bc46268:batch:1` | `ordered_batch` | 16 | 23 | 23 | 27 | 25 | 0 | 15991.45 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:1` | `materialized_child` | `__stage_value` | 2 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:3` | `materialized_child` | `____stage_value` | 2 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:5` | `materialized_child` | `______stage_value` | 4 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:7` | `materialized_child` | `________stage_value` | 2 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 2 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 2 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 2 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:16` | `positional_result` | `_________________stage_value` | 1 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:17` | `positional_result` | `__________________stage_value` | 1 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:18` | `positional_result` | `___________________stage_value` | 1 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:19` | `positional_result` | `____________________stage_value` | 1 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:20` | `positional_result` | `_____________________stage_value` | 1 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:21` | `positional_result` | `______________________stage_value` | 1 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:22` | `positional_result` | `_______________________stage_value` | 1 | False | True |
| `13de3f6e7340431e9df92e081bc46268:batch:1:stage:23` | `positional_result` | `________________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `13de3f6e7340431e9df92e081bc46268:batch:1` | 7 | 9 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | to_list ms | scan ms | attach ms | python | native |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 533.817 | 1958.381 | 637.010 | 0.088 | False | True |
| `argmin` | 29048679 | 5495 | 10 | 612.263 | 1486.651 | 638.934 | 0.078 | False | True |
| `argmax` | 29048679 | 5495 | 20 | 471.248 | 1471.607 | 481.618 | 0.077 | False | True |
| `argmin` | 29048679 | 5495 | 20 | 419.815 | 1293.416 | 356.503 | 0.082 | False | True |
| `argmax` | 29048679 | 5495 | 20 | 372.004 | 1207.178 | 376.089 | 0.070 | False | True |
| `argmin` | 29048679 | 5495 | 20 | 473.229 | 1213.146 | 324.444 | 0.070 | False | True |
| `argmax` | 29048679 | 5495 | 5 | 479.736 | 1334.345 | 403.282 | 0.079 | False | True |
| `argmin` | 29048679 | 5495 | 10 | 0.060 | 1451.059 | 456.061 | 0.085 | False | True |
| `argmax` | 29048679 | 5495 | 30 | 0.125 | 1372.956 | 478.897 | 0.084 | False | True |
| `argmin` | 29048679 | 5495 | 40 | 0.085 | 1389.479 | 458.610 | 0.121 | False | True |
| `argmax` | 29048679 | 5495 | 60 | 0.076 | 1407.797 | 472.322 | 0.097 | False | True |
| `argmin` | 29048679 | 5495 | 20 | 0.208 | 1510.904 | 570.351 | 0.080 | False | True |
| `argmax` | 29048679 | 5495 | 30 | 0.095 | 1293.068 | 507.585 | 0.070 | False | True |
| `argmin` | 29048679 | 5495 | 40 | 0.074 | 1244.194 | 356.543 | 0.075 | False | True |
| `argmax` | 29048679 | 5495 | 60 | 0.068 | 1279.535 | 341.372 | 0.075 | False | True |
| `argmin` | 29048679 | 5495 | 20 | 0.098 | 1321.782 | 644.916 | 0.071 | False | True |
