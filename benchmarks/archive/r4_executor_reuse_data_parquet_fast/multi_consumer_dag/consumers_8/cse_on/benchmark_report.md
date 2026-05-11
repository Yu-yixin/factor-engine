# Stage Lifecycle Benchmark Report

- run_id: `610115885c354df5a2d806981f5ffacc`
- benchmark: `r4_multi_consumer_dag_8_cse_on`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `8`
- total_time_sec: `14.166291`
- peak_rss_mb: `19462.16`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `610115885c354df5a2d806981f5ffacc:batch:1` | `ordered_batch` | 8 | 1 | 0 | 10 | 1 | 0 | 10 | 1 | 8 | 0 | 19462.16 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | compute calls | store hits | hit rate | compute ms | store write ms | store hit ms | result store peak | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `610115885c354df5a2d806981f5ffacc:batch:1` | 40 | 19 | 3 | 3 | 1 | 1 | 1 | 8 | 0.889 | 3609.193 | 0.040 | 0.000 | 9 | 1848.362 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `610115885c354df5a2d806981f5ffacc:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `610115885c354df5a2d806981f5ffacc:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 10 | 10 | False | False |
| `consumer_02` | `None` | 2 | 11 | 11 | False | False |
| `consumer_03` | `None` | 3 | 12 | 12 | False | False |
| `consumer_04` | `None` | 4 | 13 | 13 | False | False |
| `consumer_05` | `None` | 5 | 14 | 14 | False | False |
| `consumer_06` | `None` | 6 | 15 | 15 | False | False |
| `consumer_07` | `None` | 7 | 16 | 16 | False | False |
| `consumer_08` | `None` | 8 | 17 | 17 | False | False |
