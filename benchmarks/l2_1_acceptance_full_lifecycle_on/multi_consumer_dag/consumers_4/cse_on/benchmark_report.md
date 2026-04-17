# Stage Lifecycle Benchmark Report

- run_id: `ea0d804263cf481dbd3f4815aafa5cbb`
- benchmark: `r4_multi_consumer_dag_4_cse_on`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `4`
- total_time_sec: `10.713900`
- peak_rss_mb: `17865.01`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ea0d804263cf481dbd3f4815aafa5cbb:batch:1` | `ordered_batch` | 4 | 1 | 1 | 14 | 1 | 0 | 9 | 0 | 4 | 0 | 17860.76 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ea0d804263cf481dbd3f4815aafa5cbb:batch:1` | 20 | 11 | 3 | 3 | 1 | 1 | 4 | 1 | 1 | 0 | 4 | 4 | 0.800 | 1852.195 | 144.207 | 700.772 | 0.238 | 701.010 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ea0d804263cf481dbd3f4815aafa5cbb:batch:1` | 1 | 1 | 1 | 232389432 | 0 | 1 | 0 | 19 | 4.000 | 4 | 3.000 | 3 | 929557728 | 1 |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `ea0d804263cf481dbd3f4815aafa5cbb:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 4 | 929557728 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `ea0d804263cf481dbd3f4815aafa5cbb:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `ea0d804263cf481dbd3f4815aafa5cbb:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 7 | 7 | False | False |
| `consumer_02` | `None` | 2 | 8 | 8 | False | False |
| `consumer_03` | `None` | 3 | 9 | 9 | False | False |
| `consumer_04` | `None` | 4 | 10 | 10 | False | False |
