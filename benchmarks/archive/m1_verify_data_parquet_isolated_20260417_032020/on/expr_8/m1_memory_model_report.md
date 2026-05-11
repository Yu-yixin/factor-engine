# M1 Memory Model Benchmark

- rows: `29048679`
- lifecycle: `True`

| workload | exprs | total sec | peak rss mb | peak frame cols | peak output cols | peak stage cols | alive outputs | late outputs | native buffers | native peak bytes | release lag | recomputed | parallel | workers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| output_retention | 8 | 17.965884 | 10267.54 | 18 | 0 | 9 | 8 | 0 | 8 | 236020517 | 0 | 0 | True | 8 |
| frame_pressure | 8 | 43.308632 | 13984.25 | 25 | 0 | 16 | 8 | 0 | 2 | 236020517 | 0 | 0 | True | 8 |
| native_buffer | 8 | 24.451340 | 20157.99 | 18 | 0 | 9 | 8 | 0 | 8 | 236020517 | 0 | 0 | True | 8 |
