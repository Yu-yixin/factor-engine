# M1 Memory Model Benchmark

- rows: `29048679`
- lifecycle: `False`

| workload | exprs | total sec | peak rss mb | peak frame cols | peak output cols | peak stage cols | alive outputs | late outputs | native buffers | native peak bytes | release lag | recomputed | parallel | workers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| output_retention | 8 | 16.947360 | 10278.78 | 19 | 0 | 10 | 8 | 0 | 8 | 236020517 | 0 | 0 | True | 8 |
| frame_pressure | 8 | 36.230987 | 14298.18 | 29 | 0 | 20 | 8 | 0 | 2 | 236020517 | 0 | 0 | True | 8 |
| native_buffer | 8 | 21.878157 | 20669.53 | 24 | 0 | 15 | 8 | 0 | 8 | 236020517 | 0 | 0 | True | 8 |
