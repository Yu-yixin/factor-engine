# M1 Memory Model Benchmark

- rows: `2560`
- lifecycle: `True`

| workload | exprs | total sec | peak rss mb | peak frame cols | peak output cols | peak stage cols | alive outputs | late outputs | native buffers | native peak bytes | release lag | recomputed | parallel | workers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| output_retention | 1 | 0.020567 | 60.09 | 8 | 0 | 2 | 1 | 0 | 1 | 20800 | 0 | 0 | True | 8 |
| output_retention | 2 | 0.025476 | 61.72 | 9 | 0 | 3 | 2 | 0 | 2 | 20800 | 0 | 0 | True | 8 |
| output_retention | 4 | 0.042796 | 63.23 | 11 | 0 | 5 | 4 | 0 | 4 | 20800 | 0 | 0 | True | 8 |
| output_retention | 8 | 0.130902 | 65.02 | 15 | 0 | 9 | 8 | 0 | 8 | 20800 | 0 | 0 | True | 8 |
| frame_pressure | 1 | 0.020509 | 66.44 | 9 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | False | 1 |
| frame_pressure | 2 | 0.033620 | 67.19 | 12 | 0 | 6 | 2 | 0 | 0 | 0 | 0 | 0 | False | 1 |
| frame_pressure | 4 | 0.077622 | 69.04 | 14 | 0 | 8 | 4 | 0 | 1 | 20800 | 0 | 0 | True | 8 |
| frame_pressure | 8 | 0.162816 | 71.30 | 22 | 0 | 16 | 8 | 0 | 2 | 20800 | 0 | 0 | True | 8 |
| native_buffer | 1 | 0.021529 | 72.25 | 8 | 0 | 2 | 1 | 0 | 1 | 20800 | 0 | 0 | True | 8 |
| native_buffer | 2 | 0.035693 | 73.11 | 9 | 0 | 3 | 2 | 0 | 2 | 20800 | 0 | 0 | True | 8 |
| native_buffer | 4 | 0.048830 | 74.29 | 11 | 0 | 5 | 4 | 0 | 4 | 20800 | 0 | 0 | True | 8 |
| native_buffer | 8 | 0.090445 | 75.87 | 15 | 0 | 9 | 8 | 0 | 8 | 20800 | 0 | 0 | True | 8 |
