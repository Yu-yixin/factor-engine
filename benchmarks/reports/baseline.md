# Baseline Benchmark (R17)

Date: 2026-04-14

Environment:
- Python: 3.13.13
- Polars: 1.39.3
- Rows: 120,000
- Codes: 500
- Industries: 12
- Expressions: 26
- Dataset shape: synthetic fixed-seed minute-like workload, seed = 20260414

## Execution Modes

| mode | mean (s) | min (s) | max (s) | repeats | avg / expr (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| evaluate() loop | 11.580486 | 10.975632 | 12.185341 | 2 | 445.403 |
| evaluate_many() | 9.067172 | 8.820359 | 9.313986 | 2 | 348.737 |
| workflow batch | 9.096905 | 9.062693 | 9.131116 | 2 | 349.881 |
| workflow batch report | 9.521175 | 9.309360 | 9.732991 | 2 | 366.199 |

## Optimization Check

| scenario | mean (s) | note |
| --- | ---: | --- |
| legacy workflow report loop | 12.507305 | one-by-one `evaluate()` with `with_columns()` append |
| optimized workflow report | 9.521175 | validate individually, then fast-path `evaluate_many()` with fallback |

## Summary

- `evaluate_many()` speedup vs `evaluate()` loop: `1.28x`
- `workflow batch / evaluate_many()`: `1.00x`
- `legacy report / optimized report`: `1.31x`
