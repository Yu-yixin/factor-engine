# M1 Verify Comparison

- baseline: `benchmarks\m1_verify_20260417_030305\baseline_lifecycle_off`
- optimized: `benchmarks\m1_verify_20260417_030305\optimized_lifecycle_on`

| workload | exprs | base rss | opt rss | rss delta | base frame | opt frame | frame delta | base output | opt output | base stage | opt stage | native lag opt | recomputed opt |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| frame_pressure | 1 | 66.46 | 66.44 | -0.02 | 9 | 9 | 0 | 0 | 0 | 3 | 3 | 0 | 0 |
| frame_pressure | 2 | 67.34 | 67.19 | -0.15 | 12 | 12 | 0 | 0 | 0 | 6 | 6 | 0 | 0 |
| frame_pressure | 4 | 68.88 | 69.04 | 0.16 | 17 | 14 | -3 | 0 | 0 | 11 | 8 | 0 | 0 |
| frame_pressure | 8 | 71.20 | 71.30 | 0.11 | 26 | 22 | -4 | 0 | 0 | 20 | 16 | 0 | 0 |
| native_buffer | 1 | 71.61 | 72.25 | 0.64 | 8 | 8 | 0 | 0 | 0 | 2 | 2 | 0 | 0 |
| native_buffer | 2 | 72.32 | 73.11 | 0.79 | 10 | 9 | -1 | 0 | 0 | 4 | 3 | 0 | 0 |
| native_buffer | 4 | 73.38 | 74.29 | 0.91 | 14 | 11 | -3 | 0 | 0 | 8 | 5 | 0 | 0 |
| native_buffer | 8 | 75.07 | 75.87 | 0.80 | 21 | 15 | -6 | 0 | 0 | 15 | 9 | 0 | 0 |
| output_retention | 1 | 59.90 | 60.09 | 0.18 | 8 | 8 | 0 | 0 | 0 | 2 | 2 | 0 | 0 |
| output_retention | 2 | 61.52 | 61.72 | 0.20 | 10 | 9 | -1 | 0 | 0 | 4 | 3 | 0 | 0 |
| output_retention | 4 | 63.01 | 63.23 | 0.22 | 12 | 11 | -1 | 0 | 0 | 6 | 5 | 0 | 0 |
| output_retention | 8 | 65.06 | 65.02 | -0.05 | 16 | 15 | -1 | 0 | 0 | 10 | 9 | 0 | 0 |
