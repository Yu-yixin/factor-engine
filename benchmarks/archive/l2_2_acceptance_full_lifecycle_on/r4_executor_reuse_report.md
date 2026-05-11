# R4 Executor-Native Reuse Benchmark

- data: `data.parquet`
- rows: `29048679`
- lifecycle: `True`

| workload | consumers | cse | sec | est no-reuse computes | attributed computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | lifecycle candidates | releasable | peak live nodes | before bytes | after bytes | dropped | misses | drop delay avg | overlap peak | drop order | nested order | partial safe | batch end step | structural lag | finalize lag | bytes-step savings | L2 first-wave | hit rate | materialized | store peak | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms | peak rss mb |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| multi_shared_nodes | 2 | False | 12.049118 | 4 | 4 | 0 | 4 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0 | `` | True | True | 13 | 0.000 | 0.000 | 0 | 0 | 0.000 | 2 | 1 | 0.000 | 5145.212 | 404.729 | 0.000 | 404.855 | 6263.40 |
| multi_shared_nodes | 2 | True | 10.560563 | 4 | 2 | 2 | 0 | 4 | 2 | 2 | 2 | 2 | 464778864 | 0 | 2 | 0 | 0.000 | 2 | `n3,n6` | True | True | 13 | 4.000 | 3.000 | 1859115456 | 2 | 0.667 | 2 | 2 | 3015.585 | 98.094 | 558.634 | 0.000 | 558.875 | 12200.30 |
| nested_dag | 2 | False | 12.749614 | 4 | 2 | 0 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0 | `` | True | True | 10 | 0.000 | 0.000 | 0 | 0 | 0.000 | 2 | 1 | 0.000 | 4892.191 | 366.176 | 0.000 | 366.432 | 14182.41 |
| nested_dag | 2 | True | 9.468943 | 4 | 2 | 2 | 0 | 3 | 2 | 2 | 2 | 2 | 464778864 | 0 | 2 | 0 | 0.000 | 2 | `n3,n4` | True | True | 10 | 5.000 | 4.000 | 2323894320 | 2 | 0.600 | 2 | 1 | 1847.582 | 25.556 | 441.310 | 0.000 | 441.405 | 14410.03 |
| partial_reuse | 2 | False | 9.866089 | 2 | 2 | 0 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0 | `` | True | True | 12 | 0.000 | 0.000 | 0 | 0 | 0.000 | 1 | 2 | 0.000 | 2202.814 | 448.476 | 0.000 | 448.752 | 15034.60 |
| partial_reuse | 2 | True | 10.704881 | 2 | 1 | 1 | 0 | 2 | 2 | 1 | 1 | 1 | 232389432 | 0 | 1 | 0 | 0.000 | 1 | `n3` | True | True | 12 | 4.000 | 3.000 | 929557728 | 1 | 0.667 | 1 | 2 | 499.223 | 1676.043 | 483.235 | 0.000 | 483.461 | 15235.04 |
