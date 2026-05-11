# R4 Executor-Native Reuse Benchmark

- data: `data.parquet`
- rows: `29048679`
- lifecycle: `False`

| workload | consumers | cse | sec | est no-reuse computes | attributed computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | lifecycle candidates | releasable | peak live nodes | before bytes | after bytes | dropped | misses | drop delay avg | overlap peak | drop order | nested order | partial safe | batch end step | structural lag | finalize lag | bytes-step savings | L2 first-wave | hit rate | materialized | store peak | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms | peak rss mb |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| multi_shared_nodes | 2 | False | 13.467383 | 4 | 4 | 0 | 4 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0 | `` | True | True | 13 | 0.000 | 0.000 | 0 | 0 | 0.000 | 2 | 1 | 0.000 | 5521.974 | 482.182 | 0.000 | 482.318 | 6263.89 |
| multi_shared_nodes | 2 | True | 10.888934 | 4 | 2 | 2 | 0 | 4 | 2 | 2 | 2 | 2 | 464778864 | 464778864 | 0 | 0 | 0.000 | 2 | `` | True | True | 13 | 4.000 | 3.000 | 1859115456 | 2 | 0.667 | 2 | 3 | 3089.151 | 86.580 | 448.009 | 0.000 | 448.225 | 11715.17 |
| nested_dag | 2 | False | 12.655447 | 4 | 2 | 0 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0 | `` | True | True | 10 | 0.000 | 0.000 | 0 | 0 | 0.000 | 2 | 1 | 0.000 | 5281.048 | 463.971 | 0.000 | 464.160 | 14200.33 |
| nested_dag | 2 | True | 9.652292 | 4 | 2 | 2 | 0 | 3 | 2 | 2 | 2 | 2 | 464778864 | 464778864 | 0 | 0 | 0.000 | 2 | `` | True | True | 10 | 5.000 | 4.000 | 2323894320 | 2 | 0.600 | 2 | 3 | 1969.567 | 30.944 | 489.151 | 0.000 | 489.361 | 14289.01 |
| partial_reuse | 2 | False | 10.184871 | 2 | 2 | 0 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0 | `` | True | True | 12 | 0.000 | 0.000 | 0 | 0 | 0.000 | 1 | 2 | 0.000 | 2365.721 | 477.879 | 0.000 | 478.213 | 15298.29 |
| partial_reuse | 2 | True | 9.884998 | 2 | 1 | 1 | 0 | 2 | 2 | 1 | 1 | 1 | 232389432 | 232389432 | 0 | 0 | 0.000 | 1 | `` | True | True | 12 | 4.000 | 3.000 | 929557728 | 1 | 0.667 | 1 | 3 | 504.529 | 1601.185 | 646.131 | 0.000 | 646.366 | 15537.04 |
