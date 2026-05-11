# Stage Lifecycle Benchmark Report

- run_id: `1122e650c94b48838a025faad4fac03b`
- benchmark: `m3_m4_fuse_deep_operator_chains_m4_unary_chain_fusion`
- dataset: `dataframe`
- rows: `1000000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `0.258387`
- peak_rss_mb: `738.68`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `1122e650c94b48838a025faad4fac03b:batch:1` | `ordered_batch` | 1 | 1 | 1 | 11 | 1 | 0 | 9 | 0 | 1 | 0 | 666.97 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `1122e650c94b48838a025faad4fac03b:batch:1` | 11 | 5 | 4 | 4 | 1 | 2 | 2 | 1 | 1 | 0 | 2 | 1 | 0.667 | 105.519 | 1.119 | 17.364 | 0.125 | 17.488 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `1122e650c94b48838a025faad4fac03b:batch:1` | `first_wave` | True | 1 | 1 | 1 | 8000000 | 0 | 1 | 0 | `n4` | True | True | 10 | 4.000 | 4 | 3.000 | 3 | 32000000 | 1 |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `1122e650c94b48838a025faad4fac03b:batch:1` | `second_wave_nested` | False | 1 | 1 | 0 | 8000000 | 8000000 | 8000000 | 0 | 0 | 11 | 11 | 0.000 | 32000000 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n4` | `1122e650c94b48838a025faad4fac03b:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000000 | 4 | 32000000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `1122e650c94b48838a025faad4fac03b:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `1122e650c94b48838a025faad4fac03b:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `fusion` | `None` | 1 | 4 | 4 | False | False |
