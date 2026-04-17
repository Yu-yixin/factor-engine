from __future__ import annotations

import os
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


DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "minute_2026_03.parquet"


@dataclass(frozen=True)
class ScaleSpec:
    name: str
    target_rows: int
    repeats: int


@dataclass(frozen=True)
class TimingSummary:
    mean_seconds: float
    min_seconds: float
    max_seconds: float
    repeat_count: int


@dataclass(frozen=True)
class WorkloadStats:
    rows: int
    code_count: int
    min_group_len: int
    median_group_len: float
    max_group_len: int


@dataclass(frozen=True)
class StageBreakdown:
    sort_seconds: float
    segmented_view_seconds: float
    aggregate_broadcast_seconds: float
    restore_order_seconds: float

    @property
    def total_seconds(self) -> float:
        return (
            self.sort_seconds
            + self.segmented_view_seconds
            + self.aggregate_broadcast_seconds
            + self.restore_order_seconds
        )


@dataclass(frozen=True)
class BenchmarkResult:
    scale: str
    scenario: str
    timing: TimingSummary
    workload: WorkloadStats


SCALES = [
    ScaleSpec(name="S", target_rows=10_000, repeats=5),
    ScaleSpec(name="M", target_rows=100_000, repeats=3),
    ScaleSpec(name="L", target_rows=1_000_000, repeats=1),
]


def parse_expression(text: str):
    tokens = Lexer(text).tokenize()
    return Parser(tokens).parse()


def build_rename_map(columns: list[str]) -> dict[str, str]:
    rename_map: dict[str, str] = {}
    if "ths_code" in columns and "code" not in columns:
        rename_map["ths_code"] = "code"
    return rename_map


def scan_workload_source(path: Path) -> pl.LazyFrame:
    lf = pl.scan_parquet(path)
    rename_map = build_rename_map(lf.collect_schema().names())
    if rename_map:
        lf = lf.rename(rename_map)

    return lf.select(["time", "code", "open", "close", "volume"])


def load_code_lengths(path: Path) -> pl.DataFrame:
    return (
        scan_workload_source(path)
        .group_by("code")
        .len()
        .sort("len")
        .collect()
    )


def select_code_plan(lengths: pl.DataFrame, *, target_rows: int) -> pl.DataFrame:
    ordered_rows = lengths.iter_rows(named=True)
    ordered_list = list(ordered_rows)

    mixed_order: list[dict[str, object]] = []
    left = 0
    right = len(ordered_list) - 1
    while left <= right:
        mixed_order.append(ordered_list[right])
        right -= 1
        if left <= right:
            mixed_order.append(ordered_list[left])
            left += 1

    selected_codes: list[str] = []
    desired_lengths: list[int] = []
    remaining = target_rows

    for row in mixed_order:
        if remaining <= 0:
            break
        keep_rows = min(int(row["len"]), remaining)
        selected_codes.append(str(row["code"]))
        desired_lengths.append(keep_rows)
        remaining -= keep_rows

    return pl.DataFrame({"code": selected_codes, "__desired_len": desired_lengths})


def load_workload_slice(path: Path, *, selection_plan: pl.DataFrame) -> pl.DataFrame:
    codes = selection_plan.get_column("code").to_list()
    desired_rows = selection_plan.select(pl.col("__desired_len").sum()).item()

    collected = (
        scan_workload_source(path)
        .filter(pl.col("code").is_in(codes))
        .collect()
    )

    workload = (
        collected.join(selection_plan, on="code", how="inner")
        .sort(["code", "time"])
        .with_columns((pl.col("code").cum_count().over("code") - 1).alias("__code_pos"))
        .filter(pl.col("__code_pos") < pl.col("__desired_len"))
        .drop(["__desired_len", "__code_pos"])
        .sample(fraction=1.0, shuffle=True, seed=42)
    )

    if workload.height != desired_rows:
        raise ValueError(
            f"Expected {desired_rows} rows in workload slice, got {workload.height}"
        )

    return workload


