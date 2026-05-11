# Stage Lifecycle Benchmark Report

- run_id: `54646c8807b2428b94a685ac2c07b162`
- benchmark: `r4_native_heavy_4_cse_on`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `2.543734`
- peak_rss_mb: `701.07`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `54646c8807b2428b94a685ac2c07b162:batch:1` | `ordered_batch` | 1 | 1 | 1 | 11 | 1 | 0 | 9 | 0 | 1 | 0 | 697.05 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `54646c8807b2428b94a685ac2c07b162:batch:1` | 15 | 6 | 3 | 3 | 1 | 1 | 4 | 1 | 1 | 0 | 4 | 1 | 0.800 | 2417.882 | 2.783 | 13.542 | 0.095 | 13.637 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `54646c8807b2428b94a685ac2c07b162:batch:1` | 1 | 1 | 1 | 8000000 | 8000000 | 0 | 0 | 11 | 4.000 | 4 | 3.000 | 3 | 32000000 | 0 |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `54646c8807b2428b94a685ac2c07b162:batch:1` | `native_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000000 | 4 | 32000000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `54646c8807b2428b94a685ac2c07b162:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `54646c8807b2428b94a685ac2c07b162:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `native_heavy` | `None` | 1 | 4 | 4 | False | False |
