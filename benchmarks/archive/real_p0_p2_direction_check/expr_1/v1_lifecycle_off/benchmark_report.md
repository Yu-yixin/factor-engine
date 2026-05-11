# Stage Lifecycle Benchmark Report

- run_id: `c9b617c32e854bf69436be17c4cde0a7`
- benchmark: `direction_check_1_v1`
- dataset: `minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `19.110067`
- peak_rss_mb: `5301.84`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `c9b617c32e854bf69436be17c4cde0a7:batch:1` | `ordered_batch` | 1 | 2 | 0 | 12 | 12 | 2 | 5301.83 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `c9b617c32e854bf69436be17c4cde0a7:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `c9b617c32e854bf69436be17c4cde0a7:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |

## Positional Phases

| function | rows | groups | window | child ms | to_list ms | scan ms | attach ms | python kernel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `argmax` | 29048679 | 5495 | 5 | 492.274 | 563.589 | 9094.762 | 199.291 | True |
