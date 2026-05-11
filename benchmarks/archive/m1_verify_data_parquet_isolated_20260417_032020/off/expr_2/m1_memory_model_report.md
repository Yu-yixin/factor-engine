# M1 Memory Model Benchmark

- rows: `29048679`
- lifecycle: `False`

| workload | exprs | total sec | peak rss mb | peak frame cols | peak output cols | peak stage cols | alive outputs | late outputs | native buffers | native peak bytes | release lag | recomputed | parallel | workers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| output_retention | 2 | 10.056489 | 7740.51 | 13 | 0 | 4 | 2 | 0 | 2 | 236020517 | 0 | 0 | True | 8 |
| frame_pressure | 2 | 14.712540 | 12801.58 | 15 | 0 | 6 | 2 | 0 | 0 | 0 | 0 | 0 | False | 1 |
| native_buffer | 2 | 10.382600 | 14442.23 | 13 | 0 | 4 | 2 | 0 | 2 | 236020517 | 0 | 0 | True | 8 |
