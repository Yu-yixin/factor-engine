# Stage Lifecycle Benchmark Report

- run_id: `0284bf3741234c168fbfdee859e69847`
- benchmark: `r4_native_heavy_1_cse_off`
- dataset: `data.parquet`
- rows: `1000000`
- groups: `5470`
- expressions: `1`
- total_time_sec: `0.216555`
- peak_rss_mb: `345.96`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0284bf3741234c168fbfdee859e69847:batch:1` | `ordered_batch` | 1 | 2 | 0 | 11 | 2 | 0 | 11 | 2 | 1 | 8125000 | 345.92 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | compute calls | store hits | hit rate | compute ms | store write ms | store hit ms | result store peak | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0284bf3741234c168fbfdee859e69847:batch:1` | 3 | 3 | 0 | 0 | 0 | 1 | 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 1 | 17.467 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `0284bf3741234c168fbfdee859e69847:batch:1:stage:1` | `materialized_child` | `__stage_value` | 1 | True | False |
| `0284bf3741234c168fbfdee859e69847:batch:1:stage:2` | `positional_result` | `___stage_value` | 1 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `0284bf3741234c168fbfdee859e69847:batch:1` | 0 | 0 | 0 | 2 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `native_heavy` | `___stage_value` | 10 | 11 | 11 | False | False |

## Native Buffers

| buffer | output | bytes | created | attached | released | release lag | parallel | workers |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `0284bf3741234c168fbfdee859e69847:batch:1:native_buffer:1` | `native_heavy` | 8125000 | 4 | 5 | 6 | 0 | True | 8 |

## Positional Phases

| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `argmax` | 1000000 | 5470 | 10 | 2.972 | 6.606 | 12.299 | 0.353 | False | True | True | True |
