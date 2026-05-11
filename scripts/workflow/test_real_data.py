from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from factor_engine.engine import FactorEngine  # noqa: E402


DEFAULT_DATA_PATH = ROOT / "data" / "minute_2026_03.parquet"
DEFAULT_SAMPLE_ROWS = 200_000
PREVIEW_ROWS = 10


def build_rename_map(columns: list[str]) -> dict[str, str]:
    rename_map = {}

    if "datetime" in columns and "time" not in columns:
        rename_map["datetime"] = "time"
    if "timestamp" in columns and "time" not in columns:
        rename_map["timestamp"] = "time"
    if "symbol" in columns and "code" not in columns:
        rename_map["symbol"] = "code"
    if "ticker" in columns and "code" not in columns:
        rename_map["ticker"] = "code"
    if "ths_code" in columns and "code" not in columns:
        rename_map["ths_code"] = "code"

    return rename_map


def normalize_columns(df: pl.DataFrame) -> pl.DataFrame:
    rename_map = build_rename_map(df.columns)

    if rename_map:
        df = df.rename(rename_map)

    return df


def load_real_data() -> pl.DataFrame:
    path = Path(os.getenv("FACTOR_ENGINE_REAL_DATA_PATH", str(DEFAULT_DATA_PATH)))
    sample_rows = int(os.getenv("FACTOR_ENGINE_REAL_DATA_ROWS", str(DEFAULT_SAMPLE_ROWS)))
    per_code_head = int(os.getenv("FACTOR_ENGINE_REAL_DATA_PER_CODE_HEAD", "0"))
    load_mode = "sample_rows"

    if per_code_head > 0:
        load_mode = "per_code_head"
        lf = pl.scan_parquet(path)
        rename_map = build_rename_map(lf.collect_schema().names())
        if rename_map:
            lf = lf.rename(rename_map)

        df = (
            lf.with_row_index("__row_idx")
            .group_by("code", maintain_order=True)
            .head(per_code_head)
            .sort("__row_idx")
            .drop("__row_idx")
            .collect()
        )
    elif sample_rows > 0:
        # The example defaults to a large real-data slice so it finishes in practical time.
        df = pl.read_parquet(path, n_rows=sample_rows)
    else:
        load_mode = "full_file"
        df = pl.read_parquet(path)

    df = normalize_columns(df)

    print("=== Data Source ===")
    print(f"path={path}")
    print(f"rows_loaded={df.height}")
    if load_mode == "per_code_head":
        print(f"sample_mode=per_code_head({per_code_head})")
    elif sample_rows > 0:
        print("sample_mode=True (set FACTOR_ENGINE_REAL_DATA_ROWS=0 to read the full file)")
    else:
        print("sample_mode=False")

    print("\n=== Schema ===")
    print(df.schema)

    print("\n=== Head ===")
    print(df.head(5))
    return df


def require_columns(df: pl.DataFrame, required_columns: set[str]) -> None:
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")


def build_seglen_expression(df: pl.DataFrame) -> str:
    max_group_length = (
        df.group_by("code")
        .len()
        .select(pl.col("len").max().alias("max_group_length"))
        .item()
    )
    return f"seglen_mean(close, [{max_group_length}])"


def get_expression_suites(
    df: pl.DataFrame,
    *,
    include_table_expressions: bool,
) -> tuple[dict[str, list[str]], list[str]]:
    seglen_expression = build_seglen_expression(df)
    column_suites = {
        "pointwise_and_arithmetic": [
            "close",
            "open + close",
            "high - low",
            "close / delay(close, 1) - 1",
            "where(volume > ts_mean(volume, 20), close / delay(close, 1) - 1, 0)",
        ],
        "time_series": [
            "delay(close, 1)",
            "delta(close, 1)",
            "pct_change(close, 1)",
            "delay(close / delay(close, 1) - 1, 1)",
            "ts_min(close, 5)",
            "ts_max(close, 5)",
            "ts_mean(close, 5)",
            "ts_sum(volume, 5)",
            "ts_std(close, 5)",
            "ts_count(close > open, 5)",
            "ts_any(close > open, 5)",
            "ts_all(close > open, 5)",
            "ts_rank(close, 5, pct=true)",
            "corr(close, volume, 5)",
            "cov(close, volume, 5)",
            "skew(close, 5)",
            "kurt(close, 5)",
        ],
        "cross_sectional": [
            "demean(close)",
            "zscore(close)",
            "rank(close, pct=true)",
            "rank(close, ascending=true)",
        ],
        "segmented": [
            "seg_mean(close, 3)",
            seglen_expression,
            "seg_sum(volume, 3)",
            "seg_count(close > open, 3)",
            "seg_any(close > open, 3)",
            "seg_all(close > open, 3)",
            "close - seg_mean(close, 3)",
        ],
    }
    table_expressions = ["fft(close)"] if include_table_expressions else []
    return column_suites, table_expressions