def summarize_workload(df: pl.DataFrame) -> WorkloadStats:
    group_lengths = df.group_by("code").len().get_column("len")
    return WorkloadStats(
        rows=df.height,
        code_count=df.get_column("code").n_unique(),
        min_group_len=int(group_lengths.min()),
        median_group_len=float(group_lengths.median()),
        max_group_len=int(group_lengths.max()),
    )


def summarize_runs(durations: list[float]) -> TimingSummary:
    return TimingSummary(
        mean_seconds=statistics.fmean(durations),
        min_seconds=min(durations),
        max_seconds=max(durations),
        repeat_count=len(durations),
    )


def measure(fn, *, repeats: int, warmup: bool = True) -> TimingSummary:
    if warmup:
        fn()

    durations: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        durations.append(time.perf_counter() - start)

    return summarize_runs(durations)


def benchmark_stage_breakdown(df: pl.DataFrame, *, segment_count: int) -> StageBreakdown:
    executor = Executor(df)
    prepared = None

    sort_start = time.perf_counter()
    prepared = executor._get_prepared_frame()
    sort_seconds = time.perf_counter() - sort_start

    segmented_start = time.perf_counter()
    segmented_view = executor._get_segmented_view(segment_count)
    segmented_view_seconds = time.perf_counter() - segmented_start

    compiled = [
        executor.compile(parse_expression("seg_mean(close, 3)")).alias("seg_close"),
        executor.compile(parse_expression("seg_sum(volume, 3)")).alias("seg_volume"),
        executor.compile(parse_expression("seg_count(close > open, 3)")).alias("seg_up"),
    ]

    aggregate_start = time.perf_counter()
    computed = segmented_view.select([prepared.row_index_name, *compiled])
    aggregate_broadcast_seconds = time.perf_counter() - aggregate_start

    restore_start = time.perf_counter()
    computed.sort(prepared.row_index_name).drop(prepared.row_index_name)
    restore_order_seconds = time.perf_counter() - restore_start

    return StageBreakdown(
        sort_seconds=sort_seconds,
        segmented_view_seconds=segmented_view_seconds,
        aggregate_broadcast_seconds=aggregate_broadcast_seconds,
        restore_order_seconds=restore_order_seconds,
    )


def run_serial_same_count(df: pl.DataFrame) -> None:
    engine = FactorEngine()
    engine.evaluate("seg_mean(close, 3)", df, output_name="seg_close")
    engine.evaluate("seg_sum(volume, 3)", df, output_name="seg_volume")
    engine.evaluate("seg_count(close > open, 3)", df, output_name="seg_up")


def run_evaluate_many_same_count(df: pl.DataFrame) -> None:
    engine = FactorEngine()
    engine.evaluate_many(
        [
            ("seg_close", "seg_mean(close, 3)"),
            ("seg_volume", "seg_sum(volume, 3)"),
            ("seg_up", "seg_count(close > open, 3)"),
        ],
        df,
    )


def run_serial_different_count(df: pl.DataFrame) -> None:
    engine = FactorEngine()
    engine.evaluate("seg_mean(close, 3)", df, output_name="seg3")
    engine.evaluate("seg_sum(close, 5)", df, output_name="seg5_sum")
    engine.evaluate("seg_any(close > open, 7)", df, output_name="seg7_any")


def run_evaluate_many_different_count(df: pl.DataFrame) -> None:
    engine = FactorEngine()
    engine.evaluate_many(
        [
            ("seg3", "seg_mean(close, 3)"),
            ("seg5_sum", "seg_sum(close, 5)"),
            ("seg7_any", "seg_any(close > open, 7)"),
        ],
        df,
    )


def run_mixed_expression(df: pl.DataFrame) -> None:
    FactorEngine().evaluate("ts_mean(close, 10) - seg_mean(close, 3)", df)


def run_where_expression(df: pl.DataFrame) -> None:
    FactorEngine().evaluate("where(close > seg_mean(close, 3), close, open)", df)


