# Positional Phase Benchmark

- data: `data\minute_2026_03.parquet`
- rows: `10000`
- lifecycle: `True`

| exprs | total sec | peak rss mb | peak cols | child ms | positional ms | to_list ms | scan ms | attach ms | python | native |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | 0.025562 | 71.52 | 12 | 4.784 | 5.362 | 0.228 | 4.266 | 0.408 | True | False |
