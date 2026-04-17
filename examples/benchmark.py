import time

import polars as pl

from factor_engine.engine import FactorEngine


def build_data(n_codes: int = 100, n_times: int = 200) -> pl.DataFrame:
    rows = []
    for t in range(n_times):
        for i in range(n_codes):
            rows.append(
                {
                    "time": t,
                    "code": f"C{i:03d}",
                    "close": float(i + t + 1),
                    "volume": float((i + 1) * 100 + t),
                    "ret_1d": float((i % 10) / 100),
                }
            )
    return pl.DataFrame(rows)


def main():
    df = build_data()
    engine = FactorEngine()

    expressions = [
        "close / delay(close, 1) - 1",
        "ts_mean(close, 5)",
        "where(volume > ts_mean(volume, 20), ret_1d, 0)",
        "rank(close, pct=true)",
    ]

    for expression in expressions:
        start = time.perf_counter()
        engine.evaluate(expression, df)
        elapsed = time.perf_counter() - start
        print(f"{expression}: {elapsed:.4f}s")


if __name__ == "__main__":
    main()
