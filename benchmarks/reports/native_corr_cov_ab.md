# Native corr/cov A/B Report

Decision: `REJECT`

Reason: median_speedup=0.427, worst_native_cv=0.000

Full requested matrix: `NOT_RUN`. Reduced scale is documented here when used.

| rows | codes | window | null_rate | mode | native_used | polars median ms | native median ms | speedup | status |
| ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | --- |
| 24000 | 40 | 5 | 0.0 | corr | True | 3.298 | 7.717 | 0.427 | RUN |
| 24000 | 40 | 20 | 0.01 | cov | True | 1.793 | 7.097 | 0.253 | RUN |
| 24000 | 250 | 60 | 0.1 | corr | True | 3.749 | 6.988 | 0.536 | RUN |

Acceptance rule: correctness must pass, median speedup must be at least 1.25x, CV must be at most 0.15, peak RSS must not materially regress, and fallback must be safe.

This report uses total wall time for each callable path. Kernel-only time is not treated as sufficient evidence.
