# R4 Executor-Native Reuse Benchmark

- data: `data.parquet`
- rows: `1000000`

| workload | consumers | cse | sec | est no-reuse computes | attributed computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | lifecycle candidates | releasable | peak live nodes | avg lag | max lag | hit rate | materialized | store peak | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms | peak rss mb |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| repeated_heavy | 8 | False | 0.455592 | 8 | 8 | 0 | 8 | 0 | 0 | 1 | 0 | 0 | 0.000 | 0 | 0.000 | 1 | 1 | 0.000 | 338.912 | 14.360 | 0.000 | 14.459 | 309.49 |
| repeated_heavy | 8 | True | 0.174878 | 8 | 1 | 1 | 0 | 8 | 1 | 1 | 1 | 1 | 0.000 | 0 | 0.889 | 1 | 2 | 41.268 | 5.598 | 13.846 | 0.000 | 13.950 | 513.39 |
| multi_consumer_dag | 8 | False | 0.695647 | 8 | 8 | 0 | 8 | 0 | 0 | 1 | 0 | 0 | 0.000 | 0 | 0.000 | 1 | 8 | 0.000 | 561.228 | 23.025 | 0.000 | 23.220 | 537.42 |
| multi_consumer_dag | 8 | True | 0.240777 | 8 | 1 | 1 | 0 | 8 | 8 | 1 | 1 | 1 | 0.000 | 0 | 0.889 | 1 | 9 | 62.823 | 7.408 | 28.836 | 0.000 | 29.059 | 594.36 |
| native_heavy | 8 | False | 17.045493 | 8 | 8 | 0 | 8 | 0 | 0 | 1 | 0 | 0 | 0.000 | 0 | 0.000 | 1 | 1 | 0.000 | 16898.262 | 16.507 | 0.000 | 16.594 | 600.68 |
| native_heavy | 8 | True | 2.318875 | 8 | 1 | 1 | 0 | 8 | 1 | 1 | 1 | 1 | 0.000 | 0 | 0.889 | 1 | 2 | 2144.885 | 6.530 | 11.976 | 0.000 | 12.085 | 627.55 |
