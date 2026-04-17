# Stage Lifecycle Benchmark Report

- run_id: `4de3956330414179afa709fb1ec5e83f`
- benchmark: `r4_multi_consumer_dag_8_cse_off`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `8`
- total_time_sec: `25.803105`
- peak_rss_mb: `18352.61`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `4de3956330414179afa709fb1ec5e83f:batch:1` | `ordered_batch` | 8 | 0 | 0 | 9 | 0 | 0 | 9 | 0 | 8 | 0 | 18352.61 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | compute calls | store hits | hit rate | compute ms | store write ms | store hit ms | result store peak | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `4de3956330414179afa709fb1ec5e83f:batch:1` | 40 | 19 | 3 | 3 | 1 | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 8 | 17597.566 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `4de3956330414179afa709fb1ec5e83f:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 9 | 9 | False | False |
| `consumer_02` | `None` | 2 | 10 | 10 | False | False |
| `consumer_03` | `None` | 3 | 11 | 11 | False | False |
| `consumer_04` | `None` | 4 | 12 | 12 | False | False |
| `consumer_05` | `None` | 5 | 13 | 13 | False | False |
| `consumer_06` | `None` | 6 | 14 | 14 | False | False |
| `consumer_07` | `None` | 7 | 15 | 15 | False | False |
| `consumer_08` | `None` | 8 | 16 | 16 | False | False |
