# Positional Phase Benchmark

- data: `data\minute_2026_03.parquet`
- rows: `500000`
- lifecycle: `True`

| exprs | total sec | peak rss mb | peak cols | child ms | positional ms | to_list ms | scan ms | attach ms | python | native |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | 0.127759 | 204.11 | 12 | 11.903 | 45.795 | 24.238 | 8.495 | 0.122 | False | True |
| 8 | 0.545144 | 311.88 | 19 | 72.612 | 361.178 | 195.146 | 69.483 | 0.617 | False | True |
