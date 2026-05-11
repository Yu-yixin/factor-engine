# Stage Lifecycle Benchmark Report

- run_id: `05cd0486d42e4b2099b3c7e6d00c20be`
- benchmark: `m3_m3_delayed_output_attach_finalize_select_synthetic_small`
- dataset: `dataframe`
- rows: `1000`
- groups: `1000`
- expressions: `1`
- total_time_sec: `0.009342`
- peak_rss_mb: `67.45`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `05cd0486d42e4b2099b3c7e6d00c20be:batch:1` | `ordered_batch` | 1 | 1 | 1 | 11 | 1 | 0 | 9 | 0 | 1 | 0 | 67.44 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `05cd0486d42e4b2099b3c7e6d00c20be:batch:1` | 7 | 4 | 3 | 3 | 1 | 1 | 2 | 1 | 1 | 0 | 2 | 1 | 0.667 | 0.911 | 0.196 | 0.669 | 0.090 | 0.760 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `05cd0486d42e4b2099b3c7e6d00c20be:batch:1` | `first_wave` | True | 1 | 1 | 1 | 8000 | 0 | 1 | 0 | `n3` | True | True | 9 | 4.000 | 4 | 3.000 | 3 | 32000 | 1 |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `05cd0486d42e4b2099b3c7e6d00c20be:batch:1` | `second_wave_nested` | False | 1 | 1 | 0 | 8000 | 8000 | 8000 | 0 | 0 | 11 | 11 | 0.000 | 32000 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `05cd0486d42e4b2099b3c7e6d00c20be:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000 | 4 | 32000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `05cd0486d42e4b2099b3c7e6d00c20be:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `05cd0486d42e4b2099b3c7e6d00c20be:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `reuse` | `None` | 1 | 4 | 4 | False | False |
