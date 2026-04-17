# Stage Lifecycle Benchmark Report

- run_id: `11eaa4830c5d4792a377c6812e26e836`
- benchmark: `m3_m4_fuse_deep_operator_chains_mixed_pattern`
- dataset: `dataframe`
- rows: `1000`
- groups: `1000`
- expressions: `2`
- total_time_sec: `0.015552`
- peak_rss_mb: `71.75`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `11eaa4830c5d4792a377c6812e26e836:batch:1` | `ordered_batch` | 2 | 2 | 1 | 13 | 2 | 0 | 9 | 0 | 2 | 0 | 71.75 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `11eaa4830c5d4792a377c6812e26e836:batch:1` | 16 | 7 | 4 | 4 | 2 | 2 | 5 | 2 | 2 | 0 | 4 | 3 | 0.667 | 1.768 | 0.217 | 0.643 | 0.148 | 0.790 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `11eaa4830c5d4792a377c6812e26e836:batch:1` | `first_wave` | False | 2 | 2 | 2 | 16000 | 8000 | 1 | 1 | `n6` | True | False | 13 | 4.500 | 5 | 3.500 | 4 | 72000 | 2 |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `11eaa4830c5d4792a377c6812e26e836:batch:1` | `second_wave_nested` | True | 2 | 2 | 0 | 16000 | 16000 | 8000 | 1 | 0 | 13 | 12 | 0.000 | 64000 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `11eaa4830c5d4792a377c6812e26e836:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000 | 5 | 40000 |
| `n6` | `11eaa4830c5d4792a377c6812e26e836:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000 | 4 | 32000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `11eaa4830c5d4792a377c6812e26e836:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |
| `11eaa4830c5d4792a377c6812e26e836:batch:1:stage:2` | `dag_shared_intermediate` | `___dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `11eaa4830c5d4792a377c6812e26e836:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `direct` | `None` | 1 | 6 | 6 | False | False |
| `nested` | `None` | 2 | 7 | 7 | False | False |
