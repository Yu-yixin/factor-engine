# M1 Memory Model Benchmark

- rows: `29048679`
- lifecycle: `True`

| workload | exprs | total sec | peak rss mb | peak frame cols | peak output cols | peak stage cols | alive outputs | late outputs | native buffers | native peak bytes | release lag | recomputed | parallel | workers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| output_retention | 2 | 10.985548 | 7613.46 | 12 | 0 | 3 | 2 | 0 | 2 | 236020517 | 0 | 0 | True | 8 |
| frame_pressure | 2 | 15.892734 | 13068.51 | 15 | 0 | 6 | 2 | 0 | 0 | 0 | 0 | 0 | False | 1 |
| native_buffer | 2 | 13.803478 | 14567.29 | 12 | 0 | 3 | 2 | 0 | 2 | 236020517 | 0 | 0 | True | 8 |
