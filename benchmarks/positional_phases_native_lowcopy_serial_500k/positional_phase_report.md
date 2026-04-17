# Positional Phase Benchmark

- data: `data\minute_2026_03.parquet`
- rows: `500000`
- lifecycle: `True`

| exprs | total sec | peak rss mb | peak cols | child ms | bridge ms | positional ms | scan ms | attach ms | python | native | low-copy | parallel |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 1 | 0.103179 | 207.99 | 12 | 11.656 | 3.607 | 21.201 | 10.934 | 0.355 | False | True | True | False |
| 8 | 0.398851 | 316.31 | 19 | 97.754 | 27.803 | 167.178 | 93.061 | 1.559 | False | True | True | False |
