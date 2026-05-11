# Stage Lifecycle Benchmark Report

- run_id: `00c957d46fea4b6a8d1b1d865b8604a1`
- benchmark: `r4_partial_reuse_2_cse_on`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `2`
- total_time_sec: `9.165837`
- peak_rss_mb: `15481.41`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `00c957d46fea4b6a8d1b1d865b8604a1:batch:1` | `ordered_batch` | 2 | 1 | 1 | 12 | 1 | 0 | 9 | 0 | 2 | 0 | 15481.41 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `00c957d46fea4b6a8d1b1d865b8604a1:batch:1` | 10 | 6 | 3 | 3 | 1 | 2 | 2 | 1 | 1 | 0 | 2 | 2 | 0.667 | 402.954 | 1538.380 | 463.995 | 0.375 | 464.370 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `00c957d46fea4b6a8d1b1d865b8604a1:batch:1` | `first_wave` | True | 1 | 1 | 1 | 232389432 | 0 | 1 | 0 | `n3` | True | True | 12 | 4.000 | 4 | 3.000 | 3 | 929557728 | 1 |

## L3B Helper Column Lifecycle Observability

| batch | helper columns | releasable | blocked | helper live bytes | potential bytes-step savings | blocker reasons |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `00c957d46fea4b6a8d1b1d865b8604a1:batch:1` | 1 | 1 | 0 | 232389432 | 929557728 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `00c957d46fea4b6a8d1b1d865b8604a1:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 232389432 | 4 | 929557728 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `00c957d46fea4b6a8d1b1d865b8604a1:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `00c957d46fea4b6a8d1b1d865b8604a1:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `partial_a` | `None` | 1 | 5 | 5 | False | False |
| `partial_b` | `None` | 2 | 6 | 6 | False | False |
