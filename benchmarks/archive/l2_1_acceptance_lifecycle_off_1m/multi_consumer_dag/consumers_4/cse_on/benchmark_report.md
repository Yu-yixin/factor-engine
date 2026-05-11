# Stage Lifecycle Benchmark Report

- run_id: `fdb4bcd8b5894313adfb93474d382ff8`
- benchmark: `r4_multi_consumer_dag_4_cse_on`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `4`
- total_time_sec: `0.232463`
- peak_rss_mb: `656.36`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fdb4bcd8b5894313adfb93474d382ff8:batch:1` | `ordered_batch` | 4 | 1 | 0 | 14 | 1 | 0 | 10 | 1 | 4 | 0 | 608.53 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fdb4bcd8b5894313adfb93474d382ff8:batch:1` | 20 | 11 | 3 | 3 | 1 | 1 | 4 | 1 | 1 | 0 | 4 | 4 | 0.800 | 52.595 | 5.384 | 23.762 | 0.275 | 24.036 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fdb4bcd8b5894313adfb93474d382ff8:batch:1` | 1 | 1 | 1 | 8000000 | 8000000 | 0 | 0 | 19 | 4.000 | 4 | 3.000 | 3 | 32000000 | 1 |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `fdb4bcd8b5894313adfb93474d382ff8:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000000 | 4 | 32000000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `fdb4bcd8b5894313adfb93474d382ff8:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `fdb4bcd8b5894313adfb93474d382ff8:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 6 | 6 | False | False |
| `consumer_02` | `None` | 2 | 7 | 7 | False | False |
| `consumer_03` | `None` | 3 | 8 | 8 | False | False |
| `consumer_04` | `None` | 4 | 9 | 9 | False | False |
