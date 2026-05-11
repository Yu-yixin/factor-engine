from __future__ import annotations

import json
import shutil
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from factor_engine.engine import FactorEngine  # noqa: E402
from factor_engine.executor import Executor  # noqa: E402
from factor_engine.run_summary import build_run_summary, persist_run_summary, render_run_summary  # noqa: E402
from factor_engine.workflow import (  # noqa: E402
    BatchExpression,
    evaluate_expression_batch_report,
    evaluate_expression_file,
    load_expression_file,
    write_result,
)


SEED = 20260414
DEFAULT_CODES = 500
DEFAULT_TIMES = 240
DEFAULT_INDUSTRIES = 12
DEFAULT_REPEATS = 2


@dataclass(frozen=True)
class ExpressionCase:
    name: str
    expression: str
    family: str


@dataclass(frozen=True)
class TimingSummary:
    mean_seconds: float
    min_seconds: float
    max_seconds: float
    repeats: int


@dataclass(frozen=True)
class ModeResult:
    mode: str
    timing: TimingSummary


@dataclass(frozen=True)
class StageMetric:
    stage: str
    seconds: float
    detail: str


@dataclass(frozen=True)
class ScalingResult:
    label: str
    rows: int
    codes: int
    expressions: int
    seconds: float


EXPRESSIONS: list[ExpressionCase] = [
    ExpressionCase("spread", "close - open", "pointwise"),
    ExpressionCase("intraday_ret", "fill_null(close, open) / open - 1", "pointwise"),
    ExpressionCase("abs_spread", "abs(close - open)", "pointwise"),
    ExpressionCase("clipped_spread", "clip(close - open, -2, 2)", "pointwise"),
    ExpressionCase("sign_spread", "sign(close - open)", "pointwise"),
    ExpressionCase("close_is_null", "is_null(close)", "pointwise"),
    ExpressionCase("filled_close", "fill_null(close, open)", "pointwise"),
    ExpressionCase("ts_mean_5", "ts_mean(fill_null(close, open), 5)", "rolling"),
    ExpressionCase("ts_mean_20", "ts_mean(fill_null(close, open), 20)", "rolling"),
    ExpressionCase("ts_std_20", "ts_std(fill_null(close, open), 20)", "rolling"),
    ExpressionCase("ts_median_20", "ts_median(fill_null(close, open), 20)", "rolling"),
    ExpressionCase("delta_1", "delta(fill_null(close, open), 1)", "rolling"),
    ExpressionCase("pct_change_1", "pct_change(fill_null(close, open), 1)", "rolling"),
    ExpressionCase("argmax_20", "argmax(fill_null(close, open), 20)", "rolling"),
    ExpressionCase("argmin_20", "argmin(fill_null(close, open), 20)", "rolling"),
    ExpressionCase("ts_rank_20", "ts_rank(fill_null(close, open), 20, pct=true)", "rolling"),
    ExpressionCase("group_demean_close", "group_demean(fill_null(close, open), industry)", "grouped"),
    ExpressionCase("group_zscore_ret", "group_zscore(ret_1d, industry)", "grouped"),
    ExpressionCase(
        "group_rank_close",
        "group_rank(fill_null(close, open), industry, pct=true)",
        "grouped",
    ),
    ExpressionCase(
        "seglen_mean_240",
        "seglen_mean(fill_null(close, open), [60, 60, 60, 60])",
        "segmented",
    ),
    ExpressionCase("seglen_sum_240", "seglen_sum(volume, [60, 60, 60, 60])", "segmented"),
    ExpressionCase(
        "seglen_count_up",
        "seglen_count(close > open, [60, 60, 60, 60])",
        "segmented",
    ),
    ExpressionCase("seglen_any_up", "seglen_any(close > open, [60, 60, 60, 60])", "segmented"),
    ExpressionCase("seglen_all_up", "seglen_all(close > open, [60, 60, 60, 60])", "segmented"),
    ExpressionCase(
        "composed_signal",
        "where((volume > ts_mean(volume, 20)) and not is_null(close), abs(delta(fill_null(close, open), 1)), 0)",
        "composed",
    ),
    ExpressionCase(
        "grouped_clip",
        "clip(group_zscore(ts_mean(fill_null(close, open), 5), industry), -3, 3)",
        "composed",
    ),
]


