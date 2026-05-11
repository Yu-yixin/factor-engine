# Stage Lifecycle Benchmark Report

- run_id: `92ca2ea057cc4d2491837b2f23437700`
- benchmark: `m2_5_pure_nested_chain_second_wave_nested`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `9.956977`
- peak_rss_mb: `21547.57`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `92ca2ea057cc4d2491837b2f23437700:batch:1` | `ordered_batch` | 1 | 2 | 0 | 12 | 2 | 0 | 9 | 0 | 1 | 0 | 21547.56 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `92ca2ea057cc4d2491837b2f23437700:batch:1` | 11 | 5 | 4 | 4 | 2 | 2 | 4 | 2 | 2 | 0 | 3 | 2 | 0.600 | 1885.474 | 31.011 | 583.179 | 0.608 | 583.787 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `92ca2ea057cc4d2491837b2f23437700:batch:1` | `first_wave` | True | 2 | 2 | 2 | 464778864 | 0 | 2 | 0 | `n3,n4` | True | True | 10 | 5.000 | 6 | 4.000 | 5 | 2323894320 | 2 |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `92ca2ea057cc4d2491837b2f23437700:batch:1` | `second_wave_nested` | True | 2 | 2 | 0 | 464778864 | 464778864 | 0 | 2 | 0 | 12 | 10 | 0.000 | 1859115456 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `92ca2ea057cc4d2491837b2f23437700:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 6 | 1394336592 |
| `n4` | `92ca2ea057cc4d2491837b2f23437700:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 4 | 929557728 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `92ca2ea057cc4d2491837b2f23437700:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |
| `92ca2ea057cc4d2491837b2f23437700:batch:1:stage:2` | `dag_shared_intermediate` | `___dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `92ca2ea057cc4d2491837b2f23437700:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pure_nested_chain` | `None` | 1 | 4 | 4 | False | False |
