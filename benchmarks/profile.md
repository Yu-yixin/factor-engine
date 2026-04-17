# Stage Profile (R17)

Date: 2026-04-14

## Stage Metrics

| stage | seconds | note |
| --- | ---: | --- |
| rolling_time | 9.452593 | time-ordered rolling batch path |
| io_time | 0.160685 | expression-file load plus parquet/csv write |
| segmented_time | 0.076949 | segmented batch path with prepared-view reuse |
| grouped_time | 0.059392 | grouped cross-sectional batch path |
| sorting_time | 0.057193 | Executor._get_prepared_frame across ordered families |
| parse_validate_compile_time | 0.004215 | cold planning for the full expression set |

## Top 3 Bottlenecks

- `rolling_time`: 9.452593s
- `io_time`: 0.160685s
- `segmented_time`: 0.076949s

## Scaling Snapshot (`evaluate_many()`) 

| label | rows | codes | expressions | seconds |
| --- | ---: | ---: | ---: | ---: |
| rows_s | 60,000 | 250 | 26 | 4.261540 |
| rows_m | 120,000 | 500 | 26 | 9.039452 |
| rows_l | 240,000 | 1,000 | 26 | 19.128586 |
| expr_half | 120,000 | 500 | 12 | 0.042162 |
| expr_full | 120,000 | 500 | 26 | 9.522543 |

## Observations

- Rows from 60k to 240k show near-linear growth in `evaluate_many()` wall time on this synthetic workload.
- Increasing expressions from 12 to the full set mainly amplifies ordered and segmented paths rather than file IO.
- The first optimization target should stay on high-share reusable stages before deeper kernel rewrites.
