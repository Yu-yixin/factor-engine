# Performance Truth Baseline

## Executive Summary

- top 5 slowest rolling operators: argmin, argmax, argmax, argmax, argmin
- top 5 memory-heavy cases: argmin_w20_n0p01_repeated_4=85.03 MB, argmin_w20_n0p01_single_1=84.51 MB, argmin_w20_n0p0_repeated_4=84.35 MB, argmin_w20_n0p0_single_1=84.05 MB, argmin_w5_n0p01_repeated_4=83.67 MB
- restore/finalize significance: UNKNOWN
- output_attach_mode peak width: UNKNOWN
- mixed segmented + ordered sorting: UNKNOWN

## Per-Operator Ranking

| Rank | Operator | Window | Null Rate | Rows | Time ms | Peak RSS MB | Backend | Notes |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | argmin | 20 | 0.01 | 2400 | 22.023 | 85.03 | python_fallback |  |
| 2 | argmax | 20 | 0.0 | 2400 | 21.249 | 81.64 | python_fallback |  |
| 3 | argmax | 5 | 0.0 | 2400 | 20.552 | 79.95 | python_fallback |  |
| 4 | argmax | 5 | 0.01 | 2400 | 20.489 | 80.48 | python_fallback |  |
| 5 | argmin | 5 | 0.0 | 2400 | 16.838 | 82.99 | python_fallback |  |
| 6 | argmin | 5 | 0.01 | 2400 | 16.449 | 83.67 | python_fallback |  |
| 7 | argmax | 20 | 0.01 | 2400 | 15.789 | 81.90 | python_fallback |  |
| 8 | argmin | 20 | 0.0 | 2400 | 14.996 | 84.35 | python_fallback |  |
| 9 | ts_rank | 20 | 0.01 | 2400 | 14.751 | 71.55 | polars |  |
| 10 | cov | 5 | 0.0 | 2400 | 14.356 | 74.79 | polars |  |
| 11 | kurt | 5 | 0.01 | 2400 | 13.790 | 78.13 | polars |  |
| 12 | kurt | 20 | 0.0 | 2400 | 13.230 | 78.10 | polars |  |
| 13 | corr | 20 | 0.01 | 2400 | 12.617 | 74.12 | polars |  |
| 14 | kurt | 20 | 0.01 | 2400 | 12.561 | 78.32 | polars |  |
| 15 | cov | 5 | 0.01 | 2400 | 12.160 | 75.29 | polars |  |
| 16 | kurt | 5 | 0.0 | 2400 | 12.154 | 77.89 | polars |  |
| 17 | argmin | 5 | 0.0 | 2400 | 11.890 | 82.46 | python_fallback |  |
| 18 | corr | 20 | 0.0 | 2400 | 11.572 | 73.57 | polars |  |
| 19 | cov | 20 | 0.0 | 2400 | 11.495 | 75.91 | polars |  |
| 20 | corr | 5 | 0.01 | 2400 | 11.306 | 73.28 | polars |  |
| 21 | corr | 5 | 0.0 | 2400 | 11.126 | 72.66 | polars |  |
| 22 | argmax | 5 | 0.0 | 2400 | 11.077 | 79.16 | python_fallback |  |
| 23 | ts_mean | 5 | 0.0 | 2400 | 11.023 | 61.29 | polars |  |
| 24 | argmin | 5 | 0.01 | 2400 | 10.875 | 83.13 | python_fallback |  |
| 25 | ts_mean | 5 | 0.01 | 2400 | 10.588 | 62.52 | polars |  |
| 26 | ts_std | 20 | 0.0 | 2400 | 10.499 | 65.11 | polars |  |
| 27 | ts_sum | 20 | 0.01 | 2400 | 10.193 | 67.06 | polars |  |
| 28 | ts_max | 5 | 0.01 | 2400 | 10.102 | 69.34 | polars |  |
| 29 | argmax | 5 | 0.01 | 2400 | 10.020 | 80.04 | python_fallback |  |
| 30 | ts_mean | 20 | 0.01 | 2400 | 10.019 | 63.82 | polars |  |
| 31 | ts_sum | 5 | 0.0 | 2400 | 9.908 | 65.87 | polars |  |
| 32 | ts_max | 20 | 0.0 | 2400 | 9.899 | 69.34 | polars |  |
| 33 | ts_std | 5 | 0.01 | 2400 | 9.784 | 64.74 | polars |  |
| 34 | ts_rank | 20 | 0.0 | 2400 | 9.759 | 71.15 | polars |  |
| 35 | cov | 20 | 0.01 | 2400 | 9.683 | 76.36 | polars |  |
| 36 | ts_min | 5 | 0.01 | 2400 | 9.666 | 67.97 | polars |  |
| 37 | skew | 20 | 0.0 | 2400 | 9.659 | 77.05 | polars |  |
| 38 | ts_min | 20 | 0.01 | 2400 | 9.628 | 68.50 | polars |  |
| 39 | argmin | 20 | 0.0 | 2400 | 9.625 | 84.05 | python_fallback |  |
| 40 | ts_min | 20 | 0.0 | 2400 | 9.616 | 68.13 | polars |  |
| 41 | skew | 20 | 0.01 | 2400 | 9.615 | 77.30 | polars |  |
| 42 | ts_sum | 20 | 0.0 | 2400 | 9.568 | 66.88 | polars |  |
| 43 | ts_rank | 5 | 0.01 | 2400 | 9.516 | 70.86 | polars |  |
| 44 | ts_mean | 20 | 0.0 | 2400 | 9.465 | 63.27 | polars |  |
| 45 | ts_std | 5 | 0.0 | 2400 | 9.422 | 64.37 | polars |  |
| 46 | ts_max | 5 | 0.0 | 2400 | 9.335 | 69.02 | polars |  |
| 47 | ts_std | 20 | 0.01 | 2400 | 9.326 | 65.51 | polars |  |
| 48 | ts_max | 20 | 0.01 | 2400 | 9.255 | 70.01 | polars |  |
| 49 | skew | 5 | 0.01 | 2400 | 9.172 | 76.91 | polars |  |
| 50 | ts_min | 5 | 0.0 | 2400 | 9.149 | 67.54 | polars |  |
| 51 | skew | 5 | 0.0 | 2400 | 9.139 | 76.44 | polars |  |
| 52 | ts_rank | 5 | 0.0 | 2400 | 9.092 | 70.30 | polars |  |
| 53 | ts_sum | 5 | 0.01 | 2400 | 8.927 | 66.06 | polars |  |
| 54 | argmax | 20 | 0.0 | 2400 | 8.757 | 81.27 | python_fallback |  |
| 55 | corr | 20 | 0.01 | 2400 | 8.695 | 73.70 | polars |  |
| 56 | argmin | 20 | 0.01 | 2400 | 8.470 | 84.51 | python_fallback |  |
| 57 | ts_min | 20 | 0.01 | 2400 | 8.360 | 68.42 | polars |  |
| 58 | argmax | 20 | 0.01 | 2400 | 8.304 | 81.67 | python_fallback |  |
| 59 | cov | 5 | 0.01 | 2400 | 8.143 | 75.10 | polars |  |
| 60 | kurt | 5 | 0.0 | 2400 | 7.763 | 77.32 | polars |  |
| 61 | kurt | 20 | 0.0 | 2400 | 7.177 | 78.11 | polars |  |
| 62 | ts_mean | 5 | 0.0 | 2400 | 7.003 | 60.03 | polars |  |
| 63 | cov | 20 | 0.0 | 2400 | 6.809 | 75.46 | polars |  |
| 64 | cov | 20 | 0.01 | 2400 | 6.795 | 76.04 | polars |  |
| 65 | kurt | 20 | 0.01 | 2400 | 6.707 | 78.36 | polars |  |
| 66 | cov | 5 | 0.0 | 2400 | 6.485 | 74.54 | polars |  |
| 67 | corr | 5 | 0.0 | 2400 | 6.160 | 72.10 | polars |  |
| 68 | ts_std | 5 | 0.01 | 2400 | 6.122 | 64.48 | polars |  |
| 69 | ts_rank | 20 | 0.0 | 2400 | 6.063 | 71.05 | polars |  |
| 70 | corr | 5 | 0.01 | 2400 | 6.001 | 72.95 | polars |  |
| 71 | ts_max | 5 | 0.0 | 2400 | 5.893 | 68.83 | polars |  |
| 72 | corr | 20 | 0.0 | 2400 | 5.866 | 73.36 | polars |  |
| 73 | ts_max | 20 | 0.01 | 2400 | 5.782 | 69.91 | polars |  |
| 74 | ts_std | 20 | 0.01 | 2400 | 5.781 | 65.33 | polars |  |
| 75 | ts_mean | 5 | 0.01 | 2400 | 5.657 | 62.04 | polars |  |
| 76 | ts_rank | 5 | 0.0 | 2400 | 5.612 | 70.17 | polars |  |
| 77 | ts_sum | 20 | 0.0 | 2400 | 5.491 | 66.45 | polars |  |
| 78 | ts_sum | 20 | 0.01 | 2400 | 5.389 | 66.97 | polars |  |
| 79 | ts_sum | 5 | 0.0 | 2400 | 5.380 | 65.54 | polars |  |
| 80 | skew | 5 | 0.01 | 2400 | 5.310 | 76.48 | polars |  |
| 81 | ts_mean | 20 | 0.0 | 2400 | 5.294 | 62.84 | polars |  |
| 82 | ts_std | 5 | 0.0 | 2400 | 5.189 | 63.98 | polars |  |
| 83 | ts_rank | 5 | 0.01 | 2400 | 5.129 | 70.43 | polars |  |
| 84 | ts_max | 5 | 0.01 | 2400 | 5.127 | 69.16 | polars |  |
| 85 | kurt | 5 | 0.01 | 2400 | 5.086 | 77.98 | polars |  |
| 86 | ts_sum | 5 | 0.01 | 2400 | 5.072 | 66.02 | polars |  |
| 87 | ts_max | 20 | 0.0 | 2400 | 5.036 | 69.29 | polars |  |
| 88 | ts_min | 5 | 0.01 | 2400 | 5.014 | 67.70 | polars |  |
| 89 | ts_mean | 20 | 0.01 | 2400 | 4.993 | 63.53 | polars |  |
| 90 | ts_std | 20 | 0.0 | 2400 | 4.945 | 65.00 | polars |  |
| 91 | ts_min | 20 | 0.0 | 2400 | 4.944 | 68.03 | polars |  |
| 92 | skew | 20 | 0.01 | 2400 | 4.914 | 77.13 | polars |  |
| 93 | ts_rank | 20 | 0.01 | 2400 | 4.849 | 71.18 | polars |  |
| 94 | ts_min | 5 | 0.0 | 2400 | 4.801 | 67.10 | polars |  |
| 95 | skew | 20 | 0.0 | 2400 | 4.707 | 76.96 | polars |  |
| 96 | skew | 5 | 0.0 | 2400 | 4.682 | 76.48 | polars |  |

