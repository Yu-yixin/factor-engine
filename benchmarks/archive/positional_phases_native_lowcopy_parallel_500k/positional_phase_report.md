# Positional Phase Benchmark

- data: `data\minute_2026_03.parquet`
- rows: `500000`
- lifecycle: `True`

| exprs | total sec | peak rss mb | peak cols | child ms | bridge ms | positional ms | scan ms | attach ms | python | native | low-copy | parallel |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 1 | 0.174705 | 212.49 | 12 | 13.046 | 14.071 | 53.783 | 30.665 | 0.354 | False | True | True | True |
| 8 | 0.337476 | 302.73 | 19 | 78.438 | 28.173 | 124.930 | 48.697 | 1.464 | False | True | True | True |