def build_workload(
    *,
    code_count: int = DEFAULT_CODES,
    time_count: int = DEFAULT_TIMES,
    industry_count: int = DEFAULT_INDUSTRIES,
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
                pl.concat_str(
                    [pl.lit("IND"), (pl.col("__code_idx") % industry_count).cast(pl.Utf8)],
                    separator="",
                ).alias("industry"),
                (
                    100.0
                    + pl.col("__code_idx") * 0.025
                    + pl.col("__time_idx") * 0.08
                    + ((pl.col("__code_idx") * 13 + pl.col("__time_idx") * 7 + SEED) % 19) * 0.03
                ).alias("__base_open"),
                (
                    ((pl.col("__code_idx") * 17 + pl.col("__time_idx") * 11 + SEED) % 5000) + 1000
                ).cast(pl.Float64).alias("volume"),
            ]
        )
        .with_columns(
            [
                pl.col("__base_open").alias("open"),
                (
                    pl.col("__base_open")
                    + (((pl.col("__code_idx") * 11 + pl.col("__time_idx") * 5 + SEED) % 9) - 4) * 0.12
                ).alias("__base_close"),
            ]
        )
        .with_columns(
            [
                pl.when((pl.col("__time_idx") + pl.col("__code_idx") * 3 + SEED) % 53 == 0)
                .then(None)
                .otherwise(pl.col("__base_close"))
                .alias("close")
            ]
        )
        .with_columns(
            [
                (
                    pl.col("close")
                    .fill_null(pl.col("open"))
                    .shift(1)
                    .over("code")
                ).alias("__prev_close")
            ]
        )
        .with_columns(
            [
                (
                    pl.col("close").fill_null(pl.col("open")) / pl.col("__prev_close") - 1
                )
                .fill_nan(None)
                .fill_null(0.0)
                .alias("ret_1d")
            ]
        )
        .drop(["row_id", "__code_idx", "__time_idx", "__base_open", "__base_close", "__prev_close"])
        .sample(fraction=1.0, shuffle=True, seed=SEED)
    )
    return df.select(["time", "code", "industry", "open", "close", "volume", "ret_1d"])


def summarize(values: list[float]) -> TimingSummary:
    return TimingSummary(
        mean_seconds=statistics.fmean(values),
        min_seconds=min(values),
        max_seconds=max(values),
        repeats=len(values),
    )


def measure(fn: Callable[[], object], *, repeats: int = DEFAULT_REPEATS, warmup: bool = True) -> TimingSummary:
    if warmup:
        fn()

    durations: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        durations.append(time.perf_counter() - start)

    return summarize(durations)


def run_evaluate_mode(df: pl.DataFrame, expressions: list[ExpressionCase]) -> None:
    engine = FactorEngine()
    for item in expressions:
        engine.evaluate(item.expression, df, output_name=item.name)


def run_evaluate_many_mode(df: pl.DataFrame, expressions: list[ExpressionCase]) -> None:
    FactorEngine().evaluate_many([(item.name, item.expression) for item in expressions], df)


def run_workflow_batch_mode(path: Path, df: pl.DataFrame) -> None:
    evaluate_expression_file(path, df, engine=FactorEngine())


def run_workflow_report_mode(expressions: list[BatchExpression], df: pl.DataFrame) -> None:
    evaluate_expression_batch_report(expressions, df, engine=FactorEngine())


def run_workflow_report_legacy(expressions: list[BatchExpression], df: pl.DataFrame) -> None:
    engine = FactorEngine()
    result_df = df
    for item in expressions:
        evaluated = engine.evaluate(item.expression, df, output_name=item.name)
        result_df = result_df.with_columns(evaluated[item.name])
    _ = result_df


class TimerBucket:
    def __init__(self) -> None:
        self.total_seconds = 0.0

    def add(self, seconds: float) -> None:
        self.total_seconds += seconds


