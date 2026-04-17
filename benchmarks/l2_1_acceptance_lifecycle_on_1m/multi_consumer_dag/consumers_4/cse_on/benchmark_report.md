# Stage Lifecycle Benchmark Report

- run_id: `81ca960e38804d228a102f67e51ea5d4`
- benchmark: `r4_multi_consumer_dag_4_cse_on`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `4`
- total_time_sec: `0.231154`
- peak_rss_mb: `613.51`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `81ca960e38804d228a102f67e51ea5d4:batch:1` | `ordered_batch` | 4 | 1 | 1 | 14 | 1 | 0 | 9 | 0 | 4 | 0 | 540.30 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `81ca960e38804d228a102f67e51ea5d4:batch:1` | 20 | 11 | 3 | 3 | 1 | 1 | 4 | 1 | 1 | 0 | 4 | 4 | 0.800 | 62.055 | 5.899 | 19.618 | 0.204 | 19.822 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `81ca960e38804d228a102f67e51ea5d4:batch:1` | 1 | 1 | 1 | 8000000 | 0 | 1 | 0 | 19 | 4.000 | 4 | 3.000 | 3 | 32000000 | 1 |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `81ca960e38804d228a102f67e51ea5d4:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000000 | 4 | 32000000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `81ca960e38804d228a102f67e51ea5d4:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | False | True |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `81ca960e38804d228a102f67e51ea5d4:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 7 | 7 | False | False |
| `consumer_02` | `None` | 2 | 8 | 8 | False | False |
| `consumer_03` | `None` | 3 | 9 | 9 | False | False |
| `consumer_04` | `None` | 4 | 10 | 10 | False | False |
