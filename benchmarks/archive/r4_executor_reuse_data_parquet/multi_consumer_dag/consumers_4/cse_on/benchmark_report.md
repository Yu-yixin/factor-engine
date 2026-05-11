# Stage Lifecycle Benchmark Report

- run_id: `b83a4ca05175433580166dd2c6a2f8e1`
- benchmark: `r4_multi_consumer_dag_4_cse_on`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `4`
- total_time_sec: `10.575612`
- peak_rss_mb: `18051.08`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `b83a4ca05175433580166dd2c6a2f8e1:batch:1` | `ordered_batch` | 4 | 1 | 0 | 10 | 1 | 0 | 10 | 1 | 4 | 0 | 18047.11 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | compute calls | store hits | hit rate | compute ms | store write ms | store hit ms | result store peak | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `b83a4ca05175433580166dd2c6a2f8e1:batch:1` | 20 | 11 | 3 | 3 | 1 | 1 | 1 | 4 | 0.800 | 1646.050 | 0.013 | 0.000 | 5 | 847.119 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `b83a4ca05175433580166dd2c6a2f8e1:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `b83a4ca05175433580166dd2c6a2f8e1:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 6 | 6 | False | False |
| `consumer_02` | `None` | 2 | 7 | 7 | False | False |
| `consumer_03` | `None` | 3 | 8 | 8 | False | False |
| `consumer_04` | `None` | 4 | 9 | 9 | False | False |
