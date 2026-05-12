# Performance Truth Scale-Up

## Executive Summary

- matrix actually run: 288 cases, 1 warmup run, 3 measured runs per case.
- Phase-1 top bottleneck overlap: argmax, argmin.
- cov/corr/ts_rank dominate at larger scale: yes among non-positional candidates.
- argmax/argmin native dependency: benchmark paths observed = fallback.
- timings stable enough to optimize: yes.
- final recommendation: A. Start native/shared-moment design for corr/cov.

## Stable Bottleneck Ranking

| Rank | Operator | Rows | Codes | Window | Null Rate | Median ms | CV | Scaling | Backend | Decision |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| 1 | argmin | 120000 | 250 | 5 | 0.0 | 174.923 | 0.765 | noisy | fallback; native=False; fallback=True | MEASURE_MORE |
| 2 | argmin | 120000 | 250 | 5 | 0.01 | 145.267 | 0.072 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 3 | argmax | 120000 | 250 | 60 | 0.01 | 134.358 | 0.025 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 4 | argmin | 120000 | 40 | 60 | 0.0 | 131.655 | 0.071 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 5 | argmax | 120000 | 250 | 20 | 0.0 | 130.013 | 0.407 | noisy | fallback; native=False; fallback=True | MEASURE_MORE |
| 6 | argmin | 120000 | 250 | 60 | 0.01 | 128.991 | 0.012 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 7 | argmax | 120000 | 250 | 5 | 0.0 | 128.416 | 0.044 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 8 | argmax | 120000 | 40 | 60 | 0.01 | 126.784 | 0.359 | noisy | fallback; native=False; fallback=True | MEASURE_MORE |
| 9 | argmax | 120000 | 40 | 60 | 0.1 | 125.934 | 0.081 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 10 | argmax | 120000 | 250 | 60 | 0.0 | 125.769 | 0.029 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 11 | argmin | 120000 | 250 | 60 | 0.1 | 125.727 | 0.080 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 12 | argmax | 120000 | 250 | 60 | 0.1 | 125.508 | 0.085 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 13 | argmax | 120000 | 40 | 5 | 0.01 | 125.375 | 0.064 | noisy | fallback; native=False; fallback=True | MEASURE_MORE |
| 14 | argmax | 120000 | 40 | 20 | 0.01 | 125.155 | 0.439 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 15 | argmin | 120000 | 250 | 5 | 0.1 | 124.990 | 0.076 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 16 | argmin | 120000 | 250 | 20 | 0.01 | 124.892 | 0.031 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 17 | argmin | 120000 | 40 | 20 | 0.01 | 124.552 | 0.090 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 18 | argmax | 120000 | 250 | 5 | 0.1 | 124.517 | 0.070 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 19 | argmax | 120000 | 250 | 20 | 0.1 | 123.549 | 0.031 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 20 | argmin | 120000 | 250 | 20 | 0.0 | 122.849 | 0.008 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 21 | argmin | 120000 | 250 | 60 | 0.0 | 122.481 | 0.080 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 22 | argmax | 120000 | 250 | 20 | 0.01 | 122.065 | 0.472 | noisy | fallback; native=False; fallback=True | MEASURE_MORE |
| 23 | argmin | 120000 | 40 | 60 | 0.01 | 121.654 | 0.120 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 24 | argmax | 120000 | 40 | 60 | 0.0 | 121.307 | 0.028 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 25 | argmax | 120000 | 40 | 20 | 0.0 | 120.972 | 0.021 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 26 | argmax | 120000 | 250 | 5 | 0.01 | 120.387 | 0.043 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 27 | argmin | 120000 | 250 | 20 | 0.1 | 119.469 | 0.002 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 28 | argmax | 120000 | 40 | 5 | 0.1 | 118.996 | 0.055 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 29 | argmin | 120000 | 40 | 20 | 0.0 | 118.037 | 0.033 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |
| 30 | argmin | 120000 | 40 | 5 | 0.01 | 117.825 | 0.088 | stable_linear | fallback; native=False; fallback=True | MEASURE_MORE |

## Scaling Findings

| Operator | Small ms | Medium ms | Large ms | Growth | Scaling Class | Notes |
| --- | ---: | ---: | ---: | --- | --- | --- |
| argmax | 20.489 | 43.739 | 125.375 | 2.4k->24k 2.13x time / 10.00x rows | noisy | 24k->120k 2.87x time / 5.00x rows (stable_linear) |
| argmin | 22.023 | 47.753 | 124.552 | 2.4k->24k 2.17x time / 10.00x rows | stable_linear | 24k->120k 2.61x time / 5.00x rows (stable_linear) |
| corr | 11.306 | 19.596 | 62.692 | 2.4k->24k 1.73x time / 10.00x rows | stable_linear | 24k->120k 3.20x time / 5.00x rows (stable_linear) |
| cov | 9.683 | 14.764 | 62.461 | 2.4k->24k 1.52x time / 10.00x rows | stable_linear | 24k->120k 4.23x time / 5.00x rows (stable_linear) |
| ts_mean | 10.588 | 19.926 | 49.596 | 2.4k->24k 1.88x time / 10.00x rows | noisy | 24k->120k 2.49x time / 5.00x rows (noisy) |
| ts_rank | 14.751 | 16.849 | 67.526 | 2.4k->24k 1.14x time / 10.00x rows | stable_linear | 24k->120k 4.01x time / 5.00x rows (noisy) |
| ts_std | 9.784 | 22.416 | 50.692 | 2.4k->24k 2.29x time / 10.00x rows | stable_linear | 24k->120k 2.26x time / 5.00x rows (stable_linear) |
| ts_sum | 8.927 | 23.726 | 64.842 | 2.4k->24k 2.66x time / 10.00x rows | stable_linear | 24k->120k 2.73x time / 5.00x rows (noisy) |

## Native Positional Finding

argmax/argmin backend status: native_available=True; native_requested=False; paths_tested=fallback. Do not interpret positional slowness as native slowness unless paths_tested includes native. Composed-case risk remains UNKNOWN unless nested positional cases are included.

## Recommendation

A. Start native/shared-moment design for corr/cov

Uncertain findings are marked UNKNOWN. Guessed explanations are marked HYPOTHESIS.
