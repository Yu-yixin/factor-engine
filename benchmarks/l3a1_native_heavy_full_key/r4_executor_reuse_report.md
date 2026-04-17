# R4 Executor-Native Reuse Benchmark

- data: `data.parquet`
- rows: `29048679`
- lifecycle: `False`
- lifecycle mode: `off`

| workload | consumers | cse | lifecycle mode | lifecycle effective | sec | est no-reuse computes | attributed computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | native nodes | native eligibility | native compute ms | native path ms | native storage bytes | native reads | native logical consumers | native effective uses | native fallback evals | native rewrites | native helper patterns | lifecycle candidates | releasable | peak live nodes | before bytes | after bytes | dropped | misses | drop delay avg | overlap peak | drop order | nested order | partial safe | batch end step | structural lag | finalize lag | bytes-step savings | L2 first-wave | hit rate | materialized | store peak | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms | peak rss mb |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| native_heavy_multi_read | 2 | False | off | False | 130.283254 | 2 | 2 | 0 | 2 | 0 | 0 | 1 | F:1/O:0/C:0 | 0.000 | 0.000 | 0 | 0 | 0 | 0 | 1 | 0 | `unread` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0 | `` | True | True | 9 | 0.000 | 0.000 | 0 | 0 | 0.000 | 1 | 1 | 0.000 | 123293.567 | 324.446 | 0.000 | 324.567 | 16421.30 |
| native_heavy_multi_read | 2 | True | off | False | 71.879247 | 2 | 1 | 1 | 0 | 2 | 1 | 1 | F:0/O:1/C:0 | 63726.643 | 0.000 | 232389432 | 2 | 1 | 2 | 0 | 1 | `single_consumer_multi_read` | 1 | 1 | 1 | 232389432 | 232389432 | 0 | 0 | 0.000 | 1 | `` | True | True | 9 | 4.000 | 3.000 | 929557728 | 0 | 0.667 | 1 | 2 | 63726.643 | 33.865 | 316.505 | 0.000 | 316.609 | 19142.27 |
