# Stage Lifecycle Benchmark Report

- run_id: `c7ef661dd8354dd38337f1e9793e7876`
- benchmark: `m1_native_buffer_8`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `8`
- total_time_sec: `21.765507`
- peak_rss_mb: `21814.65`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1` | `ordered_batch` | 8 | 15 | 0 | 24 | 15 | 0 | 24 | 15 | 8 | 236020517 | 21814.64 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:stage:3` | `materialized_child` | `____stage_value` | 1 | True | False |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:stage:4` | `positional_result` | `_____stage_value` | 1 | True | False |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:stage:5` | `materialized_child` | `______stage_value` | 2 | True | False |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:stage:6` | `positional_result` | `_______stage_value` | 1 | True | False |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:stage:7` | `materialized_child` | `________stage_value` | 1 | True | False |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:stage:8` | `positional_result` | `_________stage_value` | 1 | True | False |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:stage:9` | `materialized_child` | `__________stage_value` | 1 | True | False |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:stage:10` | `positional_result` | `___________stage_value` | 1 | True | False |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:stage:11` | `materialized_child` | `____________stage_value` | 1 | True | False |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:stage:12` | `positional_result` | `_____________stage_value` | 1 | True | False |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:stage:13` | `materialized_child` | `______________stage_value` | 1 | True | False |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:stage:14` | `positional_result` | `_______________stage_value` | 1 | True | False |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:stage:15` | `positional_result` | `________________stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1` | 1 | 1 | 0 | 15 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pos_01_argmax_5_5` | `___stage_value` | 10 | 79 | 79 | False | False |
| `pos_02_argmin_10_10` | `_____stage_value` | 20 | 80 | 80 | False | False |
| `pos_03_argmax_20_20` | `_______stage_value` | 30 | 81 | 81 | False | False |
| `pos_04_argmin_30_20` | `_________stage_value` | 40 | 82 | 82 | False | False |
| `pos_05_argmax_40_20` | `___________stage_value` | 50 | 83 | 83 | False | False |
| `pos_06_argmin_60_20` | `_____________stage_value` | 60 | 84 | 84 | False | False |
| `pos_07_argmax_20_5` | `_______________stage_value` | 70 | 85 | 85 | False | False |
| `pos_08_argmin_20_10` | `________________stage_value` | 78 | 86 | 86 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:native_buffer:1` | `pos_01_argmax_5_5` | 236020517 | 4 | 5 | 6 | 0 | True | 8 |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:native_buffer:2` | `pos_02_argmin_10_10` | 236020517 | 14 | 15 | 16 | 0 | True | 8 |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:native_buffer:3` | `pos_03_argmax_20_20` | 236020517 | 24 | 25 | 26 | 0 | True | 8 |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:native_buffer:4` | `pos_04_argmin_30_20` | 236020517 | 34 | 35 | 36 | 0 | True | 8 |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:native_buffer:5` | `pos_05_argmax_40_20` | 236020517 | 44 | 45 | 46 | 0 | True | 8 |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:native_buffer:6` | `pos_06_argmin_60_20` | 236020517 | 54 | 55 | 56 | 0 | True | 8 |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:native_buffer:7` | `pos_07_argmax_20_5` | 236020517 | 64 | 65 | 66 | 0 | True | 8 |
| `c7ef661dd8354dd38337f1e9793e7876:batch:1:native_buffer:8` | `pos_08_argmin_20_10` | 236020517 | 72 | 73 | 74 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 29048679 | 5495 | 5 | 704.833 | 211.110 | 302.456 | 0.502 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 635.428 | 202.922 | 395.734 | 0.476 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 20 | 572.131 | 190.638 | 337.261 | 0.562 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 443.390 | 197.552 | 313.006 | 0.603 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 20 | 394.519 | 159.621 | 396.634 | 0.524 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 20 | 460.073 | 154.507 | 358.896 | 0.468 | False | True | True | True |
| `argmax` | 29048679 | 5495 | 5 | 378.612 | 309.705 | 1812.303 | 0.678 | False | True | True | True |
| `argmin` | 29048679 | 5495 | 10 | 0.103 | 206.099 | 404.263 | 0.403 | False | True | True | True |
