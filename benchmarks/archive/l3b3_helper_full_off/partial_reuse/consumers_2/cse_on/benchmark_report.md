# Stage Lifecycle Benchmark Report

- run_id: `a5f5f9302e194c818e8c140396072010`
- benchmark: `r4_partial_reuse_2_cse_on`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `2`
- total_time_sec: `12.378624`
- peak_rss_mb: `15824.61`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a5f5f9302e194c818e8c140396072010:batch:1` | `ordered_batch` | 2 | 1 | 1 | 12 | 1 | 0 | 9 | 0 | 2 | 0 | 15824.60 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a5f5f9302e194c818e8c140396072010:batch:1` | 10 | 6 | 3 | 3 | 1 | 2 | 2 | 1 | 1 | 0 | 2 | 2 | 0.667 | 478.451 | 2209.322 | 629.454 | 0.255 | 629.709 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a5f5f9302e194c818e8c140396072010:batch:1` | `first_wave` | True | 1 | 1 | 1 | 232389432 | 0 | 1 | 0 | `n3` | True | True | 12 | 4.000 | 4 | 3.000 | 3 | 929557728 | 1 |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `a5f5f9302e194c818e8c140396072010:batch:1` | `off` | False | 1 | 1 | 0 | 232389432 | 232389432 | 232389432 | 0 | 0 | 12 | 12 | 0.000 | 929557728 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `a5f5f9302e194c818e8c140396072010:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 4 | 929557728 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `a5f5f9302e194c818e8c140396072010:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `a5f5f9302e194c818e8c140396072010:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `partial_a` | `None` | 1 | 5 | 5 | False | False |
| `partial_b` | `None` | 2 | 6 | 6 | False | False |
