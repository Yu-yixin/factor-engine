# Stage Profile (R17)

Date: 2026-04-14

## Stage Metrics

| stage | seconds | note |
| --- | ---: | --- |
| rolling_time | 5.881015 | time-ordered rolling batch path |
| io_time | 0.059779 | expression-file load plus parquet/csv write |
| segmented_time | 0.044382 | segmented batch path with prepared-view reuse |
| sorting_time | 0.039157 | Executor._get_prepared_frame across ordered families |
| grouped_time | 0.029392 | grouped cross-sectional batch path |
| parse_validate_compile_time | 0.004371 | cold planning for the full expression set |

## Top 3 Bottlenecks

- `rolling_time`: 5.881015s
- `io_time`: 0.059779s
- `segmented_time`: 0.044382s

## Scaling Snapshot (`evaluate_many()`) 

| label | rows | codes | expressions | seconds |
| --- | ---: | ---: | ---: | ---: |
| rows_s | 60,000 | 250 | 26 | 3.710903 |
| rows_m | 120,000 | 500 | 26 | 7.087649 |
| rows_l | 240,000 | 1,000 | 26 | 13.891150 |
| expr_half | 120,000 | 500 | 12 | 0.038000 |
| expr_full | 120,000 | 500 | 26 | 6.991746 |

## Observations

- Rows from 60k to 240k show near-linear growth in `evaluate_many()` wall time on this synthetic workload.
- Increasing expressions from 12 to the full set mainly amplifies ordered and segmented paths rather than file IO.
- The first optimization target should stay on high-share reusable stages before deeper kernel rewrites.
