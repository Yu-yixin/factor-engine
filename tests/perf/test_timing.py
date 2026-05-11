import os
import time

import polars as pl
import pytest

from factor_engine.engine import FactorEngine


def build_benchmark_data(n_codes: int = 80, n_times: int = 160) -> pl.DataFrame:
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


def get_value(df: pl.DataFrame, code: str, time_value: int) -> float | None:
    row = df.filter((pl.col("code") == code) & (pl.col("time") == time_value))
    return row["result"][0]


@pytest.mark.parametrize(
    ("expression", "checks"),
    [
        (
            "close / delay(close, 1) - 1",
            [
                ("C000", 0, None),
                ("C000", 1, 1.0),
                ("C001", 1, 0.5),
            ],
        ),
        (
            "ts_mean(close, 5)",
            [
                ("C000", 0, 1.0),
                ("C000", 4, 3.0),
                ("C001", 4, 4.0),
            ],
        ),
        (
            "where(volume > ts_mean(volume, 20), ret_1d, 0)",
            [
                ("C001", 0, 0.0),
                ("C001", 1, 0.01),
                ("C009", 10, 0.09),
            ],
        ),
        (
            "rank(close, pct=true)",
            [
                ("C000", 0, 1.0),
                ("C079", 0, 1 / 80),
                ("C039", 10, 41 / 80),
            ],
        ),
    ],
)
def test_factor_expression_timing(expression: str, checks: list[tuple[str, int, float | None]]):
    df = build_benchmark_data()
    engine = FactorEngine()

    start = time.perf_counter()
    result = engine.evaluate(expression, df)
    elapsed = time.perf_counter() - start

    print(f"{expression}: {elapsed:.4f}s")

    assert result.height == df.height
    assert "result" in result.columns

    for code, time_value, expected in checks:
        value = get_value(result, code, time_value)
        if expected is None:
            assert value is None
        else:
            assert value == pytest.approx(expected)

    max_runtime = float(os.getenv("FACTOR_ENGINE_MAX_RUNTIME_SECONDS", "0"))
    if max_runtime > 0:
        assert elapsed <= max_runtime, (
            f"Expression {expression!r} took {elapsed:.4f}s, "
            f"which exceeds FACTOR_ENGINE_MAX_RUNTIME_SECONDS={max_runtime:.4f}s"
        )
