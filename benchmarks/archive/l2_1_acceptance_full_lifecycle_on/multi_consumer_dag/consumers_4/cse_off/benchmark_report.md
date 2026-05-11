# Stage Lifecycle Benchmark Report

- run_id: `9abd531c4c0d40f886ac74475908aba0`
- benchmark: `r4_multi_consumer_dag_4_cse_off`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `4`
- total_time_sec: `14.685391`
- peak_rss_mb: `16698.71`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `9abd531c4c0d40f886ac74475908aba0:batch:1` | `ordered_batch` | 4 | 0 | 0 | 13 | 0 | 0 | 9 | 0 | 4 | 0 | 16698.71 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `9abd531c4c0d40f886ac74475908aba0:batch:1` | 20 | 11 | 3 | 3 | 1 | 1 | 4 | 4 | 0 | 4 | 0 | 0 | 0.000 | 0.000 | 5992.866 | 646.705 | 0.334 | 647.038 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `9abd531c4c0d40f886ac74475908aba0:batch:1` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 19 | 0.000 | 0 | 0.000 | 0 | 0 | 0 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `9abd531c4c0d40f886ac74475908aba0:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 5 | 5 | False | False |
| `consumer_02` | `None` | 2 | 6 | 6 | False | False |
| `consumer_03` | `None` | 3 | 7 | 7 | False | False |
| `consumer_04` | `None` | 4 | 8 | 8 | False | False |
