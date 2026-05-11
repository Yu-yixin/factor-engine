# Stage Lifecycle Benchmark Report

- run_id: `44f452c78fc24695a53c50c16e67a912`
- benchmark: `r4_multi_consumer_dag_2_cse_off`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `2`
- total_time_sec: `10.816189`
- peak_rss_mb: `15444.09`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `44f452c78fc24695a53c50c16e67a912:batch:1` | `ordered_batch` | 2 | 0 | 0 | 11 | 0 | 0 | 9 | 0 | 2 | 0 | 15444.09 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `44f452c78fc24695a53c50c16e67a912:batch:1` | 10 | 7 | 3 | 3 | 1 | 1 | 2 | 2 | 0 | 2 | 0 | 0 | 0.000 | 0.000 | 3508.134 | 525.528 | 0.242 | 525.770 |

## L1 Lifecycle Observability

| batch | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `44f452c78fc24695a53c50c16e67a912:batch:1` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 13 | 0.000 | 0 | 0.000 | 0 | 0 | 0 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `44f452c78fc24695a53c50c16e67a912:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 3 | 3 | False | False |
| `consumer_02` | `None` | 2 | 4 | 4 | False | False |
