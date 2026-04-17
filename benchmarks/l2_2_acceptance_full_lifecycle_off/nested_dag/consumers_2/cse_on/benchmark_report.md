# Stage Lifecycle Benchmark Report

- run_id: `d0b207ec689d48ce93c93cb66b41ced8`
- benchmark: `r4_nested_dag_2_cse_on`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `9.652292`
- peak_rss_mb: `14289.01`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d0b207ec689d48ce93c93cb66b41ced8:batch:1` | `ordered_batch` | 1 | 2 | 0 | 12 | 2 | 0 | 11 | 2 | 1 | 0 | 14214.93 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d0b207ec689d48ce93c93cb66b41ced8:batch:1` | 11 | 5 | 4 | 4 | 2 | 2 | 4 | 2 | 2 | 0 | 3 | 2 | 0.600 | 1969.567 | 30.944 | 489.151 | 0.210 | 489.361 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d0b207ec689d48ce93c93cb66b41ced8:batch:1` | 2 | 2 | 2 | 464778864 | 464778864 | 0 | 0 | `` | True | True | 10 | 5.000 | 6 | 4.000 | 5 | 2323894320 | 2 |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `d0b207ec689d48ce93c93cb66b41ced8:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 6 | 1394336592 |
| `n4` | `d0b207ec689d48ce93c93cb66b41ced8:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 4 | 929557728 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `d0b207ec689d48ce93c93cb66b41ced8:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |
| `d0b207ec689d48ce93c93cb66b41ced8:batch:1:stage:2` | `dag_shared_intermediate` | `___dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `d0b207ec689d48ce93c93cb66b41ced8:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `nested_dag` | `None` | 1 | 4 | 4 | False | False |
