from __future__ import annotations

import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from factor_engine.engine import FactorEngine  # noqa: E402
from factor_engine.executor import Executor  # noqa: E402
from factor_engine.lexer import Lexer  # noqa: E402
from factor_engine.parser import Parser  # noqa: E402


SEED = 20260416
DEFAULT_CODES = 250
DEFAULT_TIMES = 240
DEFAULT_REPEATS = 3


@dataclass(frozen=True)
class BenchmarkCase:
    name: str
    kind: str
    window: int


@dataclass(frozen=True)
class BenchmarkResult:
    case: BenchmarkCase
    rows: int
    groups: int
    list_fallback_seconds: float
    dedicated_kernel_seconds: float


@dataclass(frozen=True)
class ExpressionCase:
    name: str
    expression: str


@dataclass(frozen=True)
class ExpressionBenchmarkResult:
    case: ExpressionCase
    rows: int
    groups: int
    list_fallback_seconds: float
    dedicated_kernel_seconds: float


CASES = [
    BenchmarkCase("argmax_5", "argmax", 5),
    BenchmarkCase("argmax_20", "argmax", 20),
    BenchmarkCase("argmax_60", "argmax", 60),
    BenchmarkCase("argmin_5", "argmin", 5),
    BenchmarkCase("argmin_20", "argmin", 20),
    BenchmarkCase("argmin_60", "argmin", 60),
]

EXPRESSION_CASES = [
    ExpressionCase("argmax_fill_20", "argmax(fill_null(close, open), 20)"),
    ExpressionCase(
        "argmax_ts_mean_20",
        "argmax(ts_mean(fill_null(close, open), 20), 20)",
    ),
    ExpressionCase(
        "argmax_rank_ts_mean_20",
        "argmax(rank(ts_mean(fill_null(close, open), 20), pct=true), 20)",
    ),
]


