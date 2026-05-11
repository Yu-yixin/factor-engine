# Positional Phase Benchmark

- data: `data\minute_2026_03.parquet`
- rows: `500000`
- lifecycle: `True`

| exprs | total sec | peak rss mb | peak cols | child ms | bridge ms | positional ms | scan ms | attach ms | python | native | low-copy | parallel |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 1 | 0.114362 | 200.59 | 12 | 12.723 | 3.796 | 19.457 | 7.354 | 0.295 | False | True | True | True |
| 8 | 0.380464 | 320.79 | 19 | 80.822 | 28.438 | 138.237 | 46.523 | 1.163 | False | True | True | True |
