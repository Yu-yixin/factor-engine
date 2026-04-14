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
| evaluate() loop | 7.760473 | 7.747304 | 7.773641 | 2 | 298.480 |
| evaluate_many() | 6.178913 | 6.165256 | 6.192570 | 2 | 237.650 |
| workflow batch | 6.241781 | 6.202582 | 6.280981 | 2 | 240.069 |
| workflow batch report | 6.442421 | 6.428115 | 6.456728 | 2 | 247.785 |

## Optimization Check

| scenario | mean (s) | note |
| --- | ---: | --- |
| legacy workflow report loop | 7.733965 | one-by-one `evaluate()` with `with_columns()` append |
| optimized workflow report | 6.442421 | validate individually, then fast-path `evaluate_many()` with fallback |

## Summary

- `evaluate_many()` speedup vs `evaluate()` loop: `1.26x`
- `workflow batch / evaluate_many()`: `1.01x`
- `legacy report / optimized report`: `1.20x`
