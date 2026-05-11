# Stage Lifecycle Benchmark

This benchmark compares V1 profiling-only execution with V2 lifecycle sweep enabled.

| workload | rows | expressions | V1 peak cols | V2 peak cols | V1 alive end | V2 alive end | V2 dropped | V1 peak rss mb | V2 peak rss mb |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| stage_accumulation | 21600 | 6 | 23 | 16 | 11 | 0 | 11 | 74.46 | 79.78 |
| long_lived_stage | 21600 | 4 | 19 | 17 | 9 | 0 | 10 | 83.79 | 86.09 |

## Planned Lifecycle Metrics

| workload | V2 planned reusable | V2 avoided recompute | V2 recomputed | V2 late alive |
| --- | ---: | ---: | ---: | ---: |
| stage_accumulation | 3 | 3 | 0 | 0 |
| long_lived_stage | 0 | 0 | 1 | 0 |