def get_batch_expressions(df: pl.DataFrame) -> list[tuple[str, str]]:
    return [
        ("ret_1", "close / delay(close, 1) - 1"),
        ("cs_rank", "rank(close, pct=true)"),
        ("ts_rank_5", "ts_rank(close, 5, pct=true)"),
        ("seg_close_mean", "seg_mean(close, 3)"),
        ("seg_close_len_mean", build_seglen_expression(df)),
        ("seg_up_count", "seg_count(close > open, 3)"),
    ]


def build_table_test_frame(df: pl.DataFrame) -> pl.DataFrame:
    table_rows_per_code = int(os.getenv("FACTOR_ENGINE_REAL_DATA_TABLE_ROWS_PER_CODE", "64"))
    if table_rows_per_code <= 0:
        raise ValueError("FACTOR_ENGINE_REAL_DATA_TABLE_ROWS_PER_CODE must be > 0")

    return (
        df.sort(["code", "time"])
        .group_by("code", maintain_order=True)
        .head(table_rows_per_code)
        .sort(["code", "time"])
    )


def preview_columns(result: pl.DataFrame) -> list[str]:
    fft_columns = ["code", "frequency", "magnitude", "phase"]
    if "frequency" in result.columns:
        return [column for column in fft_columns if column in result.columns]

    preferred = ["time", "code", "close", "volume", "result"]
    columns = [column for column in preferred if column in result.columns]
    return columns or result.columns[: min(6, len(result.columns))]


def run_expression(engine: FactorEngine, df: pl.DataFrame, expression: str) -> None:
    start = time.perf_counter()
    result = engine.evaluate(expression, df)
    elapsed = time.perf_counter() - start

    print(f"\n=== Expression: {expression} ===")
    print(f"shape={result.shape} elapsed={elapsed:.3f}s")
    print(result.select(preview_columns(result)).head(PREVIEW_ROWS))


def run_expression_suite(
    engine: FactorEngine,
    df: pl.DataFrame,
    suite_name: str,
    expressions: list[str],
    failures: list[tuple[str, Exception]],
) -> None:
    print(f"\n=== Suite: {suite_name} ===")
    for expression in expressions:
        try:
            run_expression(engine, df, expression)
        except Exception as exc:  # pragma: no cover - example script error reporting
            failures.append((expression, exc))
            print(f"{expression} FAILED: {type(exc).__name__}: {exc}")


def run_evaluate_many(
    engine: FactorEngine,
    df: pl.DataFrame,
    expressions: list[tuple[str, str]],
    failures: list[tuple[str, Exception]],
) -> None:
    print("\n=== API: evaluate_many ===")
    for output_name, expression in expressions:
        print(f"{output_name} <- {expression}")

    start = time.perf_counter()
    try:
        result = engine.evaluate_many(expressions, df)
    except Exception as exc:  # pragma: no cover - example script error reporting
        failures.append(("evaluate_many(...)", exc))
        print(f"evaluate_many(...) FAILED: {type(exc).__name__}: {exc}")
        return

    elapsed = time.perf_counter() - start
    preview = ["time", "code", *[name for name, _ in expressions]]
    print(f"shape={result.shape} elapsed={elapsed:.3f}s")
    print(result.select([column for column in preview if column in result.columns]).head(PREVIEW_ROWS))


def main() -> None:
    df = load_real_data()
    require_columns(df, {"time", "code", "open", "high", "low", "close", "volume"})

    engine = FactorEngine()
    include_table_expressions = os.getenv("FACTOR_ENGINE_REAL_DATA_INCLUDE_TABLE", "auto")
    if include_table_expressions == "auto":
        include_table = True
    else:
        include_table = include_table_expressions == "1"

    column_suites, table_expressions = get_expression_suites(
        df,
        include_table_expressions=include_table
    )
    batch_expressions = get_batch_expressions(df)
    failures: list[tuple[str, Exception]] = []

    print("\n=== Column Expression Suites ===")
    for suite_name, expressions in column_suites.items():
        run_expression_suite(engine, df, suite_name, expressions, failures)

    run_evaluate_many(engine, df, batch_expressions, failures)

    if table_expressions:
        print("\n=== Table Expressions ===")
        table_df = build_table_test_frame(df)
        print(f"table_rows={table_df.height} rows_per_code={os.getenv('FACTOR_ENGINE_REAL_DATA_TABLE_ROWS_PER_CODE', '64')}")
        for expression in table_expressions:
            try:
                run_expression(engine, table_df, expression)
            except Exception as exc:  # pragma: no cover - example script error reporting
                failures.append((expression, exc))
                print(f"{expression} FAILED: {type(exc).__name__}: {exc}")
    else:
        print("\n=== Table Expressions ===")
        print("skipped (set FACTOR_ENGINE_REAL_DATA_INCLUDE_TABLE=1 to force execution)")

    print("\n=== Summary ===")
    if failures:
        for expression, exc in failures:
            print(f"- {expression}: {type(exc).__name__}: {exc}")
        raise RuntimeError(f"{len(failures)} real-data expressions failed")

    column_expression_count = sum(len(expressions) for expressions in column_suites.values())
    print(
        "all_expressions_passed="
        f"{column_expression_count + len(batch_expressions) + len(table_expressions)}"
    )


if __name__ == "__main__":
    main()
