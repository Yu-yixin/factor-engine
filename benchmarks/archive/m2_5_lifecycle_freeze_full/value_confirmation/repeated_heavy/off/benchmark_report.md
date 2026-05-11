# Stage Lifecycle Benchmark Report

- run_id: `a3b926d0db5c4a60accb1940bc80ed24`
- benchmark: `m2_5_repeated_heavy_off`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `8.804452`
- peak_rss_mb: `6312.06`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a3b926d0db5c4a60accb1940bc80ed24:batch:1` | `ordered_batch` | 1 | 1 | 0 | 11 | 1 | 0 | 10 | 1 | 1 | 0 | 5735.03 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a3b926d0db5c4a60accb1940bc80ed24:batch:1` | 7 | 4 | 3 | 3 | 1 | 1 | 2 | 1 | 1 | 0 | 2 | 1 | 0.667 | 1491.755 | 28.301 | 412.537 | 0.185 | 412.722 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `a3b926d0db5c4a60accb1940bc80ed24:batch:1` | `off` | False | 1 | 1 | 1 | 232389432 | 232389432 | 0 | 0 | `` | True | True | 9 | 4.000 | 4 | 3.000 | 3 | 929557728 | 1 |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `a3b926d0db5c4a60accb1940bc80ed24:batch:1` | `off` | False | 1 | 1 | 0 | 232389432 | 232389432 | 232389432 | 0 | 0 | 11 | 11 | 0.000 | 929557728 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `a3b926d0db5c4a60accb1940bc80ed24:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 4 | 929557728 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `a3b926d0db5c4a60accb1940bc80ed24:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `a3b926d0db5c4a60accb1940bc80ed24:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `repeated_heavy` | `None` | 1 | 3 | 3 | False | False |
