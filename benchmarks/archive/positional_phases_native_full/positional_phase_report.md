# Positional Phase Benchmark

- data: `data\minute_2026_03.parquet`
- rows: `29048679`
- lifecycle: `True`

| exprs | total sec | peak rss mb | peak cols | child ms | positional ms | to_list ms | scan ms | attach ms | python | native |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | 11.398303 | 5632.33 | 12 | 548.383 | 2736.977 | 1519.572 | 580.253 | 0.145 | False | True |
| 8 | 31.475720 | 12270.62 | 19 | 3074.028 | 19934.576 | 11555.100 | 3507.139 | 0.766 | False | True |
| 16 | 51.838994 | 15991.62 | 27 | 3363.002 | 39981.335 | 22235.497 | 7504.537 | 1.300 | False | True |
