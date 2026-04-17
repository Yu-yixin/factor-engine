import polars as pl

from factor_engine.engine import FactorEngine


def main():
    df = pl.DataFrame(
        {
            "time": [1, 2, 3, 1, 2, 3],
            "code": ["A", "A", "A", "B", "B", "B"],
            "close": [10.0, 11.0, 12.0, 20.0, 21.0, 19.0],
            "volume": [100.0, 120.0, 90.0, 200.0, 180.0, 160.0],
            "ret_1d": [0.01, 0.02, -0.01, 0.03, -0.02, 0.01],
        }
    )

    engine = FactorEngine()

    expressions = [
        "close / delay(close, 1) - 1",
        "ts_mean(close, 2)",
        "where(volume > ts_mean(volume, 2), ret_1d, 0)",
        "demean(close)",
        "rank(close, pct=true)",
    ]

    for expression in expressions:
        print(f"\nExpression: {expression}")
        print(engine.evaluate(expression, df))


if __name__ == "__main__":
    main()
