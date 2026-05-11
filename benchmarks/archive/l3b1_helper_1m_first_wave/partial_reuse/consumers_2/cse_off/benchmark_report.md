# Stage Lifecycle Benchmark Report

- run_id: `e739c0369ca24f1eb29463fd0e6fdb69`
- benchmark: `r4_partial_reuse_2_cse_off`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `2`
- total_time_sec: `0.390478`
- peak_rss_mb: `613.92`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `e739c0369ca24f1eb29463fd0e6fdb69:batch:1` | `ordered_batch` | 2 | 0 | 0 | 11 | 0 | 0 | 9 | 0 | 2 | 0 | 613.92 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `e739c0369ca24f1eb29463fd0e6fdb69:batch:1` | 10 | 6 | 3 | 3 | 1 | 2 | 2 | 2 | 0 | 2 | 0 | 0 | 0.000 | 0.000 | 158.280 | 33.698 | 0.204 | 33.901 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `e739c0369ca24f1eb29463fd0e6fdb69:batch:1` | `first_wave` | False | 1 | 0 | 0 | 0 | 0 | 0 | 0 | `` | True | True | 12 | 0.000 | 0 | 0.000 | 0 | 0 | 0 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `e739c0369ca24f1eb29463fd0e6fdb69:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `partial_a` | `None` | 1 | 3 | 3 | False | False |
| `partial_b` | `None` | 2 | 4 | 4 | False | False |
