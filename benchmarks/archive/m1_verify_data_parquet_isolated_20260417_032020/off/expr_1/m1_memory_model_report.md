# M1 Memory Model Benchmark

- rows: `29048679`
- lifecycle: `False`

| workload | exprs | total sec | peak rss mb | peak frame cols | peak output cols | peak stage cols | alive outputs | late outputs | native buffers | native peak bytes | release lag | recomputed | parallel | workers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| output_retention | 1 | 10.815422 | 7293.25 | 11 | 0 | 2 | 1 | 0 | 1 | 236020517 | 0 | 0 | True | 8 |
| frame_pressure | 1 | 13.231909 | 12655.30 | 12 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | False | 1 |
| native_buffer | 1 | 9.394577 | 13653.56 | 11 | 0 | 2 | 1 | 0 | 1 | 236020517 | 0 | 0 | True | 8 |
