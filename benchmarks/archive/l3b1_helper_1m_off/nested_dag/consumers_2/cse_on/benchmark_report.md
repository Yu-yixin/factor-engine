# Stage Lifecycle Benchmark Report

- run_id: `a8b903355e304b8b847bedca931d0307`
- benchmark: `r4_nested_dag_2_cse_on`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `0.347659`
- peak_rss_mb: `558.11`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a8b903355e304b8b847bedca931d0307:batch:1` | `ordered_batch` | 1 | 2 | 0 | 12 | 2 | 0 | 11 | 2 | 1 | 0 | 512.86 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a8b903355e304b8b847bedca931d0307:batch:1` | 11 | 5 | 4 | 4 | 2 | 2 | 4 | 2 | 2 | 0 | 3 | 2 | 0.600 | 125.775 | 1.697 | 27.691 | 0.120 | 27.811 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a8b903355e304b8b847bedca931d0307:batch:1` | `off` | False | 2 | 2 | 2 | 16000000 | 16000000 | 0 | 0 | `` | True | True | 10 | 5.000 | 6 | 4.000 | 5 | 80000000 | 2 |

## L3B Helper Column Lifecycle Observability

| batch | helper columns | releasable | blocked | helper live bytes | potential bytes-step savings | blocker reasons |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `a8b903355e304b8b847bedca931d0307:batch:1` | 2 | 2 | 0 | 16000000 | 80000000 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `a8b903355e304b8b847bedca931d0307:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000000 | 6 | 48000000 |
| `n4` | `a8b903355e304b8b847bedca931d0307:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000000 | 4 | 32000000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `a8b903355e304b8b847bedca931d0307:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |
| `a8b903355e304b8b847bedca931d0307:batch:1:stage:2` | `dag_shared_intermediate` | `___dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `a8b903355e304b8b847bedca931d0307:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `nested_dag` | `None` | 1 | 4 | 4 | False | False |
