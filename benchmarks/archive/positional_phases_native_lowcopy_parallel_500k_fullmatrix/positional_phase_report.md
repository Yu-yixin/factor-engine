# Positional Phase Benchmark

- data: `data\minute_2026_03.parquet`
- rows: `500000`
- lifecycle: `True`

| exprs | total sec | peak rss mb | peak cols | child ms | bridge ms | positional ms | scan ms | attach ms | python | native | low-copy | parallel |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 1 | 0.111178 | 207.66 | 12 | 12.535 | 3.396 | 17.801 | 7.246 | 0.323 | False | True | True | True |
| 8 | 0.350027 | 276.63 | 19 | 76.542 | 28.539 | 146.242 | 58.504 | 1.232 | False | True | True | True |
| 16 | 0.554929 | 360.42 | 27 | 86.500 | 57.870 | 260.959 | 98.093 | 3.011 | False | True | True | True |
| 20 | 0.878923 | 373.83 | 31 | 164.244 | 82.703 | 352.702 | 133.688 | 4.663 | False | True | True | True |
