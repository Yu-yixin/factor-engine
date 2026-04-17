# Stage Lifecycle Benchmark Report

- run_id: `fe3e6330d8be4b47b3ef825ef34cfab4`
- benchmark: `r4_multi_consumer_dag_2_cse_off`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `2`
- total_time_sec: `10.493340`
- peak_rss_mb: `16690.16`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fe3e6330d8be4b47b3ef825ef34cfab4:batch:1` | `ordered_batch` | 2 | 0 | 0 | 9 | 0 | 0 | 9 | 0 | 2 | 0 | 16690.16 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | compute calls | store hits | hit rate | compute ms | store write ms | store hit ms | result store peak | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fe3e6330d8be4b47b3ef825ef34cfab4:batch:1` | 10 | 7 | 3 | 3 | 1 | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 2 | 3636.885 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `fe3e6330d8be4b47b3ef825ef34cfab4:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 3 | 3 | False | False |
| `consumer_02` | `None` | 2 | 4 | 4 | False | False |