def build_workload(
    *,
    code_count: int = DEFAULT_CODES,
    time_count: int = DEFAULT_TIMES,
) -> pl.DataFrame:
    total_rows = code_count * time_count
    df = (
        pl.DataFrame({"row_id": range(total_rows)})
        .with_columns(
            [
                (pl.col("row_id") // time_count).alias("__code_idx"),
                (pl.col("row_id") % time_count).alias("__time_idx"),
            ]
        )
        .with_columns(
            [
                pl.concat_str(
                    [pl.lit("C"), pl.col("__code_idx").cast(pl.Utf8)],
                    separator="",
                ).alias("code"),
                pl.col("__time_idx").alias("time"),
                (
                    100.0
                    + pl.col("__code_idx") * 0.05
                    + pl.col("__time_idx") * 0.08
                    + ((pl.col("__code_idx") * 13 + pl.col("__time_idx") * 7 + SEED) % 19) * 0.03
                ).alias("__base_close"),
            ]
        )
        .with_columns(
            [
                pl.when((pl.col("__time_idx") + pl.col("__code_idx") * 5 + SEED) % 37 == 0)
                .then(None)
                .otherwise(pl.col("__base_close"))
                .alias("close"),
                (
                    pl.col("__base_close")
                    - (((pl.col("__code_idx") * 3 + pl.col("__time_idx") * 5 + SEED) % 7) * 0.02)
                ).alias("open"),
            ]
        )
        .drop(["row_id", "__code_idx", "__time_idx", "__base_close"])
        .sample(fraction=1.0, shuffle=True, seed=SEED)
    )
    return df.select(["time", "code", "open", "close"])


def measure(fn, *, repeats: int = DEFAULT_REPEATS) -> float:
    fn()
    durations: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        durations.append(time.perf_counter() - start)
    return statistics.fmean(durations)


def _legacy_recent_arg_extreme(values: list[float | None], *, mode: str) -> int | None:
    target_index: int | None = None
    target_value: float | None = None

    for index, value in enumerate(values):
        if value is None:
            continue
        if target_index is None:
            target_index = index
            target_value = value
            continue

        if mode == "max":
            is_better = value > target_value or (value == target_value and index > target_index)
        else:
            is_better = value < target_value or (value == target_value and index > target_index)
        if is_better:
            target_index = index
            target_value = value

    if target_index is None:
        return None
    return len(values) - 1 - target_index


def evaluate_legacy_callback(df: pl.DataFrame, *, kind: str, window: int) -> pl.DataFrame:
    executor = Executor(df)
    prepared = executor._get_prepared_frame()
    sorted_df = prepared.sorted_df
    expr = (
        pl.col("close")
        .rolling_map(
            lambda series: _legacy_recent_arg_extreme(
                series.to_list(),
                mode="max" if kind == "argmax" else "min",
            ),
            window_size=window,
            min_samples=1,
        )
        .over("code")
        .cast(pl.Int64)
        .alias("result")
    )
    prepared.sorted_df = sorted_df.with_columns(expr)
    return prepared.restore_output_columns(["result"])


def evaluate_dedicated_kernel(df: pl.DataFrame, *, kind: str, window: int) -> pl.DataFrame:
    return FactorEngine().evaluate(f"{kind}(close, {window})", df)


def parse_expression(text: str):
    return Parser(Lexer(text).tokenize()).parse()


def evaluate_list_fallback(df: pl.DataFrame, expression: str) -> pl.DataFrame:
    expr = parse_expression(expression)
    if expr.name not in {"argmax", "argmin"} or len(expr.args) != 2 or expr.kwargs:
        raise ValueError("This benchmark fallback expects a root argmax/argmin expression")

    executor = Executor(df)
    prepared = executor._get_prepared_frame()
    reserved_names = set(prepared.sorted_df.columns)
    sorted_df, value_stage_name, _stage_cache = executor._materialize_expr_on_sorted_df(
        prepared.sorted_df,
        expr=expr.args[0],
        reserved_names=reserved_names,
        stage_cache={},
    )
    window = executor._expect_positive_numeric_literal(expr.args[1], expr.name)
    compiled = executor._compile_positional_list_fallback(
        pl.col(value_stage_name),
        window,
        mode=expr.name,
    )
    prepared.sorted_df = sorted_df.with_columns(compiled.alias("result"))
    return prepared.restore_output_columns(["result"])


def render_report(
    df: pl.DataFrame,
    results: list[BenchmarkResult],
    expression_results: list[ExpressionBenchmarkResult],
) -> str:
    lines = [
        "# Positional Rolling Benchmark",
        "",
        "Date: 2026-04-16",
        "",
        "Environment:",
        f"- Python: {sys.version.split()[0]}",
        f"- Polars: {pl.__version__}",
        f"- Rows: {df.height:,}",
        f"- Groups: {df.get_column('code').n_unique():,}",
        f"- Seed: {SEED}",
        "",
        "The list-fallback column uses the phase-1 `concat_list -> list.arg_*` model.",
        "The dedicated-kernel column uses the phase-3 grouped monotonic deque scan.",
        "",
        "| case | rows | groups | window | list fallback (s) | dedicated kernel (s) | speedup |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for item in results:
        speedup = item.list_fallback_seconds / max(item.dedicated_kernel_seconds, 1e-12)
        lines.append(
            f"| {item.case.name} | {item.rows:,} | {item.groups:,} | {item.case.window} | "
            f"{item.list_fallback_seconds:.6f} | {item.dedicated_kernel_seconds:.6f} | "
            f"{speedup:.2f}x |"
        )

    lines.extend(
        [
            "",
            "## Nested Expression Cases",
            "",
            "`list fallback` keeps the ordered shell and child materialization, but swaps the "
            "root `argmax/argmin` kernel back to the phase-1 list implementation.",
            "`dedicated kernel` is the default engine path.",
            "",
            "| case | rows | groups | expression | list fallback (s) | "
            "dedicated kernel (s) | speedup |",
            "| --- | ---: | ---: | --- | ---: | ---: | ---: |",
        ]
    )
    for item in expression_results:
        speedup = item.list_fallback_seconds / max(item.dedicated_kernel_seconds, 1e-12)
        lines.append(
            f"| {item.case.name} | {item.rows:,} | {item.groups:,} | `{item.case.expression}` | "
            f"{item.list_fallback_seconds:.6f} | {item.dedicated_kernel_seconds:.6f} | "
            f"{speedup:.2f}x |"
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    df = build_workload()
    results: list[BenchmarkResult] = []
    for case in CASES:
        expression = f"{case.kind}(close, {case.window})"
        list_fallback_seconds = measure(lambda: evaluate_list_fallback(df, expression))
        dedicated_kernel_seconds = measure(
            lambda: evaluate_dedicated_kernel(df, kind=case.kind, window=case.window)
        )
        results.append(
            BenchmarkResult(
                case=case,
                rows=df.height,
                groups=df.get_column("code").n_unique(),
                list_fallback_seconds=list_fallback_seconds,
                dedicated_kernel_seconds=dedicated_kernel_seconds,
            )
        )

    expression_results: list[ExpressionBenchmarkResult] = []
    for case in EXPRESSION_CASES:
        list_fallback_seconds = measure(lambda: evaluate_list_fallback(df, case.expression))
        dedicated_kernel_seconds = measure(lambda: FactorEngine().evaluate(case.expression, df))
        expression_results.append(
            ExpressionBenchmarkResult(
                case=case,
                rows=df.height,
                groups=df.get_column("code").n_unique(),
                list_fallback_seconds=list_fallback_seconds,
                dedicated_kernel_seconds=dedicated_kernel_seconds,
            )
        )

    report = render_report(df, results, expression_results)
    report_path = PROJECT_ROOT / "benchmarks" / "positional_rolling.md"
    report_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"Saved positional rolling benchmark report to {report_path}")


if __name__ == "__main__":
    main()
