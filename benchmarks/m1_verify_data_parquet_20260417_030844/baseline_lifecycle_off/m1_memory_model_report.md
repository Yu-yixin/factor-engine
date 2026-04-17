# M1 Memory Model Benchmark

- rows: `29048679`
- lifecycle: `False`

| workload | exprs | total sec | peak rss mb | peak frame cols | peak output cols | peak stage cols | alive outputs | late outputs | native buffers | native peak bytes | release lag | recomputed | parallel | workers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| output_retention | 1 | 10.298963 | 7329.42 | 11 | 0 | 2 | 1 | 0 | 1 | 236020517 | 0 | 0 | True | 8 |
| output_retention | 2 | 12.324556 | 14150.77 | 13 | 0 | 4 | 2 | 0 | 2 | 236020517 | 0 | 0 | True | 8 |
| output_retention | 4 | 15.706175 | 20187.82 | 15 | 0 | 6 | 4 | 0 | 4 | 236020517 | 0 | 0 | True | 8 |
| output_retention | 8 | 24.463756 | 20552.73 | 19 | 0 | 10 | 8 | 0 | 8 | 236020517 | 0 | 0 | True | 8 |
| frame_pressure | 1 | 17.055855 | 20947.45 | 12 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | False | 1 |
| frame_pressure | 2 | 18.915998 | 21483.29 | 15 | 0 | 6 | 2 | 0 | 0 | 0 | 0 | 0 | False | 1 |
| frame_pressure | 4 | 27.834093 | 21729.02 | 20 | 0 | 11 | 4 | 0 | 1 | 236020517 | 0 | 0 | True | 8 |
| frame_pressure | 8 | 35.768043 | 21678.54 | 29 | 0 | 20 | 8 | 0 | 2 | 236020517 | 0 | 0 | True | 8 |
| native_buffer | 1 | 10.750106 | 21339.18 | 11 | 0 | 2 | 1 | 0 | 1 | 236020517 | 0 | 0 | True | 8 |
| native_buffer | 2 | 12.157818 | 21317.43 | 13 | 0 | 4 | 2 | 0 | 2 | 236020517 | 0 | 0 | True | 8 |
| native_buffer | 4 | 14.260560 | 21862.68 | 17 | 0 | 8 | 4 | 0 | 4 | 236020517 | 0 | 0 | True | 8 |
| native_buffer | 8 | 21.765507 | 21814.65 | 24 | 0 | 15 | 8 | 0 | 8 | 236020517 | 0 | 0 | True | 8 |
