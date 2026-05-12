from __future__ import annotations

import json
import math
import shutil
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from factor_engine.engine import FactorEngine  # noqa: E402
import factor_engine.executor as executor_module  # noqa: E402


FIELD_NOT_AVAILABLE = "FIELD_NOT_AVAILABLE"
UNKNOWN = "UNKNOWN"
LATEST_ROOT = PROJECT_ROOT / "benchmarks" / "latest" / "performance_truth"
REPORT_PATH = PROJECT_ROOT / "benchmarks" / "reports" / "performance_truth_baseline.md"
SCALEUP_REPORT_PATH = PROJECT_ROOT / "benchmarks" / "reports" / "performance_truth_scaleup.md"


def build_synthetic_frame(
    *,
    row_count: int,
    code_count: int,
    null_rate: float,
    seed: int = 20260512,
) -> pl.DataFrame:
    if row_count <= 0:
        raise ValueError("row_count must be positive")
    if code_count <= 0:
        raise ValueError("code_count must be positive")

    time_count = max(1, math.ceil(row_count / code_count))
    total_rows = code_count * time_count
    null_threshold = int(null_rate * 10_000)
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
                pl.concat_str([pl.lit("C"), pl.col("__code_idx").cast(pl.Utf8)]).alias("code"),
                pl.col("__time_idx").cast(pl.Int64).alias("time"),
                pl.concat_str([pl.lit("I"), (pl.col("__code_idx") % 12).cast(pl.Utf8)]).alias(
                    "industry"
                ),
                (
                    100.0
                    + pl.col("__code_idx") * 0.017
                    + pl.col("__time_idx") * 0.031
                    + ((pl.col("__code_idx") * 13 + pl.col("__time_idx") * 7 + seed) % 19)
                    * 0.011
                ).alias("close_raw"),
                (
                    99.0
                    + pl.col("__code_idx") * 0.015
                    + pl.col("__time_idx") * 0.027
                    + ((pl.col("__code_idx") * 5 + pl.col("__time_idx") * 11 + seed) % 23)
                    * 0.009
                ).alias("open_raw"),
                (
                    1000.0
                    + ((pl.col("__code_idx") * 29 + pl.col("__time_idx") * 17 + seed) % 7000)
                ).alias("volume_raw"),
            ]
        )
    )
    if null_threshold > 0:
        close_is_null = ((pl.col("row_id") * 37 + seed) % 10_000) < null_threshold
        open_is_null = ((pl.col("row_id") * 41 + seed) % 10_000) < null_threshold
        volume_is_null = ((pl.col("row_id") * 43 + seed) % 10_000) < null_threshold
        df = df.with_columns(
            [
                pl.when(close_is_null).then(None).otherwise(pl.col("close_raw")).alias("close"),
                pl.when(open_is_null).then(None).otherwise(pl.col("open_raw")).alias("open"),
                pl.when(volume_is_null).then(None).otherwise(pl.col("volume_raw")).alias("volume"),
            ]
        )
    else:
        df = df.with_columns(
            [
                pl.col("close_raw").alias("close"),
                pl.col("open_raw").alias("open"),
                pl.col("volume_raw").alias("volume"),
            ]
        )

    return (
        df.select(["time", "code", "industry", "open", "close", "volume"])
        .head(row_count)
        .sample(fraction=1.0, shuffle=True, seed=seed)
    )


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def clean_dir(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)


def value_or_field(row: dict[str, Any], key: str) -> Any:
    return row[key] if key in row else FIELD_NOT_AVAILABLE


def sum_batch_field(batches: list[dict[str, Any]], key: str) -> Any:
    if not batches or any(key not in batch for batch in batches):
        return FIELD_NOT_AVAILABLE
    return sum(float(batch[key]) for batch in batches)


def max_batch_field(batches: list[dict[str, Any]], key: str) -> Any:
    if not batches or any(key not in batch for batch in batches):
        return FIELD_NOT_AVAILABLE
    return max(batch[key] for batch in batches)


