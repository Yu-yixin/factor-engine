# Stage Lifecycle Benchmark Report

- run_id: `c0f2abf39e0c48d4bbd513cc8ea8a4eb`
- benchmark: `r4_native_heavy_multi_read_2_cse_off`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `4.651797`
- peak_rss_mb: `699.53`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `c0f2abf39e0c48d4bbd513cc8ea8a4eb:batch:1` | `ordered_batch` | 1 | 0 | 0 | 10 | 0 | 0 | 9 | 0 | 1 | 0 | 699.53 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `c0f2abf39e0c48d4bbd513cc8ea8a4eb:batch:1` | 7 | 4 | 3 | 3 | 1 | 1 | 2 | 2 | 0 | 2 | 0 | 0 | 0.000 | 0.000 | 4530.688 | 15.171 | 0.074 | 15.246 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `c0f2abf39e0c48d4bbd513cc8ea8a4eb:batch:1` | `off` | False | 1 | 0 | 0 | 0 | 0 | 0 | 0 | `` | True | True | 9 | 0.000 | 0 | 0.000 | 0 | 0 | 0 |

## L3A Native-Heavy Lifecycle Observability

| batch | native nodes | forbidden | observable only | candidate future | native compute ms | path normalization ms | storage bytes | store reads | logical consumers | effective uses | fallback evals | rewrites | helper patterns |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `c0f2abf39e0c48d4bbd513cc8ea8a4eb:batch:1` | 1 | 1 | 0 | 0 | 0.000 | 0.000 | 0 | 0 | 0 | 0 | 1 | 0 | `unread` |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `c0f2abf39e0c48d4bbd513cc8ea8a4eb:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `native_heavy_multi_read` | `None` | 1 | 2 | 2 | False | False |
