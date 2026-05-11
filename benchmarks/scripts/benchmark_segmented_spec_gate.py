from __future__ import annotations

import math
import os
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


DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "minute_2026_03.parquet"
POC_GROUP_SIZE = 8
BASE_CODE_COUNT = 64


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
class ScenarioSpec:
    name: str
    expressions: list[tuple[str, str]]


@dataclass(frozen=True)
class ScenarioMetrics:
    view_build_seconds: float
    aggregation_seconds: float
    cache_hit_ratio: float
    prepare_calls: int
    view_requests: int


@dataclass(frozen=True)
class BenchmarkResult:
    scale: str
    scenario: str
    timing: TimingSummary
    metrics: ScenarioMetrics
    workload: WorkloadStats


@dataclass(frozen=True)
class GateDecision:
    label: str
    q1_ratio: float
    q2_ratio: float
    q3_ratio: float


SCALES = [
    ScaleSpec(name="S", target_rows=10_000, repeats=5),
    ScaleSpec(name="M", target_rows=100_000, repeats=3),
    ScaleSpec(name="L", target_rows=500_000, repeats=1),
]


SCENARIOS = [
    ScenarioSpec(
        name="evaluate(seg_mean(close, 3))",
        expressions=[("seg_count", "seg_mean(close, 3)")],
    ),
    ScenarioSpec(
        name="evaluate(seglen_mean(close, [3,5,2]))",
        expressions=[("seg_length", "seglen_mean(close, [3, 5, 2])")],
    ),
    ScenarioSpec(
        name="evaluate_many same-length x3",
        expressions=[
            ("seg_close", "seglen_mean(close, [3, 5, 2])"),
            ("seg_open", "seglen_mean(open, [3, 5, 2])"),
            ("seg_spread", "seglen_mean(close - open, [3, 5, 2])"),
        ],
    ),
    ScenarioSpec(
        name="evaluate_many different-length x3",
        expressions=[
            ("seg_352", "seglen_mean(close, [3, 5, 2])"),
            ("seg_2222", "seglen_mean(close, [2, 2, 2, 2])"),
            ("seg_1010", "seglen_mean(close, [10, 10])"),
        ],
    ),
    ScenarioSpec(
        name="evaluate_many mixed count+length",
        expressions=[
            ("seg_count", "seg_mean(close, 3)"),
            ("seg_length", "seglen_mean(close, [3, 5, 2])"),
        ],
    ),
    ScenarioSpec(
        name="diversity sweep (1 unique spec)",
        expressions=[
            ("spec_352", "seglen_mean(close, [3, 5, 2])"),
        ],
    ),
    ScenarioSpec(
        name="diversity sweep (2 unique specs)",
        expressions=[
            ("spec_352", "seglen_mean(close, [3, 5, 2])"),
            ("spec_2222", "seglen_mean(close, [2, 2, 2, 2])"),
        ],
    ),
    ScenarioSpec(
        name="diversity sweep (4 unique specs)",
        expressions=[
            ("spec_352", "seglen_mean(close, [3, 5, 2])"),
            ("spec_2222", "seglen_mean(close, [2, 2, 2, 2])"),
            ("spec_1010", "seglen_mean(close, [10, 10])"),
            ("spec_44", "seglen_mean(close, [4, 4])"),
        ],
    ),
    ScenarioSpec(
        name="diversity sweep (8 unique specs)",
        expressions=[
            ("spec_352", "seglen_mean(close, [3, 5, 2])"),
            ("spec_2222", "seglen_mean(close, [2, 2, 2, 2])"),
            ("spec_1010", "seglen_mean(close, [10, 10])"),
            ("spec_44", "seglen_mean(close, [4, 4])"),
            ("spec_11111111", "seglen_mean(close, [1, 1, 1, 1, 1, 1, 1, 1])"),
            ("spec_332", "seglen_mean(close, [3, 3, 2])"),
            ("spec_53", "seglen_mean(close, [5, 3])"),
            ("spec_422", "seglen_mean(close, [4, 2, 2])"),
        ],
    ),
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


def select_base_codes(lengths: pl.DataFrame, *, code_count: int) -> list[str]:
    eligible = [
        row["code"]
        for row in lengths.iter_rows(named=True)
        if int(row["len"]) >= POC_GROUP_SIZE
    ]
    if len(eligible) < code_count:
        raise ValueError(
            f"Expected at least {code_count} codes with >= {POC_GROUP_SIZE} rows, got {len(eligible)}"
        )

    selected: list[str] = []
    left = 0
    right = len(eligible) - 1
    while len(selected) < code_count and left <= right:
        selected.append(str(eligible[right]))
        right -= 1
        if len(selected) < code_count and left <= right:
            selected.append(str(eligible[left]))
            left += 1

    return selected[:code_count]


def load_base_groups(path: Path, *, codes: list[str], group_size: int) -> pl.DataFrame:
    collected = (
        scan_workload_source(path)
        .filter(pl.col("code").is_in(codes))
        .collect()
    )

    base = (
        collected.sort(["code", "time"])
        .with_columns((pl.col("code").cum_count().over("code") - 1).alias("__code_pos"))
        .filter(pl.col("__code_pos") < group_size)
        .drop("__code_pos")
    )

    return base


def build_scale_workload(base_groups: pl.DataFrame, *, target_rows: int) -> pl.DataFrame:
    rows_per_replica = base_groups.height
    replica_count = max(1, math.ceil(target_rows / rows_per_replica))
    replicas = pl.DataFrame({"__replica": list(range(replica_count))})

    replicated = (
        base_groups.join(replicas, how="cross")
        .with_columns(
            pl.format("{}#{}", pl.col("code"), pl.col("__replica")).alias("code")
        )
        .drop("__replica")
        .head(target_rows)
        .sample(fraction=1.0, shuffle=True, seed=42)
    )

    return replicated


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


def run_scenario(df: pl.DataFrame, scenario: ScenarioSpec) -> None:
    engine = FactorEngine()
    if len(scenario.expressions) == 1:
        output_name, expression = scenario.expressions[0]
        engine.evaluate(expression, df, output_name=output_name)
        return

    engine.evaluate_many(scenario.expressions, df)


def profile_scenario(df: pl.DataFrame, scenario: ScenarioSpec) -> ScenarioMetrics:
    executor = Executor(df)
    prepared = executor._get_prepared_frame()
    parsed_items = [
        (output_name, parse_expression(expression))
        for output_name, expression in scenario.expressions
    ]

    grouped_items: dict[object, list[tuple[str, object]]] = {}
    for output_name, expr in parsed_items:
        spec_key = executor._get_segment_spec_key(expr)
        grouped_items.setdefault(spec_key, []).append((output_name, expr))

    prepare_calls = 0
    prepare_seconds = 0.0
    original_prepare = Executor._prepare_segmented_sorted_df

    def timed_prepare(self, sorted_df, *, segment_spec_key):
        nonlocal prepare_calls, prepare_seconds
        start = time.perf_counter()
        result = original_prepare(self, sorted_df, segment_spec_key=segment_spec_key)
        prepare_seconds += time.perf_counter() - start
        prepare_calls += 1
        return result

    Executor._prepare_segmented_sorted_df = timed_prepare
    try:
        aggregation_seconds = 0.0
        for spec_key, items in grouped_items.items():
            segmented_df = executor._get_segmented_view(spec_key)
            compiled = [
                executor.compile(expr).alias(output_name)
                for output_name, expr in items
            ]
            start = time.perf_counter()
            segmented_df.select([prepared.row_index_name, *compiled])
            aggregation_seconds += time.perf_counter() - start
    finally:
        Executor._prepare_segmented_sorted_df = original_prepare

    view_requests = len(parsed_items)
    cache_hit_ratio = 0.0
    if view_requests > 0:
        cache_hit_ratio = (view_requests - prepare_calls) / view_requests

    return ScenarioMetrics(
        view_build_seconds=prepare_seconds,
        aggregation_seconds=aggregation_seconds,
        cache_hit_ratio=cache_hit_ratio,
        prepare_calls=prepare_calls,
        view_requests=view_requests,
    )


def benchmark_scale(df: pl.DataFrame, scale: ScaleSpec) -> list[BenchmarkResult]:
    workload = summarize_workload(df)
    results: list[BenchmarkResult] = []

    for scenario in SCENARIOS:
        timing = measure(lambda: run_scenario(df, scenario), repeats=scale.repeats)
        metrics = profile_scenario(df, scenario)
        results.append(
            BenchmarkResult(
                scale=scale.name,
                scenario=scenario.name,
                timing=timing,
                metrics=metrics,
                workload=workload,
            )
        )

    return results


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


def decide_gate(benchmark_results: list[BenchmarkResult]) -> GateDecision:
    largest_scale = max(SCALES, key=lambda item: item.target_rows).name

    single_count = lookup_result(
        benchmark_results,
        scale=largest_scale,
        scenario="evaluate(seg_mean(close, 3))",
    )
    single_length = lookup_result(
        benchmark_results,
        scale=largest_scale,
        scenario="evaluate(seglen_mean(close, [3,5,2]))",
    )
    diversity_1 = lookup_result(
        benchmark_results,
        scale=largest_scale,
        scenario="diversity sweep (1 unique spec)",
    )
    diversity_8 = lookup_result(
        benchmark_results,
        scale=largest_scale,
        scenario="diversity sweep (8 unique specs)",
    )
    mixed = lookup_result(
        benchmark_results,
        scale=largest_scale,
        scenario="evaluate_many mixed count+length",
    )

    q1_ratio = single_length.timing.mean_seconds / max(single_count.timing.mean_seconds, 1e-12)
    q2_ratio = (
        diversity_8.timing.mean_seconds
        / max(diversity_1.timing.mean_seconds * 8, 1e-12)
    )
    q3_ratio = mixed.timing.mean_seconds / max(
        single_count.timing.mean_seconds + single_length.timing.mean_seconds,
        1e-12,
    )

    if q1_ratio <= 1.25 and q2_ratio <= 1.25 and q3_ratio <= 1.10:
        label = "GOOD"
    elif q1_ratio <= 2.00 and q2_ratio <= 1.50 and q3_ratio <= 1.25:
        label = "ACCEPTABLE"
    else:
        label = "BAD"

    return GateDecision(
        label=label,
        q1_ratio=q1_ratio,
        q2_ratio=q2_ratio,
        q3_ratio=q3_ratio,
    )


def render_markdown(
    path: Path,
    benchmark_results: list[BenchmarkResult],
    gate_decision: GateDecision,
) -> str:
    lines: list[str] = []
    lines.append("# Segmented Spec Gate Benchmark (R13.5-B)")
    lines.append("")
    lines.append("Date: 2026-04-14")
    lines.append("")
    lines.append("Environment:")
    lines.append(f"- Python: {sys.version.split()[0]}")
    lines.append(f"- Polars: {pl.__version__}")
    lines.append(f"- Source data: `{path}`")
    lines.append("- Input shape: real intraday parquet normalized to `time / code / open / close / volume`")
    lines.append(
        f"- Workload shaping: first `{POC_GROUP_SIZE}` rows per selected code, then replicated with suffixed code ids to keep PoC length specs legal while preserving out-of-order input"
    )
    lines.append(
        "- R13.5 note: length specs such as `[3,5,2]` and `[2,2,2,2]` require full group coverage, so this gate uses short per-code slices by design"
    )
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
    lines.append("## Scenario Metrics")
    lines.append("")
    lines.append(
        "| scale | scenario | total mean (s) | view build (s) | aggregation (s) | cache hit ratio | prepare calls | view requests |"
    )
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for result in benchmark_results:
        lines.append(
            f"| {result.scale} | {result.scenario} | {result.timing.mean_seconds:.6f} | "
            f"{result.metrics.view_build_seconds:.6f} | {result.metrics.aggregation_seconds:.6f} | "
            f"{result.metrics.cache_hit_ratio:.2f} | {result.metrics.prepare_calls} | {result.metrics.view_requests} |"
        )
    lines.append("")
    lines.append("## Gate Questions")
    lines.append("")
    lines.append(
        f"- Q1: `single(length) / single(count) = {gate_decision.q1_ratio:.2f}` on the largest scale."
    )
    lines.append(
        f"- Q2: `diversity(8) / (diversity(1) * 8) = {gate_decision.q2_ratio:.2f}` on the largest scale."
    )
    lines.append(
        f"- Q3: `mixed(count+length) / (single(count) + single(length)) = {gate_decision.q3_ratio:.2f}` on the largest scale."
    )
    lines.append("")
    lines.append("## Gate Decision")
    lines.append("")
    lines.append(f"- Decision: `{gate_decision.label}`")
    if gate_decision.label == "GOOD":
        lines.append("- Next step: seglen family may enter Phase 7 expansion.")
    elif gate_decision.label == "ACCEPTABLE":
        lines.append("- Next step: do not optimize yet; document usage constraints and keep the family frozen.")
    else:
        lines.append("- Next step: freeze seglen family and move to R13.6 optimization.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    data_path = Path(
        os.getenv("FACTOR_ENGINE_SEGMENTED_WORKLOAD_PATH", str(DEFAULT_DATA_PATH))
    )
    lengths = load_code_lengths(data_path)
    base_codes = select_base_codes(lengths, code_count=BASE_CODE_COUNT)
    base_groups = load_base_groups(
        data_path,
        codes=base_codes,
        group_size=POC_GROUP_SIZE,
    )

    all_results: list[BenchmarkResult] = []
    for scale in SCALES:
        df = build_scale_workload(base_groups, target_rows=scale.target_rows)
        all_results.extend(benchmark_scale(df, scale))

    gate_decision = decide_gate(all_results)
    markdown = render_markdown(data_path, all_results, gate_decision)
    output_dir = PROJECT_ROOT / "benchmarks" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "segmented_spec_gate.md"
    output_path.write_text(markdown, encoding="utf-8")

    print(markdown)
    print(f"Saved segmented spec gate report to {output_path}")


if __name__ == "__main__":
    main()
