# Stage Lifecycle Benchmark Report

- run_id: `fdfcfd620fa24499a737b84c11d8c383`
- benchmark: `positional_phase_expr_16`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `16`
- total_time_sec: `29.617698`
- peak_rss_mb: `19120.63`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1` | `ordered_batch` | 16 | 23 | 23 | 27 | 25 | 0 | 19120.46 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:1` | `materialized_child` | `__stage_value` | 2 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:3` | `materialized_child` | `____stage_value` | 2 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:5` | `materialized_child` | `______stage_value` | 4 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:7` | `materialized_child` | `________stage_value` | 2 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 2 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 2 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 2 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:16` | `positional_result` | `_________________stage_value` | 1 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:17` | `positional_result` | `__________________stage_value` | 1 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:18` | `positional_result` | `___________________stage_value` | 1 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:19` | `positional_result` | `____________________stage_value` | 1 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:20` | `positional_result` | `_____________________stage_value` | 1 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:21` | `positional_result` | `______________________stage_value` | 1 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:22` | `positional_result` | `_______________________stage_value` | 1 | False | True |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1:stage:23` | `positional_result` | `________________________stage_value` | 1 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `fdfcfd620fa24499a737b84c11d8c383:batch:1` | 7 | 9 | 0 | 0 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 508.422 | 175.415 | 813.566 | 0.490 | False | True | True | False |
| `argmin` | 29048679 | 5495 | 10 | 569.973 | 144.720 | 619.617 | 0.339 | False | True | True | False |
| `argmax` | 29048679 | 5495 | 20 | 364.426 | 133.506 | 646.678 | 0.365 | False | True | True | False |
| `argmin` | 29048679 | 5495 | 20 | 370.951 | 139.505 | 525.208 | 0.939 | False | True | True | False |
| `argmax` | 29048679 | 5495 | 20 | 381.136 | 140.680 | 562.407 | 0.374 | False | True | True | False |
| `argmin` | 29048679 | 5495 | 20 | 363.497 | 141.935 | 547.397 | 0.403 | False | True | True | False |
| `argmax` | 29048679 | 5495 | 5 | 424.278 | 149.859 | 598.573 | 0.465 | False | True | True | False |
| `argmin` | 29048679 | 5495 | 10 | 0.062 | 154.614 | 701.496 | 0.328 | False | True | True | False |
| `argmax` | 29048679 | 5495 | 30 | 0.150 | 172.274 | 631.729 | 0.399 | False | True | True | False |
| `argmin` | 29048679 | 5495 | 40 | 0.083 | 183.181 | 709.057 | 0.419 | False | True | True | False |
| `argmax` | 29048679 | 5495 | 60 | 0.077 | 182.941 | 688.984 | 0.601 | False | True | True | False |
| `argmin` | 29048679 | 5495 | 20 | 0.087 | 210.050 | 771.139 | 0.355 | False | True | True | False |
| `argmax` | 29048679 | 5495 | 30 | 0.111 | 158.948 | 705.141 | 0.462 | False | True | True | False |
| `argmin` | 29048679 | 5495 | 40 | 0.078 | 149.443 | 657.559 | 0.378 | False | True | True | False |
| `argmax` | 29048679 | 5495 | 60 | 0.080 | 148.517 | 685.451 | 0.470 | False | True | True | False |
| `argmin` | 29048679 | 5495 | 20 | 0.161 | 149.812 | 845.172 | 0.397 | False | True | True | False |
