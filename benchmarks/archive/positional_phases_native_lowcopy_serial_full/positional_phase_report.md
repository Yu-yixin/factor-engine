# Positional Phase Benchmark

- data: `data\minute_2026_03.parquet`
- rows: `29048679`
- lifecycle: `True`

| exprs | total sec | peak rss mb | peak cols | child ms | bridge ms | positional ms | scan ms | attach ms | python | native | low-copy | parallel |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 1 | 9.450280 | 5728.92 | 12 | 594.625 | 197.599 | 1249.560 | 768.188 | 0.526 | False | True | True | False |
| 8 | 20.930046 | 13944.23 | 19 | 3044.002 | 1367.373 | 9559.429 | 5596.398 | 3.784 | False | True | True | False |
| 16 | 29.617698 | 19120.63 | 27 | 2983.569 | 2535.400 | 17922.187 | 10709.175 | 7.182 | False | True | True | False |