def infer_backend(operator: str, phases: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    if phases:
        if any(bool(item.get("native_kernel_used")) for item in phases):
            return "native"
        if any(bool(item.get("python_kernel_used")) for item in phases):
            return "python_fallback"
    if int(summary.get("ordered_batch_count", 0)) > 0:
        return "polars"
    return "unknown"


def evaluate_profiled(
    *,
    expressions: list[tuple[str, str]],
    df: pl.DataFrame,
    profile_dir: Path,
    benchmark_name: str,
    output_attach_mode: str | None = None,
    lifecycle: bool = False,
) -> tuple[pl.DataFrame, dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], float]:
    clean_dir(profile_dir)
    engine = FactorEngine()
    started = time.perf_counter()
    result = engine.evaluate_many(
        expressions,
        df,
        profiling=True,
        profile_output_dir=profile_dir,
        benchmark_name=benchmark_name,
        dataset_name="synthetic_performance_truth",
        lifecycle=lifecycle,
        output_attach_mode=output_attach_mode,
    )
    elapsed_ms = (time.perf_counter() - started) * 1000
    summary = read_json(profile_dir / "latest_run.json")
    batches = read_jsonl(profile_dir / "latest_batch_details.jsonl")
    phases = read_jsonl(profile_dir / "latest_positional_phase_details.jsonl")
    return result, summary, batches, phases, elapsed_ms


def correctness_smoke_passed(result: pl.DataFrame, df: pl.DataFrame, output_names: list[str]) -> bool:
    if result.height != df.height:
        return False
    for output_name in output_names:
        if output_name not in result.columns:
            return False
    return True


def write_artifact(name: str, rows: list[dict[str, Any]], *, update_baseline: bool = True) -> Path:
    LATEST_ROOT.mkdir(parents=True, exist_ok=True)
    path = LATEST_ROOT / name
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    if update_baseline:
        render_baseline_report()
    return path


