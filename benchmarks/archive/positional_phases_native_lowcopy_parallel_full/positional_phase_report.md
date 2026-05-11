# Positional Phase Benchmark

- data: `data\minute_2026_03.parquet`
- rows: `29048679`
- lifecycle: `True`

| exprs | total sec | peak rss mb | peak cols | child ms | bridge ms | positional ms | scan ms | attach ms | python | native | low-copy | parallel |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 1 | 9.288744 | 5763.41 | 12 | 585.209 | 164.177 | 830.258 | 373.428 | 0.599 | False | True | True | True |
| 8 | 18.282200 | 12951.78 | 19 | 3256.800 | 1345.812 | 6668.569 | 2801.355 | 3.511 | False | True | True | True |
| 16 | 26.828467 | 18993.60 | 27 | 3215.155 | 2730.933 | 14355.682 | 5667.356 | 7.699 | False | True | True | True |
| 20 | 34.231298 | 22245.18 | 31 | 5278.439 | 3757.334 | 18631.623 | 7700.256 | 9.235 | False | True | True | True |
