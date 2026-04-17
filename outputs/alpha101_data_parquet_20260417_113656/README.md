# Alpha101 Factors 1-4 on data.parquet

- input: `data\data.parquet`
- rows: `29048679`
- time column: `time`
- code column: `ths_code`
- returns: `close / delay(close, 1) - 1` by `ths_code`, ordered by `time`

The four formulas were evaluated through explicit intermediate columns because the current planner does not directly route every ordered/cross-sectional nested composition used by the Alpha101 notation.

## Outputs

- factors parquet: `alpha101_factors.parquet`
- preview csv: `preview_100.csv`
- expressions: `expressions.json`
- execution steps: `execution_steps.json`
- summary: `summary.json`

## Final Columns

```text
time, ths_code, alpha_1, alpha_2, alpha_3, alpha_4
```

## Original Expression Translation

```text
Alpha#1 = rank(argmax(signedpower(where(returns < 0, stddev(returns, 20), close), 2), 5)) - 0.5
Alpha#2 = -1 * correlation(rank(delta(log(volume), 2)), rank((close - open) / open), 6)
Alpha#3 = -1 * correlation(rank(open), rank(volume), 10)
Alpha#4 = -1 * ts_rank(rank(low), 9)
```
