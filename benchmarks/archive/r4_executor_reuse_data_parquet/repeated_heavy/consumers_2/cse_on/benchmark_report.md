# Stage Lifecycle Benchmark Report

- run_id: `a151f6fccd084cc3b6d4b0f13e9192ee`
- benchmark: `r4_repeated_heavy_2_cse_on`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `11.838943`
- peak_rss_mb: `14812.91`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a151f6fccd084cc3b6d4b0f13e9192ee:batch:1` | `ordered_batch` | 1 | 1 | 0 | 10 | 1 | 0 | 10 | 1 | 1 | 0 | 14812.91 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | compute calls | store hits | hit rate | compute ms | store write ms | store hit ms | result store peak | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a151f6fccd084cc3b6d4b0f13e9192ee:batch:1` | 7 | 4 | 3 | 3 | 1 | 1 | 1 | 2 | 0.667 | 1899.242 | 0.018 | 0.000 | 2 | 744.591 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `a151f6fccd084cc3b6d4b0f13e9192ee:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `a151f6fccd084cc3b6d4b0f13e9192ee:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `repeated_heavy` | `None` | 1 | 3 | 3 | False | False |
