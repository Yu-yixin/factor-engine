# M1 Memory Model Benchmark

- rows: `2560`
- lifecycle: `False`

| workload | exprs | total sec | peak rss mb | peak frame cols | peak output cols | peak stage cols | alive outputs | late outputs | native buffers | native peak bytes | release lag | recomputed | parallel | workers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| output_retention | 1 | 0.018133 | 59.90 | 8 | 0 | 2 | 1 | 0 | 1 | 20800 | 0 | 0 | True | 8 |
| output_retention | 2 | 0.023514 | 61.52 | 10 | 0 | 4 | 2 | 0 | 2 | 20800 | 0 | 0 | True | 8 |
| output_retention | 4 | 0.047534 | 63.01 | 12 | 0 | 6 | 4 | 0 | 4 | 20800 | 0 | 0 | True | 8 |
| output_retention | 8 | 0.063979 | 65.06 | 16 | 0 | 10 | 8 | 0 | 8 | 20800 | 0 | 0 | True | 8 |
| frame_pressure | 1 | 0.015054 | 66.46 | 9 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | False | 1 |
| frame_pressure | 2 | 0.024596 | 67.34 | 12 | 0 | 6 | 2 | 0 | 0 | 0 | 0 | 0 | False | 1 |
| frame_pressure | 4 | 0.044243 | 68.88 | 17 | 0 | 11 | 4 | 0 | 1 | 20800 | 0 | 0 | True | 8 |
| frame_pressure | 8 | 0.081627 | 71.20 | 26 | 0 | 20 | 8 | 0 | 2 | 20800 | 0 | 0 | True | 8 |
| native_buffer | 1 | 0.013997 | 71.61 | 8 | 0 | 2 | 1 | 0 | 1 | 20800 | 0 | 0 | True | 8 |
| native_buffer | 2 | 0.030514 | 72.32 | 10 | 0 | 4 | 2 | 0 | 2 | 20800 | 0 | 0 | True | 8 |
| native_buffer | 4 | 0.044769 | 73.38 | 14 | 0 | 8 | 4 | 0 | 4 | 20800 | 0 | 0 | True | 8 |
| native_buffer | 8 | 0.079421 | 75.07 | 21 | 0 | 15 | 8 | 0 | 8 | 20800 | 0 | 0 | True | 8 |
