# Stage Lifecycle Benchmark Report

- run_id: `499a94911c22489bb3599346d90eaceb`
- benchmark: `r4_multi_consumer_dag_2_cse_on`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `2`
- total_time_sec: `8.931433`
- peak_rss_mb: `16733.36`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `499a94911c22489bb3599346d90eaceb:batch:1` | `ordered_batch` | 2 | 1 | 0 | 10 | 1 | 0 | 10 | 1 | 2 | 0 | 16733.36 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | compute calls | store hits | hit rate | compute ms | store write ms | store hit ms | result store peak | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `499a94911c22489bb3599346d90eaceb:batch:1` | 10 | 7 | 3 | 3 | 1 | 1 | 1 | 2 | 0.667 | 1330.673 | 0.012 | 0.000 | 3 | 741.888 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `499a94911c22489bb3599346d90eaceb:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `499a94911c22489bb3599346d90eaceb:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 4 | 4 | False | False |
| `consumer_02` | `None` | 2 | 5 | 5 | False | False |
