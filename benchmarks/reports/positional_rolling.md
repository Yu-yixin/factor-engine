# Positional Rolling Benchmark

Date: 2026-04-16

Environment:
- Python: 3.14.4
- Polars: 1.39.3
- Rows: 60,000
- Groups: 250
- Seed: 20260416

The list-fallback column uses the phase-1 `concat_list -> list.arg_*` model.
The dedicated-kernel column uses the phase-3 grouped monotonic deque scan.

| case | rows | groups | window | list fallback (s) | dedicated kernel (s) | speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| argmax_5 | 60,000 | 250 | 5 | 0.066847 | 0.023230 | 2.88x |
| argmax_20 | 60,000 | 250 | 20 | 0.261770 | 0.023155 | 11.30x |
| argmax_60 | 60,000 | 250 | 60 | 0.761721 | 0.043671 | 17.44x |
| argmin_5 | 60,000 | 250 | 5 | 0.068541 | 0.024676 | 2.78x |
| argmin_20 | 60,000 | 250 | 20 | 0.251976 | 0.023350 | 10.79x |
| argmin_60 | 60,000 | 250 | 60 | 0.771838 | 0.024183 | 31.92x |

## Nested Expression Cases

`list fallback` keeps the ordered shell and child materialization, but swaps the root `argmax/argmin` kernel back to the phase-1 list implementation.
`dedicated kernel` is the default engine path.

| case | rows | groups | expression | list fallback (s) | dedicated kernel (s) | speedup |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| argmax_fill_20 | 60,000 | 250 | `argmax(fill_null(close, open), 20)` | 0.253874 | 0.023324 | 10.88x |
| argmax_ts_mean_20 | 60,000 | 250 | `argmax(ts_mean(fill_null(close, open), 20), 20)` | 0.257942 | 0.023177 | 11.13x |
| argmax_rank_ts_mean_20 | 60,000 | 250 | `argmax(rank(ts_mean(fill_null(close, open), 20), pct=true), 20)` | 0.264296 | 0.025342 | 10.43x |
