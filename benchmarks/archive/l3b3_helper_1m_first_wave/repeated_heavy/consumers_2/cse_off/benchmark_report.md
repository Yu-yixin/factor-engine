# Stage Lifecycle Benchmark Report

- run_id: `d8923f2050324efab5ad4a221833df6f`
- benchmark: `r4_repeated_heavy_2_cse_off`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `0.198731`
- peak_rss_mb: `313.30`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d8923f2050324efab5ad4a221833df6f:batch:1` | `ordered_batch` | 1 | 0 | 0 | 10 | 0 | 0 | 9 | 0 | 1 | 0 | 313.30 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d8923f2050324efab5ad4a221833df6f:batch:1` | 7 | 4 | 3 | 3 | 1 | 1 | 2 | 2 | 0 | 2 | 0 | 0 | 0.000 | 0.000 | 78.946 | 17.311 | 0.114 | 17.425 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d8923f2050324efab5ad4a221833df6f:batch:1` | `first_wave` | False | 1 | 0 | 0 | 0 | 0 | 0 | 0 | `` | True | True | 9 | 0.000 | 0 | 0.000 | 0 | 0 | 0 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `d8923f2050324efab5ad4a221833df6f:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `repeated_heavy` | `None` | 1 | 2 | 2 | False | False |
