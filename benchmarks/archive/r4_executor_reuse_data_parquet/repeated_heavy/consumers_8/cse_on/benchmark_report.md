# Stage Lifecycle Benchmark Report

- run_id: `0971ae19f1814a319ee9fd02ec2ad6af`
- benchmark: `r4_repeated_heavy_8_cse_on`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `10.520263`
- peak_rss_mb: `15419.59`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0971ae19f1814a319ee9fd02ec2ad6af:batch:1` | `ordered_batch` | 1 | 1 | 0 | 10 | 1 | 0 | 10 | 1 | 1 | 0 | 15419.59 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | compute calls | store hits | hit rate | compute ms | store write ms | store hit ms | result store peak | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0971ae19f1814a319ee9fd02ec2ad6af:batch:1` | 31 | 10 | 3 | 3 | 1 | 1 | 1 | 8 | 0.889 | 1831.633 | 0.011 | 0.000 | 2 | 808.498 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `0971ae19f1814a319ee9fd02ec2ad6af:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `0971ae19f1814a319ee9fd02ec2ad6af:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `repeated_heavy` | `None` | 1 | 3 | 3 | False | False |