def benchmark_scale(
    path: Path,
    lengths: pl.DataFrame,
    scale: ScaleSpec,
) -> tuple[list[BenchmarkResult], StageBreakdown]:
    selection_plan = select_code_plan(lengths, target_rows=scale.target_rows)
    df = load_workload_slice(path, selection_plan=selection_plan)
    workload = summarize_workload(df)
    stage_breakdown = benchmark_stage_breakdown(df, segment_count=3)

    results = [
        BenchmarkResult(
            scale=scale.name,
            scenario="evaluate(seg_mean(close, 3))",
            timing=measure(
                lambda: FactorEngine().evaluate("seg_mean(close, 3)", df),
                repeats=scale.repeats,
            ),
            workload=workload,
        ),
        BenchmarkResult(
            scale=scale.name,
            scenario="serial same-count x3",
            timing=measure(lambda: run_serial_same_count(df), repeats=scale.repeats),
            workload=workload,
        ),
        BenchmarkResult(
            scale=scale.name,
            scenario="evaluate_many same-count x3",
            timing=measure(lambda: run_evaluate_many_same_count(df), repeats=scale.repeats),
            workload=workload,
        ),
        BenchmarkResult(
            scale=scale.name,
            scenario="serial different-count x3",
            timing=measure(lambda: run_serial_different_count(df), repeats=scale.repeats),
            workload=workload,
        ),
        BenchmarkResult(
            scale=scale.name,
            scenario="evaluate_many different-count x3",
            timing=measure(
                lambda: run_evaluate_many_different_count(df),
                repeats=scale.repeats,
            ),
            workload=workload,
        ),
        BenchmarkResult(
            scale=scale.name,
            scenario="evaluate(ts_mean(close, 10) - seg_mean(close, 3))",
            timing=measure(lambda: run_mixed_expression(df), repeats=scale.repeats),
            workload=workload,
        ),
        BenchmarkResult(
            scale=scale.name,
            scenario="evaluate(where(close > seg_mean(close, 3), close, open))",
            timing=measure(lambda: run_where_expression(df), repeats=scale.repeats),
            workload=workload,
        ),
    ]

    return results, stage_breakdown


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


def summarize_answers(
    benchmark_results: list[BenchmarkResult],
    stage_breakdowns: dict[str, StageBreakdown],
) -> list[str]:
    largest_scale = max(SCALES, key=lambda item: item.target_rows).name
    largest_breakdown = stage_breakdowns[largest_scale]
    total = largest_breakdown.total_seconds or 1e-12
    view_share = largest_breakdown.segmented_view_seconds / total

    same_serial = lookup_result(
        benchmark_results,
        scale=largest_scale,
        scenario="serial same-count x3",
    )
    same_many = lookup_result(
        benchmark_results,
        scale=largest_scale,
        scenario="evaluate_many same-count x3",
    )
    same_ratio = same_many.timing.mean_seconds / max(same_serial.timing.mean_seconds, 1e-12)

    diff_many = lookup_result(
        benchmark_results,
        scale=largest_scale,
        scenario="evaluate_many different-count x3",
    )
    diff_ratio = diff_many.timing.mean_seconds / max(same_many.timing.mean_seconds, 1e-12)

    mixed = lookup_result(
        benchmark_results,
        scale=largest_scale,
        scenario="evaluate(ts_mean(close, 10) - seg_mean(close, 3))",
    )
    single = lookup_result(
        benchmark_results,
        scale=largest_scale,
        scenario="evaluate(seg_mean(close, 3))",
    )
    mixed_ratio = mixed.timing.mean_seconds / max(single.timing.mean_seconds, 1e-12)

    return [
        (
            f"- Q1: 在 `{largest_scale}` 档真实 workload 里，segmented view 构造约占 stage benchmark 的 "
            f"`{view_share:.1%}`；这能直接判断 `segment_id` 和分段准备是否还是主要瓶颈。"
        ),
        (
            f"- Q2: `{largest_scale}` 档里，`evaluate_many same-count x3 / serial same-count x3 = {same_ratio:.2f}`。"
            " 这个比值越低，说明同一 `segment_count` 的 prepared view 复用越有真实价值。"
        ),
        (
            f"- Q3: `{largest_scale}` 档里，`evaluate_many different-count x3 / evaluate_many same-count x3 = {diff_ratio:.2f}`。"
            " 如果不同 `segment_count` 明显更贵，后续优化就应该围绕跨 count 成本边界，而不是继续盲目扩函数。"
        ),
        (
            f"- Q4: `{largest_scale}` 档里，`mixed(ts_mean - seg_mean) / single(seg_mean) = {mixed_ratio:.2f}`。"
            " 这个比值用来判断 segmented 在 mixed workload 里的额外负担是否已经足够可控。"
        ),
    ]


