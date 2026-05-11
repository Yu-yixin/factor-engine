# Stage Lifecycle Benchmark Report

- run_id: `b8d705c89f9e47a89605bec02939e0b2`
- benchmark: `r4_native_heavy_2_cse_on`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `2.946620`
- peak_rss_mb: `788.00`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `b8d705c89f9e47a89605bec02939e0b2:batch:1` | `ordered_batch` | 1 | 1 | 0 | 10 | 1 | 0 | 10 | 1 | 1 | 0 | 782.70 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | compute calls | store hits | hit rate | compute ms | store write ms | store hit ms | result store peak | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `b8d705c89f9e47a89605bec02939e0b2:batch:1` | 7 | 4 | 3 | 3 | 1 | 1 | 1 | 2 | 0.667 | 2793.725 | 0.016 | 0.000 | 2 | 20.560 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `b8d705c89f9e47a89605bec02939e0b2:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `b8d705c89f9e47a89605bec02939e0b2:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `native_heavy` | `None` | 1 | 3 | 3 | False | False |
