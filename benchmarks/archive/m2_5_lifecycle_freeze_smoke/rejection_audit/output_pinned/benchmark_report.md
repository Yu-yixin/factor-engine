# Stage Lifecycle Benchmark Report

- run_id: `38d837400f494e0eb9e18511b25c19f9`
- benchmark: `m2_5_reject_output_pinned`
- dataset: `data.parquet`
- rows: `1000`
- groups: `1000`
- expressions: `2`
- total_time_sec: `0.019981`
- peak_rss_mb: `70.43`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `38d837400f494e0eb9e18511b25c19f9:batch:1` | `ordered_batch` | 2 | 2 | 2 | 13 | 2 | 0 | 9 | 0 | 2 | 0 | 70.43 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `38d837400f494e0eb9e18511b25c19f9:batch:1` | 14 | 5 | 4 | 4 | 2 | 2 | 5 | 2 | 2 | 0 | 4 | 3 | 0.667 | 2.188 | 0.259 | 0.689 | 0.178 | 0.867 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `38d837400f494e0eb9e18511b25c19f9:batch:1` | `first_wave` | True | 1 | 2 | 2 | 16000 | 8000 | 1 | 0 | `n4` | True | True | 11 | 4.500 | 5 | 3.500 | 4 | 72000 | 1 |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `38d837400f494e0eb9e18511b25c19f9:batch:1` | `second_wave_nested` | False | 2 | 1 | 1 | 16000 | 16000 | 16000 | 0 | 0 | 13 | 13 | 0.000 | 64000 | `final_output_dependency` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `38d837400f494e0eb9e18511b25c19f9:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000 | 5 | 40000 |
| `n4` | `38d837400f494e0eb9e18511b25c19f9:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000 | 4 | 32000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `38d837400f494e0eb9e18511b25c19f9:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |
| `38d837400f494e0eb9e18511b25c19f9:batch:1:stage:2` | `dag_shared_intermediate` | `___dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `38d837400f494e0eb9e18511b25c19f9:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pinned` | `None` | 1 | 7 | 7 | False | False |
| `nested` | `None` | 2 | 8 | 8 | False | False |
