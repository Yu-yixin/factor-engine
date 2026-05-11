# Stage Lifecycle Benchmark Report

- run_id: `d9ec45b627c64f0aa9a0a049c95a5bfa`
- benchmark: `m3_baseline_synthetic_large`
- dataset: `dataframe`
- rows: `1000000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `0.234008`
- peak_rss_mb: `557.71`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d9ec45b627c64f0aa9a0a049c95a5bfa:batch:1` | `ordered_batch` | 1 | 2 | 2 | 12 | 2 | 0 | 9 | 0 | 1 | 0 | 512.03 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d9ec45b627c64f0aa9a0a049c95a5bfa:batch:1` | 15 | 8 | 5 | 5 | 2 | 2 | 4 | 2 | 2 | 0 | 4 | 2 | 0.667 | 103.500 | 3.286 | 14.347 | 0.093 | 14.440 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d9ec45b627c64f0aa9a0a049c95a5bfa:batch:1` | `first_wave` | True | 2 | 2 | 2 | 16000000 | 0 | 2 | 0 | `n3,n6` | True | True | 13 | 4.000 | 4 | 3.000 | 3 | 64000000 | 2 |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `d9ec45b627c64f0aa9a0a049c95a5bfa:batch:1` | `second_wave_nested` | False | 2 | 2 | 0 | 16000000 | 16000000 | 16000000 | 0 | 0 | 12 | 12 | 0.000 | 64000000 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `d9ec45b627c64f0aa9a0a049c95a5bfa:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000000 | 4 | 32000000 |
| `n6` | `d9ec45b627c64f0aa9a0a049c95a5bfa:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000000 | 4 | 32000000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `d9ec45b627c64f0aa9a0a049c95a5bfa:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |
| `d9ec45b627c64f0aa9a0a049c95a5bfa:batch:1:stage:2` | `dag_shared_intermediate` | `___dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `d9ec45b627c64f0aa9a0a049c95a5bfa:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `multi` | `None` | 1 | 6 | 6 | False | False |
