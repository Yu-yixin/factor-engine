# Stage Lifecycle Benchmark Report

- run_id: `2848c056b430405babb67030d622c227`
- benchmark: `r4_multi_consumer_dag_4_cse_off`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `4`
- total_time_sec: `13.403330`
- peak_rss_mb: `18042.76`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `2848c056b430405babb67030d622c227:batch:1` | `ordered_batch` | 4 | 0 | 0 | 9 | 0 | 0 | 9 | 0 | 4 | 0 | 18042.76 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | compute calls | store hits | hit rate | compute ms | store write ms | store hit ms | result store peak | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `2848c056b430405babb67030d622c227:batch:1` | 20 | 11 | 3 | 3 | 1 | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 4 | 6321.686 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `2848c056b430405babb67030d622c227:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `consumer_01` | `None` | 1 | 5 | 5 | False | False |
| `consumer_02` | `None` | 2 | 6 | 6 | False | False |
| `consumer_03` | `None` | 3 | 7 | 7 | False | False |
| `consumer_04` | `None` | 4 | 8 | 8 | False | False |
