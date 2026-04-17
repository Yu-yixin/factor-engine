# R4 Executor-Native Reuse Benchmark

- data: `data.parquet`
- rows: `1000000`

| workload | consumers | cse | sec | est no-reuse computes | actual computes | store hits | hit rate | materialized | store peak | compute ms | store write ms | store hit ms | finalize ms | peak rss mb |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| native_heavy | 1 | False | 0.216555 | 0 | 0 | 0 | 0.000 | 0 | 1 | 0.000 | 0.000 | 0.000 | 17.467 | 345.96 |
| native_heavy | 1 | True | 0.202343 | 0 | 0 | 0 | 0.000 | 0 | 1 | 0.000 | 0.000 | 0.000 | 28.330 | 578.20 |
| native_heavy | 2 | False | 5.350934 | 2 | 0 | 0 | 0.000 | 1 | 1 | 0.000 | 0.000 | 0.000 | 5171.966 | 797.23 |
| native_heavy | 2 | True | 2.946620 | 2 | 1 | 2 | 0.667 | 1 | 2 | 2793.725 | 0.016 | 0.000 | 20.560 | 788.00 |