def render_markdown(
    path: Path,
    benchmark_results: list[BenchmarkResult],
    stage_breakdowns: dict[str, StageBreakdown],
) -> str:
    lines: list[str] = []
    lines.append("# Segmented Workload Benchmark (R12)")
    lines.append("")
    lines.append("Date: 2026-04-14")
    lines.append("")
    lines.append("Environment:")
    lines.append(f"- Python: {sys.version.split()[0]}")
    lines.append(f"- Polars: {pl.__version__}")
    lines.append(f"- Source data: `{path}`")
    lines.append("- Input shape: real intraday parquet, normalized to `time / code / open / close / volume`")
    lines.append("- Workload shaping: uneven per-code lengths selected from real distribution, then shuffled to preserve out-of-order input")
    lines.append("")
    lines.append("## Workload Stats")
    lines.append("")
    lines.append("| scale | rows | codes | min group | median group | max group |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    seen_scales: set[str] = set()
    for result in benchmark_results:
        if result.scale in seen_scales:
            continue
        seen_scales.add(result.scale)
        workload = result.workload
        lines.append(
            f"| {result.scale} | {workload.rows:,} | {workload.code_count:,} | "
            f"{workload.min_group_len} | {workload.median_group_len:.1f} | {workload.max_group_len} |"
        )
    lines.append("")
    lines.append("## Stage Breakdown (`seg_mean/seg_sum/seg_count`, same-count x3 representative)")
    lines.append("")
    lines.append("| scale | sort (s) | segmented view (s) | aggregate+broadcast (s) | restore order (s) | view share |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for scale_name, breakdown in stage_breakdowns.items():
        total = breakdown.total_seconds or 1e-12
        view_share = breakdown.segmented_view_seconds / total
        lines.append(
            f"| {scale_name} | {breakdown.sort_seconds:.6f} | {breakdown.segmented_view_seconds:.6f} | "
            f"{breakdown.aggregate_broadcast_seconds:.6f} | {breakdown.restore_order_seconds:.6f} | {view_share:.1%} |"
        )
    lines.append("")
    lines.append("## Wall Time")
    lines.append("")
    lines.append("| scale | scenario | mean (s) | min (s) | max (s) | repeats |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: |")
    for result in benchmark_results:
        lines.append(
            f"| {result.scale} | {result.scenario} | {result.timing.mean_seconds:.6f} | "
            f"{result.timing.min_seconds:.6f} | {result.timing.max_seconds:.6f} | {result.timing.repeat_count} |"
        )
    lines.append("")
    lines.append("## Q1 / Q2 / Q3 / Q4")
    lines.append("")
    lines.extend(summarize_answers(benchmark_results, stage_breakdowns))
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    data_path = Path(
        os.getenv("FACTOR_ENGINE_SEGMENTED_WORKLOAD_PATH", str(DEFAULT_DATA_PATH))
    )
    lengths = load_code_lengths(data_path)

    all_results: list[BenchmarkResult] = []
    stage_breakdowns: dict[str, StageBreakdown] = {}
    for scale in SCALES:
        results, breakdown = benchmark_scale(data_path, lengths, scale)
        all_results.extend(results)
        stage_breakdowns[scale.name] = breakdown

    markdown = render_markdown(data_path, all_results, stage_breakdowns)
    output_dir = PROJECT_ROOT / "benchmarks"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "segmented_workload.md"
    output_path.write_text(markdown, encoding="utf-8")

    print(markdown)
    print(f"Saved workload benchmark report to {output_path}")


if __name__ == "__main__":
    main()
