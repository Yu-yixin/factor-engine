# Stage Lifecycle Benchmark Report

- run_id: `2cdf1a5e8e16468bbd3419438cf03149`
- benchmark: `m3_baseline_m4_repeated_neutral_subgraph`
- dataset: `dataframe`
- rows: `1000000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `0.384934`
- peak_rss_mb: `725.11`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `2cdf1a5e8e16468bbd3419438cf03149:batch:1` | `ordered_batch` | 1 | 0 | 0 | 10 | 0 | 0 | 9 | 0 | 1 | 0 | 725.11 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `2cdf1a5e8e16468bbd3419438cf03149:batch:1` | 19 | 11 | 4 | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 145.720 | 20.266 | 0.134 | 20.400 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `2cdf1a5e8e16468bbd3419438cf03149:batch:1` | `first_wave` | False | 0 | 0 | 0 | 0 | 0 | 0 | 0 | `` | True | True | 4 | 0.000 | 0 | 0.000 | 0 | 0 | 0 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `2cdf1a5e8e16468bbd3419438cf03149:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `neutral` | `None` | 1 | 2 | 2 | False | False |
