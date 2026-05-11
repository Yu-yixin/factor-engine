# M1 Memory Model Benchmark

- rows: `29048679`
- lifecycle: `False`

| workload | exprs | total sec | peak rss mb | peak frame cols | peak output cols | peak stage cols | alive outputs | late outputs | native buffers | native peak bytes | release lag | recomputed | parallel | workers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| output_retention | 4 | 12.053036 | 8639.29 | 15 | 0 | 6 | 4 | 0 | 4 | 236020517 | 0 | 0 | True | 8 |
| frame_pressure | 4 | 23.061226 | 14123.05 | 20 | 0 | 11 | 4 | 0 | 1 | 236020517 | 0 | 0 | True | 8 |
| native_buffer | 4 | 14.202545 | 17025.39 | 17 | 0 | 8 | 4 | 0 | 4 | 236020517 | 0 | 0 | True | 8 |
