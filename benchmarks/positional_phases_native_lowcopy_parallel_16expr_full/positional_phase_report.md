# Positional Phase Benchmark

- data: `data\minute_2026_03.parquet`
- rows: `29048679`
- lifecycle: `True`

| exprs | total sec | peak rss mb | peak cols | child ms | bridge ms | positional ms | scan ms | attach ms | python | native | low-copy | parallel |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 16 | 22.965138 | 12754.71 | 27 | 2698.465 | 2610.572 | 11708.789 | 5111.637 | 6.760 | False | True | True | True |
