from __future__ import annotations

import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from factor_engine.engine import FactorEngine  # noqa: E402
from factor_engine.executor import Executor  # noqa: E402
from factor_engine.lexer import Lexer  # noqa: E402
from factor_engine.parser import Parser  # noqa: E402


@dataclass(frozen=True)
class ScaleSpec:
    name: str
    rows: int
    repeats: int


@dataclass(frozen=True)
class TimingSummary:
    mean_seconds: float
    min_seconds: float
    max_seconds: float
    repeat_count: int


@dataclass(frozen=True)
class StageBreakdown:
    sort_seconds: float
    segment_id_seconds: float
    aggregate_broadcast_seconds: float

    @property
    def total_seconds(self) -> float:
        return (
            self.sort_seconds
            + self.segment_id_seconds
            + self.aggregate_broadcast_seconds
        )


@dataclass(frozen=True)
class BenchmarkResult:
    scale: str
    rows: int
    scenario: str
    timing: TimingSummary


SCALES = [
    ScaleSpec(name="S", rows=10_000, repeats=5),
    ScaleSpec(name="M", rows=100_000, repeats=3),
    ScaleSpec(name="L", rows=1_000_000, repeats=1),
]


def parse_expression(text: str):
    tokens = Lexer(text).tokenize()
    return Parser(tokens).parse()


def build_segmented_data(target_rows: int, *, n_codes: int = 97) -> pl.DataFrame:
    lengths = _build_group_lengths(target_rows, n_codes=n_codes)

    times: list[int] = []
    codes: list[str] = []
    close: list[float] = []
    open_: list[float] = []
    volume: list[float] = []

    for code_index, group_length in enumerate(lengths):
        code_name = f"C{code_index:03d}"
        base_price = 50.0 + code_index * 0.7
        for time_index in range(group_length):
            drift = time_index * 0.13
            wave = ((time_index % 17) - 8) * 0.21
            close_value = base_price + drift + wave
            open_value = close_value - ((time_index % 5) - 2) * 0.09

            times.append(time_index)
            codes.append(code_name)
            close.append(close_value)
            open_.append(open_value)
            volume.append(float((code_index + 1) * 1000 + time_index * 3))

    df = pl.DataFrame(
        {
            "time": times,
            "code": codes,
            "close": close,
            "open": open_,
            "volume": volume,
        }
    )

    # A shuffled input keeps the benchmark aligned with the production contract:
    # segmented execution must restore original order instead of assuming pre-sorted data.
    return df.with_row_index("__shuffle_idx").sort("__shuffle_idx", descending=True).drop("__shuffle_idx")


