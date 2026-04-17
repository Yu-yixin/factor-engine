# Stage Lifecycle Benchmark Report

- run_id: `921706afa44a45989a385d7a8777daec`
- benchmark: `r4_repeated_heavy_4_cse_on`
- dataset: `data.parquet`
- rows: `29048679`
- groups: `5495`
- expressions: `1`
- total_time_sec: `12.275439`
- peak_rss_mb: `15854.33`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `921706afa44a45989a385d7a8777daec:batch:1` | `ordered_batch` | 1 | 1 | 0 | 10 | 1 | 0 | 10 | 1 | 1 | 0 | 15854.33 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | compute calls | store hits | hit rate | compute ms | store write ms | store hit ms | result store peak | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `921706afa44a45989a385d7a8777daec:batch:1` | 15 | 6 | 3 | 3 | 1 | 1 | 1 | 4 | 0.800 | 2037.808 | 0.051 | 0.000 | 2 | 940.561 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `921706afa44a45989a385d7a8777daec:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `921706afa44a45989a385d7a8777daec:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `repeated_heavy` | `None` | 1 | 3 | 3 | False | False |
