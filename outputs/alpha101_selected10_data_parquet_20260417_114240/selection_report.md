# Alpha101 Selected 10 Run

## Selection Rule

Selected factors avoid missing physical fields (`vwap`, `adv20`), avoid new routes, avoid lifecycle/M4 expansion, and stay inside currently accepted operators with explicit staging where needed.

## Selected Factors

| factor | expression |
| --- | --- |
| `alpha_2` | `-1 * correlation(rank(delta(log(volume), 2)), rank((close - open) / open), 6)` |
| `alpha_3` | `-1 * correlation(rank(open), rank(volume), 10)` |
| `alpha_4` | `-1 * ts_rank(rank(low), 9)` |
| `alpha_6` | `-1 * correlation(open, volume, 10)` |
| `alpha_9` | `where(0 < ts_min(delta(close, 1), 5), delta(close, 1), where(ts_max(delta(close, 1), 5) < 0, delta(close, 1), -1 * delta(close, 1)))` |
| `alpha_10` | `rank(where(0 < ts_min(delta(close, 1), 4), delta(close, 1), where(ts_max(delta(close, 1), 4) < 0, delta(close, 1), -1 * delta(close, 1))))` |
| `alpha_12` | `sign(delta(volume, 1)) * (-1 * delta(close, 1))` |
| `alpha_13` | `-1 * rank(covariance(rank(close), rank(volume), 5))` |
| `alpha_16` | `-1 * rank(covariance(rank(high), rank(volume), 5))` |
| `alpha_23` | `where((sum(high, 20) / 20) < high, -1 * delta(high, 2), 0)` |

## Excluded From This Batch

| factor | reason |
| --- | --- |
| `alpha_1` | Uses Ts_ArgMax / positional native-heavy path; supported by staging, but not among the safest 10. |
| `alpha_5` | Requires vwap, which is not a physical column in data.parquet; deriving it would add semantic assumptions. |
| `alpha_8` | Uses returns plus repeated deep composed rolling/delay expression; higher materialization pressure than selected set. |
| `alpha_11` | Requires vwap, which is not a physical column in data.parquet. |
| `alpha_14` | Uses returns plus mixed rank/correlation; feasible but higher nested pressure than selected set. |
| `alpha_15` | Rolling sum over ranked rolling correlation; deeper ordered/cross-sectional staging pressure. |
| `alpha_17` | Requires adv20 and more complex nested rolling/rank composition. |
| `alpha_18` | Feasible, but combines stddev(abs(...)) and correlation under final rank; lower priority than cleaner selected set. |
| `alpha_20` | Feasible with staging, but uses three delayed legs and three ranks; lower priority than selected set. |
| `alpha_22` | Feasible with staging, but combines delta(correlation(...)) and rank(stddev(...)); lower priority than selected set. |
