# Stage Lifecycle Benchmark Report

- run_id: `3e91f46f359e471a98c2b7e3d3ce3513`
- benchmark: `r4_multi_shared_nodes_2_cse_on`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `10.888934`
- peak_rss_mb: `11715.17`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `3e91f46f359e471a98c2b7e3d3ce3513:batch:1` | `ordered_batch` | 1 | 2 | 0 | 12 | 2 | 0 | 11 | 2 | 1 | 0 | 11715.16 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `3e91f46f359e471a98c2b7e3d3ce3513:batch:1` | 15 | 8 | 5 | 5 | 2 | 2 | 4 | 2 | 2 | 0 | 4 | 2 | 0.667 | 3089.151 | 86.580 | 448.009 | 0.215 | 448.225 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `3e91f46f359e471a98c2b7e3d3ce3513:batch:1` | 2 | 2 | 2 | 464778864 | 464778864 | 0 | 0 | `` | True | True | 13 | 4.000 | 4 | 3.000 | 3 | 1859115456 | 2 |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `3e91f46f359e471a98c2b7e3d3ce3513:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 4 | 929557728 |
| `n6` | `3e91f46f359e471a98c2b7e3d3ce3513:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 4 | 929557728 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `3e91f46f359e471a98c2b7e3d3ce3513:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |
| `3e91f46f359e471a98c2b7e3d3ce3513:batch:1:stage:2` | `dag_shared_intermediate` | `___dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `3e91f46f359e471a98c2b7e3d3ce3513:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `multi_shared_nodes` | `None` | 1 | 4 | 4 | False | False |