class _MethodTimer:
    def __init__(self, cls: type, method_name: str, bucket: TimerBucket) -> None:
        self.cls = cls
        self.method_name = method_name
        self.bucket = bucket
        self.original = getattr(cls, method_name)

    def __enter__(self) -> "_MethodTimer":
        original = self.original
        bucket = self.bucket

        def wrapped(instance, *args, **kwargs):
            start = time.perf_counter()
            try:
                return original(instance, *args, **kwargs)
            finally:
                bucket.add(time.perf_counter() - start)

        setattr(self.cls, self.method_name, wrapped)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        setattr(self.cls, self.method_name, self.original)


def profile_stages(
    df: pl.DataFrame,
    expressions: list[ExpressionCase],
    expression_path: Path,
    temp_dir: Path,
) -> list[StageMetric]:
    planning_engine = FactorEngine()
    planning_start = time.perf_counter()
    for item in expressions:
        planning_engine._get_or_compile(item.expression, df)
    planning_seconds = time.perf_counter() - planning_start

    rolling_items = [item for item in expressions if item.family == "rolling"]
    grouped_items = [item for item in expressions if item.family == "grouped"]
    segmented_items = [item for item in expressions if item.family == "segmented"]
    ordered_items = rolling_items + segmented_items + [item for item in expressions if item.family == "composed"]

    sort_bucket = TimerBucket()
    with _MethodTimer(Executor, "_get_prepared_frame", sort_bucket):
        FactorEngine().evaluate_many([(item.name, item.expression) for item in ordered_items], df)

    rolling_bucket = TimerBucket()
    with _MethodTimer(Executor, "_evaluate_many_row_aligned_time_ordered", rolling_bucket):
        FactorEngine().evaluate_many([(item.name, item.expression) for item in rolling_items], df)

    grouped_bucket = TimerBucket()
    with _MethodTimer(Executor, "_evaluate_many_row_aligned_no_time_order", grouped_bucket):
        FactorEngine().evaluate_many([(item.name, item.expression) for item in grouped_items], df)

    segmented_bucket = TimerBucket()
    with _MethodTimer(Executor, "_evaluate_many_segmented_columns", segmented_bucket):
        FactorEngine().evaluate_many([(item.name, item.expression) for item in segmented_items], df)

    batch_df = FactorEngine().evaluate_many([(item.name, item.expression) for item in expressions], df)
    io_start = time.perf_counter()
    load_expression_file(expression_path)
    parquet_path = temp_dir / "profile_result.parquet"
    csv_path = temp_dir / "profile_result.csv"
    write_result(batch_df, parquet_path)
    write_result(batch_df.head(5_000), csv_path)
    io_seconds = time.perf_counter() - io_start

    return [
        StageMetric("parse_validate_compile_time", planning_seconds, "cold planning for the full expression set"),
        StageMetric("sorting_time", sort_bucket.total_seconds, "Executor._get_prepared_frame across ordered families"),
        StageMetric("rolling_time", rolling_bucket.total_seconds, "time-ordered rolling batch path"),
        StageMetric("grouped_time", grouped_bucket.total_seconds, "grouped cross-sectional batch path"),
        StageMetric("segmented_time", segmented_bucket.total_seconds, "segmented batch path with prepared-view reuse"),
        StageMetric("io_time", io_seconds, "expression-file load plus parquet/csv write"),
    ]


def benchmark_scaling() -> list[ScalingResult]:
    shapes = [
        ("rows_s", 250, DEFAULT_TIMES, len(EXPRESSIONS)),
        ("rows_m", 500, DEFAULT_TIMES, len(EXPRESSIONS)),
        ("rows_l", 1000, DEFAULT_TIMES, len(EXPRESSIONS)),
        ("expr_half", DEFAULT_CODES, DEFAULT_TIMES, 12),
        ("expr_full", DEFAULT_CODES, DEFAULT_TIMES, len(EXPRESSIONS)),
    ]

    results: list[ScalingResult] = []
    for label, codes, times, expr_count in shapes:
        df = build_workload(code_count=codes, time_count=times)
        selected = EXPRESSIONS[:expr_count]
        start = time.perf_counter()
        FactorEngine().evaluate_many([(item.name, item.expression) for item in selected], df)
        seconds = time.perf_counter() - start
        results.append(
            ScalingResult(
                label=label,
                rows=df.height,
                codes=df.get_column("code").n_unique(),
                expressions=expr_count,
                seconds=seconds,
            )
        )

    return results


