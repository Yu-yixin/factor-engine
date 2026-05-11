# Stage Lifecycle Benchmark Report

- run_id: `d6b975bf4fe8417d8dbe3baeded36cd8`
- benchmark: `m2_5_reject_output_pinned`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `2`
- total_time_sec: `11.349622`
- peak_rss_mb: `20882.15`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d6b975bf4fe8417d8dbe3baeded36cd8:batch:1` | `ordered_batch` | 2 | 2 | 2 | 13 | 2 | 0 | 9 | 0 | 2 | 0 | 20882.12 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d6b975bf4fe8417d8dbe3baeded36cd8:batch:1` | 14 | 5 | 4 | 4 | 2 | 2 | 5 | 2 | 2 | 0 | 4 | 3 | 0.667 | 2629.336 | 63.470 | 687.090 | 0.213 | 687.303 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d6b975bf4fe8417d8dbe3baeded36cd8:batch:1` | `first_wave` | True | 1 | 2 | 2 | 464778864 | 232389432 | 1 | 0 | `n4` | True | True | 11 | 4.500 | 5 | 3.500 | 4 | 2091504888 | 1 |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `d6b975bf4fe8417d8dbe3baeded36cd8:batch:1` | `second_wave_nested` | False | 2 | 1 | 1 | 464778864 | 464778864 | 464778864 | 0 | 0 | 13 | 13 | 0.000 | 1859115456 | `final_output_dependency` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `d6b975bf4fe8417d8dbe3baeded36cd8:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 5 | 1161947160 |
| `n4` | `d6b975bf4fe8417d8dbe3baeded36cd8:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 4 | 929557728 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `d6b975bf4fe8417d8dbe3baeded36cd8:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |
| `d6b975bf4fe8417d8dbe3baeded36cd8:batch:1:stage:2` | `dag_shared_intermediate` | `___dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `d6b975bf4fe8417d8dbe3baeded36cd8:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pinned` | `None` | 1 | 7 | 7 | False | False |
| `nested` | `None` | 2 | 8 | 8 | False | False |
