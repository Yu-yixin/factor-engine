# M1 Memory Model Benchmark

- rows: `29048679`
- lifecycle: `True`

| workload | exprs | total sec | peak rss mb | peak frame cols | peak output cols | peak stage cols | alive outputs | late outputs | native buffers | native peak bytes | release lag | recomputed | parallel | workers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| output_retention | 4 | 12.252674 | 8672.41 | 14 | 0 | 5 | 4 | 0 | 4 | 236020517 | 0 | 0 | True | 8 |
| frame_pressure | 4 | 22.596266 | 13412.14 | 17 | 0 | 8 | 4 | 0 | 1 | 236020517 | 0 | 0 | True | 8 |
| native_buffer | 4 | 15.273554 | 17679.65 | 14 | 0 | 5 | 4 | 0 | 4 | 236020517 | 0 | 0 | True | 8 |
