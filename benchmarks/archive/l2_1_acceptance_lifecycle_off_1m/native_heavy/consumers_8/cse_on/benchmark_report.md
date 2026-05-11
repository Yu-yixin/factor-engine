# Stage Lifecycle Benchmark Report

- run_id: `f921dd8c31e64724ba501d4181e8613a`
- benchmark: `r4_native_heavy_8_cse_on`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `2.328493`
- peak_rss_mb: `837.11`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `f921dd8c31e64724ba501d4181e8613a:batch:1` | `ordered_batch` | 1 | 1 | 0 | 11 | 1 | 0 | 10 | 1 | 1 | 0 | 834.74 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `f921dd8c31e64724ba501d4181e8613a:batch:1` | 31 | 10 | 3 | 3 | 1 | 1 | 8 | 1 | 1 | 0 | 8 | 1 | 0.889 | 2193.474 | 7.634 | 20.119 | 0.116 | 20.235 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `f921dd8c31e64724ba501d4181e8613a:batch:1` | 1 | 1 | 1 | 8000000 | 8000000 | 0 | 0 | 15 | 4.000 | 4 | 3.000 | 3 | 32000000 | 0 |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `f921dd8c31e64724ba501d4181e8613a:batch:1` | `native_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000000 | 4 | 32000000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `f921dd8c31e64724ba501d4181e8613a:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `f921dd8c31e64724ba501d4181e8613a:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `native_heavy` | `None` | 1 | 3 | 3 | False | False |