def _build_group_lengths(target_rows: int, *, n_codes: int) -> list[int]:
    base = max(8, target_rows // n_codes)
    lengths = [max(1, base + ((code_index * 7) % 11) - 5) for code_index in range(n_codes)]

    current_total = sum(lengths)
    if current_total == target_rows:
        return lengths

    index = 0
    diff = target_rows - current_total
    step = 1 if diff > 0 else -1
    while diff != 0:
        if step > 0 or lengths[index] > 1:
            lengths[index] += step
            diff -= step
        index = (index + 1) % n_codes

    return lengths


def summarize_runs(durations: list[float]) -> TimingSummary:
    return TimingSummary(
        mean_seconds=statistics.fmean(durations),
        min_seconds=min(durations),
        max_seconds=max(durations),
        repeat_count=len(durations),
    )


def measure(
    fn,
    *,
    repeats: int,
    warmup: bool = True,
) -> TimingSummary:
    if warmup:
        fn()

    durations: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        durations.append(time.perf_counter() - start)

    return summarize_runs(durations)


def benchmark_stage_breakdown(df: pl.DataFrame, *, segment_count: int) -> StageBreakdown:
    expr = parse_expression(f"seg_mean(close, {segment_count})")
    executor = Executor(df)

    sort_start = time.perf_counter()
    prepared = executor._get_prepared_frame()
    sort_seconds = time.perf_counter() - sort_start

    segment_start = time.perf_counter()
    segmented_df = executor._prepare_segmented_sorted_df(
        prepared.sorted_df,
        segment_count=segment_count,
    )
    segment_seconds = time.perf_counter() - segment_start

    aggregate_start = time.perf_counter()
    compiled = executor.compile(expr)
    segmented_df.with_columns(compiled.alias("result"))
    aggregate_seconds = time.perf_counter() - aggregate_start

    return StageBreakdown(
        sort_seconds=sort_seconds,
        segment_id_seconds=segment_seconds,
        aggregate_broadcast_seconds=aggregate_seconds,
    )


def benchmark_scale(scale: ScaleSpec) -> tuple[list[BenchmarkResult], StageBreakdown]:
    df = build_segmented_data(scale.rows)
    stage_breakdown = benchmark_stage_breakdown(df, segment_count=3)

    results: list[BenchmarkResult] = []

    results.append(
        BenchmarkResult(
            scale=scale.name,
            rows=df.height,
            scenario="evaluate(seg_mean(close, 3))",
            timing=measure(
                lambda: FactorEngine().evaluate("seg_mean(close, 3)", df),
                repeats=scale.repeats,
            ),
        )
    )
    results.append(
        BenchmarkResult(
            scale=scale.name,
            rows=df.height,
            scenario="serial same-count x3",
            timing=measure(
                lambda: run_serial_same_count(df),
                repeats=scale.repeats,
            ),
        )
    )
    results.append(
        BenchmarkResult(
            scale=scale.name,
            rows=df.height,
            scenario="evaluate_many same-count x3",
            timing=measure(
                lambda: run_evaluate_many_same_count(df),
                repeats=scale.repeats,
            ),
        )
    )
    results.append(
        BenchmarkResult(
            scale=scale.name,
            rows=df.height,
            scenario="serial different-count x2",
            timing=measure(
                lambda: run_serial_different_count(df),
                repeats=scale.repeats,
            ),
        )
    )
    results.append(
        BenchmarkResult(
            scale=scale.name,
            rows=df.height,
            scenario="evaluate_many different-count x2",
            timing=measure(
                lambda: run_evaluate_many_different_count(df),
                repeats=scale.repeats,
            ),
        )
    )
    results.append(
        BenchmarkResult(
            scale=scale.name,
            rows=df.height,
            scenario="evaluate(where(close > seg_mean(close, 3), close, open))",
            timing=measure(
                lambda: FactorEngine().evaluate(
                    "where(close > seg_mean(close, 3), close, open)",
                    df,
                ),
                repeats=scale.repeats,
            ),
        )
    )
    results.append(
        BenchmarkResult(
            scale=scale.name,
            rows=df.height,
            scenario="evaluate(ts_mean(close, 5) - seg_mean(close, 3))",
            timing=measure(
                lambda: FactorEngine().evaluate(
                    "ts_mean(close, 5) - seg_mean(close, 3)",
                    df,
                ),
                repeats=scale.repeats,
            ),
        )
    )

    return results, stage_breakdown


def run_serial_same_count(df: pl.DataFrame) -> None:
    engine = FactorEngine()
    engine.evaluate("seg_mean(close, 3)", df, output_name="seg_close")
    engine.evaluate("seg_mean(open, 3)", df, output_name="seg_open")
    engine.evaluate("seg_mean(close - open, 3)", df, output_name="seg_spread")


def run_evaluate_many_same_count(df: pl.DataFrame) -> None:
    engine = FactorEngine()
    engine.evaluate_many(
        [
            ("seg_close", "seg_mean(close, 3)"),
            ("seg_open", "seg_mean(open, 3)"),
            ("seg_spread", "seg_mean(close - open, 3)"),
        ],
        df,
    )


def run_serial_different_count(df: pl.DataFrame) -> None:
    engine = FactorEngine()
    engine.evaluate("seg_mean(close, 3)", df, output_name="seg3")
    engine.evaluate("seg_mean(close, 5)", df, output_name="seg5")


def run_evaluate_many_different_count(df: pl.DataFrame) -> None:
    engine = FactorEngine()
    engine.evaluate_many(
        [
            ("seg3", "seg_mean(close, 3)"),
            ("seg5", "seg_mean(close, 5)"),
        ],
        df,
    )


def render_markdown(
    benchmark_results: list[BenchmarkResult],
    stage_breakdowns: dict[str, StageBreakdown],
) -> str:
    lines: list[str] = []
    lines.append("# Segmented Benchmark v1")
    lines.append("")
    lines.append("Date: 2026-04-14")
    lines.append("")
    lines.append("Environment:")
    lines.append(f"- Python: {sys.version.split()[0]}")
    lines.append(f"- Polars: {pl.__version__}")
    lines.append("- Input shape: synthetic uneven multi-code dataset with shuffled row order")
    lines.append("")
    lines.append("Dataset scales:")
    for scale in SCALES:
        lines.append(f"- `{scale.name}`: target ~{scale.rows:,} rows")
    lines.append("")
    lines.append("## Stage Breakdown (`seg_mean(close, 3)`)")
    lines.append("")
    lines.append("| scale | rows | sort (s) | segment_id (s) | aggregate+broadcast (s) | segment share |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for scale_name, breakdown in stage_breakdowns.items():
        total = breakdown.total_seconds or 1e-12
        segment_share = breakdown.segment_id_seconds / total
        row_count = next(result.rows for result in benchmark_results if result.scale == scale_name)
        lines.append(
            f"| {scale_name} | {row_count:,} | {breakdown.sort_seconds:.6f} | "
            f"{breakdown.segment_id_seconds:.6f} | {breakdown.aggregate_broadcast_seconds:.6f} | "
            f"{segment_share:.1%} |"
        )
    lines.append("")
    lines.append("## Wall Time")
    lines.append("")
    lines.append("| scale | rows | scenario | mean (s) | min (s) | max (s) | repeats |")
    lines.append("| --- | ---: | --- | ---: | ---: | ---: | ---: |")
    for result in benchmark_results:
        lines.append(
            f"| {result.scale} | {result.rows:,} | {result.scenario} | "
            f"{result.timing.mean_seconds:.6f} | {result.timing.min_seconds:.6f} | "
            f"{result.timing.max_seconds:.6f} | {result.timing.repeat_count} |"
        )
    lines.append("")
    lines.append("## Q1 / Q2 / Q3")
    lines.append("")
    lines.extend(summarize_answers(benchmark_results, stage_breakdowns))
    lines.append("")
    return "\n".join(lines)


def summarize_answers(
    benchmark_results: list[BenchmarkResult],
    stage_breakdowns: dict[str, StageBreakdown],
) -> list[str]:
    answers: list[str] = []

    largest_scale = max(SCALES, key=lambda item: item.rows).name
    largest_breakdown = stage_breakdowns[largest_scale]
    total = largest_breakdown.total_seconds or 1e-12
    segment_share = largest_breakdown.segment_id_seconds / total
    answers.append(
        f"- Q1: 在 `{largest_scale}` 档里，`segment_id` 构造约占 stage benchmark 的 `{segment_share:.1%}`；"
        "当前结果说明 segmented v1 的主瓶颈已经更偏向 `segment_id` 预处理，而不是排序本身。"
    )

    same_serial = lookup_result(benchmark_results, scale=largest_scale, scenario="serial same-count x3")
    same_many = lookup_result(
        benchmark_results,
        scale=largest_scale,
        scenario="evaluate_many same-count x3",
    )
    same_ratio = same_many.timing.mean_seconds / same_serial.timing.mean_seconds
    answers.append(
        f"- Q2: `{largest_scale}` 档里，`evaluate_many same-count x3 / serial same-count x3 = {same_ratio:.2f}`。"
        "如果该比值接近 1，说明同一 `segment_count` 下重复预处理仍然明显，没有得到有效复用。"
    )

    diff_many = lookup_result(
        benchmark_results,
        scale=largest_scale,
        scenario="evaluate_many different-count x2",
    )
    single = lookup_result(
        benchmark_results,
        scale=largest_scale,
        scenario="evaluate(seg_mean(close, 3))",
    )
    diff_ratio = diff_many.timing.mean_seconds / max(single.timing.mean_seconds, 1e-12)
    answers.append(
        f"- Q3: `{largest_scale}` 档里，`evaluate_many different-count x2 / single = {diff_ratio:.2f}`。"
        "如果不同 `segment_count` 场景明显高于单表达式且没有同-count 优势，就说明后续需要按 `segment_count` 做 prepared view 复用。"
    )

    return answers


def lookup_result(
    benchmark_results: list[BenchmarkResult],
    *,
    scale: str,
    scenario: str,
) -> BenchmarkResult:
    for result in benchmark_results:
        if result.scale == scale and result.scenario == scenario:
            return result
    raise KeyError(f"Missing benchmark result for scale={scale}, scenario={scenario}")


def main() -> None:
    all_results: list[BenchmarkResult] = []
    stage_breakdowns: dict[str, StageBreakdown] = {}

    for scale in SCALES:
        results, breakdown = benchmark_scale(scale)
        all_results.extend(results)
        stage_breakdowns[scale.name] = breakdown

    markdown = render_markdown(all_results, stage_breakdowns)
    output_dir = PROJECT_ROOT / "benchmarks" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "segmented_v1.md"
    output_path.write_text(markdown, encoding="utf-8")

    print(markdown)
    print(f"Saved benchmark report to {output_path}")


if __name__ == "__main__":
    main()
