# Stage Lifecycle Benchmark Report

- run_id: `38e4089a30f54795b110f0a75bd1c0c7`
- benchmark: `r4_multi_consumer_dag_8_cse_on`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `8`
- total_time_sec: `0.243080`
- peak_rss_mb: `684.12`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `38e4089a30f54795b110f0a75bd1c0c7:batch:1` | `ordered_batch` | 8 | 1 | 0 | 18 | 1 | 0 | 10 | 1 | 8 | 0 | 616.22 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `38e4089a30f54795b110f0a75bd1c0c7:batch:1` | 40 | 19 | 3 | 3 | 1 | 1 | 8 | 1 | 1 | 0 | 8 | 8 | 0.889 | 62.138 | 5.578 | 20.535 | 0.305 | 20.839 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `38e4089a30f54795b110f0a75bd1c0c7:batch:1` | 1 | 1 | 1 | 8000000 | 8000000 | 0 | 0 | 31 | 4.000 | 4 | 3.000 | 3 | 32000000 | 1 |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `38e4089a30f54795b110f0a75bd1c0c7:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000000 | 4 | 32000000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `38e4089a30f54795b110f0a75bd1c0c7:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `38e4089a30f54795b110f0a75bd1c0c7:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 10 | 10 | False | False |
| `consumer_02` | `None` | 2 | 11 | 11 | False | False |
| `consumer_03` | `None` | 3 | 12 | 12 | False | False |
| `consumer_04` | `None` | 4 | 13 | 13 | False | False |
| `consumer_05` | `None` | 5 | 14 | 14 | False | False |
| `consumer_06` | `None` | 6 | 15 | 15 | False | False |
| `consumer_07` | `None` | 7 | 16 | 16 | False | False |
| `consumer_08` | `None` | 8 | 17 | 17 | False | False |
