# Stage Lifecycle Benchmark Report

- run_id: `fa13c8790ae14344af90920a43a8b15e`
- benchmark: `r4_nested_probe_a_2_cse_on`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `22.614468`
- peak_rss_mb: `10328.69`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fa13c8790ae14344af90920a43a8b15e:batch:1` | `ordered_batch` | 1 | 2 | 2 | 12 | 2 | 0 | 9 | 0 | 1 | 0 | 10328.67 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fa13c8790ae14344af90920a43a8b15e:batch:1` | 11 | 5 | 4 | 4 | 2 | 2 | 4 | 2 | 2 | 0 | 3 | 2 | 0.600 | 4309.993 | 32.111 | 600.281 | 0.257 | 600.537 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fa13c8790ae14344af90920a43a8b15e:batch:1` | `first_wave` | True | 2 | 2 | 2 | 464778864 | 0 | 2 | 0 | `n3,n4` | True | True | 10 | 5.000 | 6 | 4.000 | 5 | 2323894320 | 2 |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `fa13c8790ae14344af90920a43a8b15e:batch:1` | `first_wave` | False | 2 | 2 | 0 | 464778864 | 464778864 | 464778864 | 0 | 0 | 12 | 12 | 0.000 | 2323894320 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `fa13c8790ae14344af90920a43a8b15e:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 6 | 1394336592 |
| `n4` | `fa13c8790ae14344af90920a43a8b15e:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 4 | 929557728 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `fa13c8790ae14344af90920a43a8b15e:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |
| `fa13c8790ae14344af90920a43a8b15e:batch:1:stage:2` | `dag_shared_intermediate` | `___dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `fa13c8790ae14344af90920a43a8b15e:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `nested_probe_a` | `None` | 1 | 6 | 6 | False | False |
