# Stage Lifecycle Benchmark Report

- run_id: `db9d8e4336384222897694850350ee20`
- benchmark: `m3_m4_cse_expand_repeated_subgraphs_mixed_pattern`
- dataset: `dataframe`
- rows: `1000000`
- groups: `5470`
- expressions: `2`
- total_time_sec: `0.300086`
- peak_rss_mb: `779.02`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `db9d8e4336384222897694850350ee20:batch:1` | `ordered_batch` | 2 | 2 | 1 | 13 | 2 | 0 | 9 | 0 | 2 | 0 | 705.79 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `db9d8e4336384222897694850350ee20:batch:1` | 16 | 7 | 4 | 4 | 2 | 2 | 5 | 2 | 2 | 0 | 4 | 3 | 0.667 | 115.519 | 4.846 | 21.058 | 0.348 | 21.406 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `db9d8e4336384222897694850350ee20:batch:1` | `first_wave` | False | 2 | 2 | 2 | 16000000 | 8000000 | 1 | 1 | `n6` | True | False | 13 | 4.500 | 5 | 3.500 | 4 | 72000000 | 2 |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `db9d8e4336384222897694850350ee20:batch:1` | `second_wave_nested` | True | 2 | 2 | 0 | 16000000 | 16000000 | 8000000 | 1 | 0 | 13 | 12 | 0.000 | 64000000 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `db9d8e4336384222897694850350ee20:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000000 | 5 | 40000000 |
| `n6` | `db9d8e4336384222897694850350ee20:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000000 | 4 | 32000000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `db9d8e4336384222897694850350ee20:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |
| `db9d8e4336384222897694850350ee20:batch:1:stage:2` | `dag_shared_intermediate` | `___dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `db9d8e4336384222897694850350ee20:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `direct` | `None` | 1 | 6 | 6 | False | False |
| `nested` | `None` | 2 | 7 | 7 | False | False |
