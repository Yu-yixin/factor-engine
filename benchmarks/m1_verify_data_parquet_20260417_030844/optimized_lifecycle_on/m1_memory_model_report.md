# M1 Memory Model Benchmark

- rows: `29048679`
- lifecycle: `True`

| workload | exprs | total sec | peak rss mb | peak frame cols | peak output cols | peak stage cols | alive outputs | late outputs | native buffers | native peak bytes | release lag | recomputed | parallel | workers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| output_retention | 1 | 9.482436 | 7327.45 | 11 | 0 | 2 | 1 | 0 | 1 | 236020517 | 0 | 0 | True | 8 |
| output_retention | 2 | 11.139269 | 14148.95 | 12 | 0 | 3 | 2 | 0 | 2 | 236020517 | 0 | 0 | True | 8 |
| output_retention | 4 | 13.652268 | 22117.75 | 14 | 0 | 5 | 4 | 0 | 4 | 236020517 | 0 | 0 | True | 8 |
| output_retention | 8 | 20.565877 | 22190.41 | 18 | 0 | 9 | 8 | 0 | 8 | 236020517 | 0 | 0 | True | 8 |
| frame_pressure | 1 | 14.921135 | 22261.68 | 12 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | False | 1 |
| frame_pressure | 2 | 18.450042 | 22329.95 | 15 | 0 | 6 | 2 | 0 | 0 | 0 | 0 | 0 | False | 1 |
| frame_pressure | 4 | 26.182814 | 22014.77 | 17 | 0 | 8 | 4 | 0 | 1 | 236020517 | 0 | 0 | True | 8 |
| frame_pressure | 8 | 36.081443 | 21814.75 | 25 | 0 | 16 | 8 | 0 | 2 | 236020517 | 0 | 0 | True | 8 |
| native_buffer | 1 | 9.903377 | 21774.24 | 11 | 0 | 2 | 1 | 0 | 1 | 236020517 | 0 | 0 | True | 8 |
| native_buffer | 2 | 11.387769 | 21581.11 | 12 | 0 | 3 | 2 | 0 | 2 | 236020517 | 0 | 0 | True | 8 |
| native_buffer | 4 | 14.883589 | 21698.95 | 14 | 0 | 5 | 4 | 0 | 4 | 236020517 | 0 | 0 | True | 8 |
| native_buffer | 8 | 19.168475 | 21748.50 | 18 | 0 | 9 | 8 | 0 | 8 | 236020517 | 0 | 0 | True | 8 |