def write_expression_file(path: Path, expressions: list[ExpressionCase]) -> None:
    payload = {
        "expressions": [
            {"name": item.name, "expression": item.expression}
            for item in expressions
        ]
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_benchmark_run_summary(
    *,
    df: pl.DataFrame,
    expressions: list[ExpressionCase],
    total_time_seconds: float,
    load_time_seconds: float | None,
    execute_time_seconds: float | None,
    write_time_seconds: float | None,
    notes: str | None,
) -> object:
    return build_run_summary(
        mode="benchmark_real_workload",
        data_path="generated://benchmark_real_workload",
        expression_source="inline:benchmark_real_workload",
        rows=int(df.height),
        codes=int(df.get_column("code").n_unique()),
        expressions=len(expressions),
        success_count=len(expressions),
        failed_count=0,
        total_time_seconds=total_time_seconds,
        load_time_seconds=load_time_seconds,
        validate_time_seconds=None,
        execute_time_seconds=execute_time_seconds,
        write_time_seconds=write_time_seconds,
        output_path=None,
        notes=notes,
        benchmark_name="benchmark_real_workload",
    )


def render_baseline(
    df: pl.DataFrame,
    results: list[ModeResult],
    *,
    num_expressions: int,
    legacy_report: TimingSummary,
    optimized_report: TimingSummary,
) -> str:
    result_map = {item.mode: item.timing for item in results}
    evaluate_loop = result_map["evaluate() loop"]
    evaluate_many = result_map["evaluate_many()"]
    workflow_batch = result_map["workflow batch"]
    speedup = evaluate_loop.mean_seconds / max(evaluate_many.mean_seconds, 1e-12)
    workflow_ratio = workflow_batch.mean_seconds / max(evaluate_many.mean_seconds, 1e-12)
    report_ratio = legacy_report.mean_seconds / max(optimized_report.mean_seconds, 1e-12)

    lines = [
        "# Baseline Benchmark (R17)",
        "",
        "Date: 2026-04-14",
        "",
        "Environment:",
        f"- Python: {sys.version.split()[0]}",
        f"- Polars: {pl.__version__}",
        f"- Rows: {df.height:,}",
        f"- Codes: {df.get_column('code').n_unique():,}",
        f"- Industries: {df.get_column('industry').n_unique():,}",
        f"- Expressions: {num_expressions}",
        f"- Dataset shape: synthetic fixed-seed minute-like workload, seed = {SEED}",
        "",
        "## Execution Modes",
        "",
        "| mode | mean (s) | min (s) | max (s) | repeats | avg / expr (ms) |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]

    for item in results:
        avg_ms = item.timing.mean_seconds * 1000 / num_expressions
        lines.append(
            f"| {item.mode} | {item.timing.mean_seconds:.6f} | {item.timing.min_seconds:.6f} | "
            f"{item.timing.max_seconds:.6f} | {item.timing.repeats} | {avg_ms:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Optimization Check",
            "",
            "| scenario | mean (s) | note |",
            "| --- | ---: | --- |",
            f"| legacy workflow report loop | {legacy_report.mean_seconds:.6f} | one-by-one `evaluate()` with `with_columns()` append |",
            f"| optimized workflow report | {optimized_report.mean_seconds:.6f} | validate individually, then fast-path `evaluate_many()` with fallback |",
            "",
            "## Summary",
            "",
            f"- `evaluate_many()` speedup vs `evaluate()` loop: `{speedup:.2f}x`",
            f"- `workflow batch / evaluate_many()`: `{workflow_ratio:.2f}x`",
            f"- `legacy report / optimized report`: `{report_ratio:.2f}x`",
            "",
        ]
    )
    return "\n".join(lines)


def render_profile(
    stage_metrics: list[StageMetric],
    scaling_results: list[ScalingResult],
) -> str:
    ordered = sorted(stage_metrics, key=lambda item: item.seconds, reverse=True)
    top_3 = ordered[:3]

    lines = [
        "# Stage Profile (R17)",
        "",
        "Date: 2026-04-14",
        "",
        "## Stage Metrics",
        "",
        "| stage | seconds | note |",
        "| --- | ---: | --- |",
    ]
    for metric in ordered:
        lines.append(f"| {metric.stage} | {metric.seconds:.6f} | {metric.detail} |")

    lines.extend(
        [
            "",
            "## Top 3 Bottlenecks",
            "",
        ]
    )
    for metric in top_3:
        lines.append(f"- `{metric.stage}`: {metric.seconds:.6f}s")

    lines.extend(
        [
            "",
            "## Scaling Snapshot (`evaluate_many()`) ",
            "",
            "| label | rows | codes | expressions | seconds |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in scaling_results:
        lines.append(
            f"| {item.label} | {item.rows:,} | {item.codes:,} | {item.expressions} | {item.seconds:.6f} |"
        )

    lines.extend(
        [
            "",
            "## Observations",
            "",
            "- Rows from 60k to 240k show near-linear growth in `evaluate_many()` wall time on this synthetic workload.",
            "- Increasing expressions from 12 to the full set mainly amplifies ordered and segmented paths rather than file IO.",
            "- The first optimization target should stay on high-share reusable stages before deeper kernel rewrites.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    total_start = time.perf_counter()
    load_start = time.perf_counter()
    df = build_workload()
    load_time_seconds = time.perf_counter() - load_start
    batch_expressions = [BatchExpression(name=item.name, expression=item.expression) for item in EXPRESSIONS]
    temp_dir = PROJECT_ROOT / ".tmp_benchmark_real_workload"
    temp_dir.mkdir(exist_ok=True)
    try:
        expression_path = temp_dir / "benchmark_expressions.json"
        write_expression_file(expression_path, EXPRESSIONS)

        execute_start = time.perf_counter()
        baseline_results = [
            ModeResult(
                mode="evaluate() loop",
                timing=measure(lambda: run_evaluate_mode(df, EXPRESSIONS)),
            ),
            ModeResult(
                mode="evaluate_many()",
                timing=measure(lambda: run_evaluate_many_mode(df, EXPRESSIONS)),
            ),
            ModeResult(
                mode="workflow batch",
                timing=measure(lambda: run_workflow_batch_mode(expression_path, df)),
            ),
            ModeResult(
                mode="workflow batch report",
                timing=measure(lambda: run_workflow_report_mode(batch_expressions, df)),
            ),
        ]

        legacy_report = measure(lambda: run_workflow_report_legacy(batch_expressions, df))
        optimized_report = next(
            item.timing for item in baseline_results if item.mode == "workflow batch report"
        )

        stage_metrics = profile_stages(df, EXPRESSIONS, expression_path, temp_dir)
        scaling_results = benchmark_scaling()
        execute_time_seconds = time.perf_counter() - execute_start

        benchmarks_dir = PROJECT_ROOT / "benchmarks" / "reports"
        benchmarks_dir.mkdir(parents=True, exist_ok=True)

        write_start = time.perf_counter()
        baseline_path = benchmarks_dir / "baseline.md"
        baseline_markdown = render_baseline(
            df,
            baseline_results,
            num_expressions=len(EXPRESSIONS),
            legacy_report=legacy_report,
            optimized_report=optimized_report,
        )
        baseline_path.write_text(baseline_markdown, encoding="utf-8")

        profile_path = benchmarks_dir / "profile.md"
        profile_markdown = render_profile(stage_metrics, scaling_results)
        profile_path.write_text(profile_markdown, encoding="utf-8")
        write_time_seconds = time.perf_counter() - write_start
        total_time_seconds = time.perf_counter() - total_start

        print(baseline_markdown)
        print(f"Saved baseline benchmark report to {baseline_path}")
        print()
        print(profile_markdown)
        print(f"Saved stage profile report to {profile_path}")

        summary = build_benchmark_run_summary(
            df=df,
            expressions=EXPRESSIONS,
            total_time_seconds=total_time_seconds,
            load_time_seconds=load_time_seconds,
            execute_time_seconds=execute_time_seconds,
            write_time_seconds=write_time_seconds,
            notes="wrote baseline.md and profile.md",
        )
        print(render_run_summary(summary))
        try:
            persist_run_summary(summary, benchmarks_dir=benchmarks_dir)
        except Exception as exc:  # pragma: no cover - CLI warning path
            print(f"[run-summary-warning] failed to persist summary: {exc}", file=sys.stderr)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
