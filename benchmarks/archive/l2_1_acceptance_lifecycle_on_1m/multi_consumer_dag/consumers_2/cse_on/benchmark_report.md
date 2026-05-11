# Stage Lifecycle Benchmark Report

- run_id: `b33fbd6fd5a94b9cbc6207cf5cac02d2`
- benchmark: `r4_multi_consumer_dag_2_cse_on`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `2`
- total_time_sec: `0.175010`
- peak_rss_mb: `573.12`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `b33fbd6fd5a94b9cbc6207cf5cac02d2:batch:1` | `ordered_batch` | 2 | 1 | 1 | 12 | 1 | 0 | 9 | 0 | 2 | 0 | 507.73 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `b33fbd6fd5a94b9cbc6207cf5cac02d2:batch:1` | 10 | 7 | 3 | 3 | 1 | 1 | 2 | 1 | 1 | 0 | 2 | 2 | 0.667 | 47.719 | 2.757 | 16.025 | 0.228 | 16.253 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `b33fbd6fd5a94b9cbc6207cf5cac02d2:batch:1` | 1 | 1 | 1 | 8000000 | 0 | 1 | 0 | 13 | 4.000 | 4 | 3.000 | 3 | 32000000 | 1 |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `b33fbd6fd5a94b9cbc6207cf5cac02d2:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000000 | 4 | 32000000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `b33fbd6fd5a94b9cbc6207cf5cac02d2:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `b33fbd6fd5a94b9cbc6207cf5cac02d2:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 5 | 5 | False | False |
| `consumer_02` | `None` | 2 | 6 | 6 | False | False |
