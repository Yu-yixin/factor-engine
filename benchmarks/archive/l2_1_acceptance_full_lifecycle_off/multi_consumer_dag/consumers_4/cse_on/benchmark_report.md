# Stage Lifecycle Benchmark Report

- run_id: `934cf056092d4840845214f27505a721`
- benchmark: `r4_multi_consumer_dag_4_cse_on`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `4`
- total_time_sec: `9.982512`
- peak_rss_mb: `16774.29`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `934cf056092d4840845214f27505a721:batch:1` | `ordered_batch` | 4 | 1 | 0 | 14 | 1 | 0 | 10 | 1 | 4 | 0 | 16757.07 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `934cf056092d4840845214f27505a721:batch:1` | 20 | 11 | 3 | 3 | 1 | 1 | 4 | 1 | 1 | 0 | 4 | 4 | 0.800 | 1468.311 | 186.485 | 607.389 | 0.296 | 607.685 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `934cf056092d4840845214f27505a721:batch:1` | 1 | 1 | 1 | 232389432 | 232389432 | 0 | 0 | 19 | 4.000 | 4 | 3.000 | 3 | 929557728 | 1 |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `934cf056092d4840845214f27505a721:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 4 | 929557728 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `934cf056092d4840845214f27505a721:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `934cf056092d4840845214f27505a721:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 6 | 6 | False | False |
| `consumer_02` | `None` | 2 | 7 | 7 | False | False |
| `consumer_03` | `None` | 3 | 8 | 8 | False | False |
| `consumer_04` | `None` | 4 | 9 | 9 | False | False |
