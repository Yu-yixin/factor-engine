# Stage Lifecycle Benchmark Report

- run_id: `984c72ef661843d78c182fad265657a6`
- benchmark: `r4_multi_consumer_dag_2_cse_on`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `2`
- total_time_sec: `0.231304`
- peak_rss_mb: `556.64`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `984c72ef661843d78c182fad265657a6:batch:1` | `ordered_batch` | 2 | 1 | 0 | 12 | 1 | 0 | 10 | 1 | 2 | 0 | 476.85 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `984c72ef661843d78c182fad265657a6:batch:1` | 10 | 7 | 3 | 3 | 1 | 1 | 2 | 1 | 1 | 0 | 2 | 2 | 0.667 | 58.760 | 5.125 | 31.682 | 0.199 | 31.881 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | peak live bytes est | avg lag steps | max lag steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `984c72ef661843d78c182fad265657a6:batch:1` | 1 | 1 | 1 | 8000000 | 0.000 | 0 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `984c72ef661843d78c182fad265657a6:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `984c72ef661843d78c182fad265657a6:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 4 | 4 | False | False |
| `consumer_02` | `None` | 2 | 5 | 5 | False | False |
