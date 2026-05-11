# Stage Lifecycle Benchmark Report

- run_id: `cd81bd1f8b394750bf9d5c846701f28c`
- benchmark: `r4_nested_probe_c_2_cse_off`
- dataset: `data.parquet`
- rows: `1000`
- groups: `1000`
- expressions: `1`
- total_time_sec: `0.013390`
- peak_rss_mb: `67.62`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `cd81bd1f8b394750bf9d5c846701f28c:batch:1` | `ordered_batch` | 1 | 0 | 0 | 10 | 0 | 0 | 9 | 0 | 1 | 0 | 67.62 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `cd81bd1f8b394750bf9d5c846701f28c:batch:1` | 11 | 6 | 3 | 3 | 1 | 3 | 2 | 2 | 0 | 2 | 0 | 0 | 0.000 | 0.000 | 4.690 | 0.446 | 0.092 | 0.538 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `cd81bd1f8b394750bf9d5c846701f28c:batch:1` | `first_wave` | False | 1 | 0 | 0 | 0 | 0 | 0 | 0 | `` | True | True | 11 | 0.000 | 0 | 0.000 | 0 | 0 | 0 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `cd81bd1f8b394750bf9d5c846701f28c:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `nested_probe_c` | `None` | 1 | 2 | 2 | False | False |
