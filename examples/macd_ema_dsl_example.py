"""Experimental EMA/MACD DSL example for the feature branch only."""

from pathlib import Path
import sys

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from factor_engine.engine import FactorEngine


def main() -> None:
    df = pl.DataFrame(
        {
            "code": ["BTC", "ETH", "BTC", "ETH", "BTC", "ETH"],
            "time": [2, 1, 1, 3, 3, 2],
            "close": [102.0, 200.0, 100.0, 205.0, 105.0, 202.0],
        }
    )

    expressions = [
        ("macd_dif", "ema(close, 12) - ema(close, 26)"),
        ("macd_dea", "ema(ema(close, 12) - ema(close, 26), 9)"),
        (
            "macd_hist",
            "(ema(close, 12) - ema(close, 26)) - ema(ema(close, 12) - ema(close, 26), 9)",
        ),
    ]

    result = FactorEngine().evaluate_many(expressions, df)
    output = result.select(["code", "time", "close", "macd_dif", "macd_dea", "macd_hist"])
    print(output.write_csv())


if __name__ == "__main__":
    main()
