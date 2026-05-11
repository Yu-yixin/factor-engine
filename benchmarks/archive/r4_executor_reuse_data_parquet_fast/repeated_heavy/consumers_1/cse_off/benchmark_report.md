# Stage Lifecycle Benchmark Report

- run_id: `f8f73b4b6a67473db4cba16205657c9f`
- benchmark: `r4_repeated_heavy_1_cse_off`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `9.930581`
- peak_rss_mb: `6328.01`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `f8f73b4b6a67473db4cba16205657c9f:batch:1` | `ordered_batch` | 1 | 0 | 0 | 9 | 0 | 0 | 9 | 0 | 1 | 0 | 6328.01 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | compute calls | store hits | hit rate | compute ms | store write ms | store hit ms | result store peak | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `f8f73b4b6a67473db4cba16205657c9f:batch:1` | 3 | 3 | 0 | 0 | 0 | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 1 | 2064.709 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `f8f73b4b6a67473db4cba16205657c9f:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `repeated_heavy` | `None` | 1 | 2 | 2 | False | False |
