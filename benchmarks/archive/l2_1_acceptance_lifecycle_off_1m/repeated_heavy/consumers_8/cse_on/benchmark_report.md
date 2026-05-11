# Stage Lifecycle Benchmark Report

- run_id: `bd281c6c3d2c4c9ba87c17fd915816a4`
- benchmark: `r4_repeated_heavy_8_cse_on`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `0.221198`
- peak_rss_mb: `566.17`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `bd281c6c3d2c4c9ba87c17fd915816a4:batch:1` | `ordered_batch` | 1 | 1 | 0 | 11 | 1 | 0 | 10 | 1 | 1 | 0 | 520.57 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `bd281c6c3d2c4c9ba87c17fd915816a4:batch:1` | 31 | 10 | 3 | 3 | 1 | 1 | 8 | 1 | 1 | 0 | 8 | 1 | 0.889 | 48.560 | 9.943 | 22.016 | 0.128 | 22.144 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `bd281c6c3d2c4c9ba87c17fd915816a4:batch:1` | 1 | 1 | 1 | 8000000 | 8000000 | 0 | 0 | 15 | 4.000 | 4 | 3.000 | 3 | 32000000 | 1 |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `bd281c6c3d2c4c9ba87c17fd915816a4:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000000 | 4 | 32000000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `bd281c6c3d2c4c9ba87c17fd915816a4:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `bd281c6c3d2c4c9ba87c17fd915816a4:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `repeated_heavy` | `None` | 1 | 3 | 3 | False | False |
