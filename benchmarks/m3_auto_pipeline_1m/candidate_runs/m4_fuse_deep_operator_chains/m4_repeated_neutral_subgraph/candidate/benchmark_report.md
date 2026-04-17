# Stage Lifecycle Benchmark Report

- run_id: `ca80c3842d9a417da8e5acef03517569`
- benchmark: `m3_m4_fuse_deep_operator_chains_m4_repeated_neutral_subgraph`
- dataset: `dataframe`
- rows: `1000000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `0.296753`
- peak_rss_mb: `723.73`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ca80c3842d9a417da8e5acef03517569:batch:1` | `ordered_batch` | 1 | 2 | 2 | 12 | 2 | 0 | 9 | 0 | 1 | 0 | 656.70 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ca80c3842d9a417da8e5acef03517569:batch:1` | 19 | 9 | 6 | 6 | 2 | 2 | 4 | 2 | 2 | 0 | 2 | 2 | 0.500 | 64.703 | 68.363 | 21.490 | 0.154 | 21.645 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ca80c3842d9a417da8e5acef03517569:batch:1` | `first_wave` | False | 2 | 2 | 2 | 16000000 | 16000000 | 0 | 2 | `` | True | False | 14 | 4.000 | 4 | 3.000 | 3 | 64000000 | 2 |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `ca80c3842d9a417da8e5acef03517569:batch:1` | `second_wave_nested` | False | 2 | 2 | 0 | 16000000 | 16000000 | 16000000 | 0 | 0 | 12 | 12 | 0.000 | 64000000 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n5` | `ca80c3842d9a417da8e5acef03517569:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000000 | 4 | 32000000 |
| `n7` | `ca80c3842d9a417da8e5acef03517569:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000000 | 4 | 32000000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `ca80c3842d9a417da8e5acef03517569:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |
| `ca80c3842d9a417da8e5acef03517569:batch:1:stage:2` | `dag_shared_intermediate` | `___dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `ca80c3842d9a417da8e5acef03517569:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `neutral` | `None` | 1 | 6 | 6 | False | False |