def load_artifact(name: str) -> list[dict[str, Any]]:
    path = LATEST_ROOT / name
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return UNKNOWN
    if value == FIELD_NOT_AVAILABLE:
        return FIELD_NOT_AVAILABLE
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def numeric(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def top_numeric(rows: list[dict[str, Any]], key: str, limit: int) -> list[dict[str, Any]]:
    return sorted(
        [row for row in rows if numeric(row.get(key)) is not None],
        key=lambda row: float(row[key]),
        reverse=True,
    )[:limit]


def classify_decisions(
    rolling: list[dict[str, Any]],
    finalize: list[dict[str, Any]],
    mixed: list[dict[str, Any]],
) -> list[tuple[str, str, str]]:
    decisions: list[tuple[str, str, str]] = []
    slow_ops = {str(row.get("operator")) for row in top_numeric(rolling, "total_time_ms", 5)}
    finalize_rows = [row for row in finalize if numeric(row.get("restore_time_ms")) is not None]
    mixed_repeat = any(row.get("sorted_prepared_frame_reuse") == "rebuilt" for row in mixed)

    decisions.append(
        (
            "native ts_rank",
            "ACCEPT_NEXT" if "ts_rank" in slow_ops else "MEASURE_MORE",
            "measured slow top-5" if "ts_rank" in slow_ops else "not proven top-5 in current run",
        )
    )
    corr_cov_slow = bool({"corr", "cov"} & slow_ops)
    decisions.append(
        (
            "native corr/cov shared moments",
            "ACCEPT_NEXT" if corr_cov_slow else "MEASURE_MORE",
            "corr/cov measured top-5" if corr_cov_slow else "shared-moment benefit remains UNKNOWN",
        )
    )
    restore_significant = any(
        float(row["restore_time_ms"]) >= float(row["total_time_ms"]) * 0.15
        for row in finalize_rows
        if numeric(row.get("total_time_ms")) is not None
    )
    decisions.append(
        (
            "restore/finalize optimization",
            "ACCEPT_NEXT" if restore_significant else "MEASURE_MORE",
            "restore >= 15% of total in at least one measured case"
            if restore_significant
            else "restore/finalize significance not established",
        )
    )
    attach_peaks = {
        str(row.get("attach_mode")): row.get("peak_frame_col_count")
        for row in finalize
        if numeric(row.get("peak_frame_col_count")) is not None
    }
    changes_width = len(set(attach_peaks.values())) > 1
    decisions.append(
        (
            "output attach default mode change",
            "MEASURE_MORE" if changes_width else "DO_NOT_TOUCH_YET",
            "peak width changes by attach mode" if changes_width else "no measured peak-width case for changing default",
        )
    )
    decisions.append(
        (
            "mixed segmented+ordered prepared-frame reuse",
            "ACCEPT_NEXT" if mixed_repeat else "MEASURE_MORE",
            "prepare sort was rebuilt in mixed run" if mixed_repeat else "repeated sorting evidence is UNKNOWN/not observed",
        )
    )
    shared_nodes = any(numeric(row.get("shared_node_count")) for row in finalize)
    decisions.append(
        (
            "broader CSE expansion",
            "MEASURE_MORE" if shared_nodes else "DO_NOT_TOUCH_YET",
            "shared nodes observed but optimization target requires narrower proof"
            if shared_nodes
            else "no measured CSE pressure in current report",
        )
    )
    native_heavy = any(numeric(row.get("native_heavy_node_count")) for row in finalize)
    decisions.append(
        (
            "native-heavy active drop",
            "MEASURE_MORE" if native_heavy else "DO_NOT_TOUCH_YET",
            "native-heavy nodes observed; active-drop benefit remains UNKNOWN"
            if native_heavy
            else "no measured native-heavy pressure in current report",
        )
    )
    return decisions


def render_baseline_report() -> Path:
    rolling = load_artifact("rolling_operators.json")
    finalize = load_artifact("ordered_finalize_restore.json")
    mixed = load_artifact("mixed_segmented_ordered_sorting.json")
    slowest = top_numeric(rolling, "total_time_ms", 5)
    memory_heavy = top_numeric([*rolling, *finalize, *mixed], "peak_rss_mb", 5)

    restore_rows = [row for row in finalize if numeric(row.get("restore_time_ms")) is not None]
    restore_text = UNKNOWN
    if restore_rows:
        top_restore = max(restore_rows, key=lambda row: float(row["restore_time_ms"]))
        ratio = (
            float(top_restore["restore_time_ms"]) / float(top_restore["total_time_ms"])
            if numeric(top_restore.get("total_time_ms")) and float(top_restore["total_time_ms"])
            else 0.0
        )
        restore_text = (
            f"{fmt(top_restore['restore_time_ms'])} ms max restore ({ratio:.1%} of total in "
            f"{top_restore.get('case')}/{top_restore.get('attach_mode')})"
        )

    attach_width_text = UNKNOWN
    if finalize:
        width_by_mode = {
            str(row.get("attach_mode")): row.get("peak_frame_col_count")
            for row in finalize
            if numeric(row.get("peak_frame_col_count")) is not None
        }
        attach_width_text = (
            "changed peak width" if len(set(width_by_mode.values())) > 1 else "no peak-width change measured"
        )

    mixed_text = UNKNOWN
    if mixed:
        mixed_text = (
            "likely repeats sorting"
            if any(row.get("sorted_prepared_frame_reuse") == "rebuilt" for row in mixed)
            else "no repeated sort observed"
        )

    lines = [
        "# Performance Truth Baseline",
        "",
        "## Executive Summary",
        "",
        f"- top 5 slowest rolling operators: {', '.join(str(row.get('operator')) for row in slowest) or UNKNOWN}",
        "- top 5 memory-heavy cases: "
        + (
            ", ".join(
                f"{row.get('case', row.get('operator', 'case'))}={fmt(row.get('peak_rss_mb'), 2)} MB"
                for row in memory_heavy
            )
            or UNKNOWN
        ),
        f"- restore/finalize significance: {restore_text}",
        f"- output_attach_mode peak width: {attach_width_text}",
        f"- mixed segmented + ordered sorting: {mixed_text}",
        "",
        "## Per-Operator Ranking",
        "",
        "| Rank | Operator | Window | Null Rate | Rows | Time ms | Peak RSS MB | Backend | Notes |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for rank, row in enumerate(top_numeric(rolling, "total_time_ms", len(rolling)), start=1):
        lines.append(
            f"| {rank} | {row.get('operator')} | {row.get('window')} | {row.get('null_rate')} | "
            f"{row.get('row_count')} | {fmt(row.get('total_time_ms'))} | "
            f"{fmt(row.get('peak_rss_mb'), 2)} | {row.get('backend_path')} | "
            f"{row.get('notes', '')} |"
        )
    if not rolling:
        lines.append(f"| 1 | {UNKNOWN} |  |  |  |  |  |  | no rolling benchmark artifact found |")

    lines.extend(
        [
            "",
            "## Restore / Finalize Ranking",
            "",
            "| Case | Attach Mode | Expressions | Total ms | Restore ms | Finalize ms | Peak Frame Cols | Peak RSS MB |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in top_numeric(finalize, "total_time_ms", len(finalize)):
        lines.append(
            f"| {row.get('case')} | {row.get('attach_mode')} | {row.get('expression_count')} | "
            f"{fmt(row.get('total_time_ms'))} | {fmt(row.get('restore_time_ms'))} | "
            f"{fmt(row.get('finalize_select_time_ms'))} | {fmt(row.get('peak_frame_col_count'), 0)} | "
            f"{fmt(row.get('peak_rss_mb'), 2)} |"
        )
    if not finalize:
        lines.append(f"| {UNKNOWN} | {UNKNOWN} |  |  |  |  |  | no finalize benchmark artifact found |")

    lines.extend(
        [
            "",
            "## Mixed Route Sorting Findings",
            "",
            "| Case | Prepare Sort Count | Prepare Sort ms | Total ms | Evidence | Conclusion |",
            "| --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for row in mixed:
        lines.append(
            f"| {row.get('case')} | {fmt(row.get('prepare_sort_count'), 0)} | "
            f"{fmt(row.get('prepare_sort_time_ms'))} | {fmt(row.get('total_time_ms'))} | "
            f"{row.get('evidence')} | {row.get('conclusion')} |"
        )
    if not mixed:
        lines.append(f"| {UNKNOWN} |  |  |  | no mixed sorting benchmark artifact found | {UNKNOWN} |")

    lines.extend(["", "## Optimization Decision", "", "| Candidate | Classification | Basis |", "| --- | --- | --- |"])
    for candidate, classification, basis in classify_decisions(rolling, finalize, mixed):
        lines.append(f"| {candidate} | {classification} | {basis} |")

    lines.extend(
        [
            "",
            "Rules applied: bottlenecks are reported only from measured rows; unavailable profile fields are shown as FIELD_NOT_AVAILABLE; guessed causes are marked HYPOTHESIS.",
            "",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return REPORT_PATH


def _median_field(row: dict[str, Any]) -> Any:
    return row.get("median_time_ms", row.get("total_time_ms", FIELD_NOT_AVAILABLE))


def _scaling_class(time_ratio: float | None, row_ratio: float | None, cv: float | None) -> str:
    if time_ratio is None or row_ratio is None or row_ratio <= 0:
        return "unknown"
    if cv is not None and cv > 0.20:
        return "noisy"
    if time_ratio <= row_ratio * 1.35:
        return "stable_linear"
    return "superlinear_suspected"


def _case_key(row: dict[str, Any], *, row_count: int | None = None) -> tuple[Any, ...]:
    return (
        row.get("operator"),
        row_count if row_count is not None else row.get("row_count"),
        row.get("code_count"),
        row.get("window"),
        row.get("null_rate"),
        row.get("expression_count_mode"),
        row.get("expression_count"),
    )


def _find_scaled_pair(
    rows: list[dict[str, Any]],
    row: dict[str, Any],
    target_rows: int,
) -> dict[str, Any] | None:
    target_key = _case_key(row, row_count=target_rows)
    for candidate in rows:
        if _case_key(candidate) == target_key:
            return candidate
    return None


def _operator_representatives(
    rows: list[dict[str, Any]],
    *,
    scaling_rows: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    available_scaling_rows = scaling_rows or rows
    representatives: list[dict[str, Any]] = []
    for operator in sorted({str(row.get("operator")) for row in rows}):
        op_rows = [
            row
            for row in rows
            if row.get("operator") == operator and numeric(_median_field(row)) is not None
        ]
        if not op_rows:
            continue
        with_small_medium = [
            row
            for row in op_rows
            if _find_scaled_pair(available_scaling_rows, row, 2400) is not None
            and _find_scaled_pair(available_scaling_rows, row, 24000) is not None
        ]
        candidates = with_small_medium or op_rows
        representatives.append(max(candidates, key=lambda item: float(_median_field(item))))
    return representatives


def _stable_bottleneck_decision(row: dict[str, Any]) -> str:
    cv = numeric(row.get("coefficient_of_variation"))
    rank = numeric(row.get("rank_by_median"))
    if cv is None or cv > 0.20:
        return "MEASURE_MORE"
    if row.get("operator") in {"argmax", "argmin"} and row.get("benchmark_path_tested") != "native":
        return "MEASURE_MORE"
    if rank is not None and rank <= 10:
        return "OPTIMIZE_NEXT"
    return "NOT_A_BOTTLENECK"


def _backend_label(row: dict[str, Any]) -> str:
    if row.get("operator") in {"argmax", "argmin"}:
        tested = row.get("benchmark_path_tested", UNKNOWN)
        native_used = row.get("native_path_used", UNKNOWN)
        fallback_used = row.get("python_fallback_used", UNKNOWN)
        return f"{tested}; native={native_used}; fallback={fallback_used}"
    return str(row.get("backend_path", UNKNOWN))


def _scale_notes(rows: list[dict[str, Any]], row: dict[str, Any]) -> tuple[str, str, str, str]:
    small = _find_scaled_pair(rows, row, 2400)
    medium = _find_scaled_pair(rows, row, 24000)
    large = _find_scaled_pair(rows, row, 120000)
    small_ms = fmt(_median_field(small), 3) if small else UNKNOWN
    medium_ms = fmt(_median_field(medium), 3) if medium else UNKNOWN
    large_ms = fmt(_median_field(large), 3) if large else UNKNOWN
    growth = UNKNOWN
    scaling = "unknown"
    notes = []
    if small and medium:
        small_value = float(_median_field(small))
        medium_value = float(_median_field(medium))
        growth_ratio = medium_value / small_value if small_value else None
        row_ratio = 24000 / 2400
        cv = numeric(medium.get("coefficient_of_variation"))
        scaling = _scaling_class(growth_ratio, row_ratio, cv)
        growth = f"2.4k->24k {growth_ratio:.2f}x time / {row_ratio:.2f}x rows"
    if medium and large:
        medium_value = float(_median_field(medium))
        large_value = float(_median_field(large))
        growth_ratio = large_value / medium_value if medium_value else None
        row_ratio = 120000 / 24000
        cv = numeric(large.get("coefficient_of_variation"))
        large_scaling = _scaling_class(growth_ratio, row_ratio, cv)
        notes.append(f"24k->120k {growth_ratio:.2f}x time / {row_ratio:.2f}x rows ({large_scaling})")
        if scaling == "unknown":
            scaling = large_scaling
    return small_ms, medium_ms, large_ms, growth, f"{scaling}; {'; '.join(notes)}".strip("; ")


def _phase1_top_overlap(rows: list[dict[str, Any]]) -> str:
    phase1 = {"cov", "ts_rank", "argmin", "argmax"}
    top = {
        str(row.get("operator"))
        for row in sorted(
            [row for row in rows if numeric(_median_field(row)) is not None],
            key=lambda item: float(_median_field(item)),
            reverse=True,
        )[:10]
    }
    overlap = sorted(phase1 & top)
    return ", ".join(overlap) if overlap else "UNKNOWN"


def _final_recommendation(rows: list[dict[str, Any]]) -> tuple[str, str]:
    stable_rows = [
        row
        for row in rows
        if numeric(row.get("coefficient_of_variation")) is not None
        and float(row["coefficient_of_variation"]) <= 0.20
    ]
    if len(stable_rows) < max(5, len(rows) // 2):
        return "D", "Do more measurement because results are unstable"
    top_stable = [
        row
        for row in sorted(stable_rows, key=lambda item: float(_median_field(item)), reverse=True)
        if row.get("operator") not in {"argmax", "argmin"}
        or row.get("benchmark_path_tested") == "native"
    ][:10]
    top_ops = {str(row.get("operator")) for row in top_stable}
    if {"corr", "cov"} & top_ops:
        return "A", "Start native/shared-moment design for corr/cov"
    if "ts_rank" in top_ops:
        return "B", "Start ts_rank optimization design"
    return "D", "Do more measurement because results are unstable"


def render_scaleup_report(rows: list[dict[str, Any]], output_report: str | Path | None = None) -> Path:
    report_path = Path(output_report) if output_report is not None else SCALEUP_REPORT_PATH
    scaling_rows = [*load_artifact("rolling_operators.json"), *rows]
    sorted_rows = sorted(
        [row for row in rows if numeric(_median_field(row)) is not None],
        key=lambda item: float(_median_field(item)),
        reverse=True,
    )
    for rank, row in enumerate(sorted_rows, start=1):
        row["rank_by_median"] = row.get("rank_by_median", rank)

    stable_top = [
        row
        for row in sorted_rows
        if numeric(row.get("coefficient_of_variation")) is not None
        and float(row["coefficient_of_variation"]) <= 0.20
    ][:10]
    non_positional_stable_top = [
        row
        for row in sorted_rows
        if row.get("operator") not in {"argmax", "argmin"}
        and numeric(row.get("coefficient_of_variation")) is not None
        and float(row["coefficient_of_variation"]) <= 0.20
    ][:10]
    non_positional_top_ops = {str(row.get("operator")) for row in non_positional_stable_top}
    positional_rows = [row for row in rows if row.get("operator") in {"argmax", "argmin"}]
    positional_paths = sorted({str(row.get("benchmark_path_tested", UNKNOWN)) for row in positional_rows})
    recommendation_code, recommendation_text = _final_recommendation(rows)
    stable_enough = (
        "yes"
        if len(stable_top) >= 3 and recommendation_code != "D"
        else "no"
    )

    lines = [
        "# Performance Truth Scale-Up",
        "",
        "## Executive Summary",
        "",
        f"- matrix actually run: {len(rows)} cases, 1 warmup run, 3 measured runs per case.",
        f"- Phase-1 top bottleneck overlap: {_phase1_top_overlap(rows)}.",
        "- cov/corr/ts_rank dominate at larger scale: "
        + (
            "yes among non-positional candidates"
            if {"cov", "corr", "ts_rank"} & non_positional_top_ops
            else "UNKNOWN"
        )
        + ".",
        f"- argmax/argmin native dependency: benchmark paths observed = {', '.join(positional_paths) or UNKNOWN}.",
        f"- timings stable enough to optimize: {stable_enough}.",
        f"- final recommendation: {recommendation_code}. {recommendation_text}.",
        "",
        "## Stable Bottleneck Ranking",
        "",
        "| Rank | Operator | Rows | Codes | Window | Null Rate | Median ms | CV | Scaling | Backend | Decision |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in sorted_rows[:30]:
        _small, _medium, _large, _growth, scaling_note = _scale_notes(scaling_rows, row)
        scaling = scaling_note.split("; ", 1)[0] if scaling_note else "unknown"
        lines.append(
            f"| {row.get('rank_by_median')} | {row.get('operator')} | {row.get('row_count')} | "
            f"{row.get('code_count')} | {row.get('window')} | {row.get('null_rate')} | "
            f"{fmt(_median_field(row))} | {fmt(row.get('coefficient_of_variation'))} | "
            f"{scaling} | {_backend_label(row)} | {_stable_bottleneck_decision(row)} |"
        )

    lines.extend(
        [
            "",
            "## Scaling Findings",
            "",
            "| Operator | Small ms | Medium ms | Large ms | Growth | Scaling Class | Notes |",
            "| --- | ---: | ---: | ---: | --- | --- | --- |",
        ]
    )
    for row in _operator_representatives(rows, scaling_rows=scaling_rows):
        small_ms, medium_ms, large_ms, growth, scaling_note = _scale_notes(scaling_rows, row)
        scaling_class = scaling_note.split("; ", 1)[0] if scaling_note else "unknown"
        notes = scaling_note.split("; ", 1)[1] if "; " in scaling_note else ""
        lines.append(
            f"| {row.get('operator')} | {small_ms} | {medium_ms} | {large_ms} | "
            f"{growth} | {scaling_class} | {notes or 'UNKNOWN'} |"
        )

    native_available_values = sorted({str(row.get("native_available", UNKNOWN)) for row in positional_rows})
    native_requested_values = sorted({str(row.get("native_requested", UNKNOWN)) for row in positional_rows})
    lines.extend(
        [
            "",
            "## Native Positional Finding",
            "",
            (
                "argmax/argmin backend status: "
                f"native_available={','.join(native_available_values) or UNKNOWN}; "
                f"native_requested={','.join(native_requested_values) or UNKNOWN}; "
                f"paths_tested={','.join(positional_paths) or UNKNOWN}. "
                "Do not interpret positional slowness as native slowness unless paths_tested includes native. "
                "Composed-case risk remains UNKNOWN unless nested positional cases are included."
            ),
            "",
            "## Recommendation",
            "",
            f"{recommendation_code}. {recommendation_text}",
            "",
            "Uncertain findings are marked UNKNOWN. Guessed explanations are marked HYPOTHESIS.",
            "",
        ]
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


@contextmanager
def counted_prepared_sorts() -> Iterator[dict[str, Any]]:
    original = executor_module.build_prepared_frame
    state: dict[str, Any] = {"count": 0, "time_ms": 0.0}

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        started = time.perf_counter()
        try:
            return original(*args, **kwargs)
        finally:
            state["count"] += 1
            state["time_ms"] += (time.perf_counter() - started) * 1000

    executor_module.build_prepared_frame = wrapper
    try:
        yield state
    finally:
        executor_module.build_prepared_frame = original


def route_groups(expressions: list[tuple[str, str]], df: pl.DataFrame) -> dict[str, int]:
    engine = FactorEngine()
    groups: dict[str, int] = {}
    for _name, expression in expressions:
        try:
            route = str(engine.inspect_plan(expression, df).get("route", UNKNOWN))
        except Exception:
            route = UNKNOWN
        groups[route] = groups.get(route, 0) + 1
    return groups