## Restore / Finalize Ranking

| Case | Attach Mode | Expressions | Total ms | Restore ms | Finalize ms | Peak Frame Cols | Peak RSS MB |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| UNKNOWN | UNKNOWN |  |  |  |  |  | no finalize benchmark artifact found |

## Mixed Route Sorting Findings

| Case | Prepare Sort Count | Prepare Sort ms | Total ms | Evidence | Conclusion |
| --- | ---: | ---: | ---: | --- | --- |
| UNKNOWN |  |  |  | no mixed sorting benchmark artifact found | UNKNOWN |

## Optimization Decision

| Candidate | Classification | Basis |
| --- | --- | --- |
| native ts_rank | MEASURE_MORE | not proven top-5 in current run |
| native corr/cov shared moments | MEASURE_MORE | shared-moment benefit remains UNKNOWN |
| restore/finalize optimization | MEASURE_MORE | restore/finalize significance not established |
| output attach default mode change | DO_NOT_TOUCH_YET | no measured peak-width case for changing default |
| mixed segmented+ordered prepared-frame reuse | MEASURE_MORE | repeated sorting evidence is UNKNOWN/not observed |
| broader CSE expansion | DO_NOT_TOUCH_YET | no measured CSE pressure in current report |
| native-heavy active drop | DO_NOT_TOUCH_YET | no measured native-heavy pressure in current report |

Rules applied: bottlenecks are reported only from measured rows; unavailable profile fields are shown as FIELD_NOT_AVAILABLE; guessed causes are marked HYPOTHESIS.
