# Positional Phase Benchmark

- data: `data\minute_2026_03.parquet`
- rows: `500000`
- lifecycle: `True`

| exprs | total sec | peak rss mb | peak cols | child ms | positional ms | to_list ms | scan ms | attach ms | python | native |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | 0.286071 | 207.23 | 12 | 9.895 | 192.990 | 9.326 | 162.397 | 4.158 | True | False |
| 8 | 1.477901 | 292.47 | 19 | 70.219 | 1282.382 | 65.169 | 1031.964 | 34.866 | True | False |
