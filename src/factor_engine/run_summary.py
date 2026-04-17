from __future__ import annotations

import csv
import json
import platform as platform_module
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


CSV_COLUMNS = [
    "timestamp",
    "mode",
    "data_path",
    "expression_source",
    "rows",
    "codes",
    "expressions",
    "success_count",
    "failed_count",
    "total_time_seconds",
    "load_time_seconds",
    "validate_time_seconds",
    "execute_time_seconds",
    "write_time_seconds",
    "output_path",
    "notes",
]


@dataclass(frozen=True)
class RunSummary:
    timestamp: str
    mode: str
    data_path: str
    expression_source: str
    rows: int
    codes: int | None
    expressions: int
    success_count: int
    failed_count: int
    total_time_seconds: float
    load_time_seconds: float | None
    validate_time_seconds: float | None
    execute_time_seconds: float | None
    write_time_seconds: float | None
    output_path: str | None
    notes: str | None
    benchmark_name: str | None = None
    exception_summary: str | None = None
    python_version: str | None = None
    platform: str | None = None
    git_like_version_marker: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SummaryArtifacts:
    latest_json_path: Path
    history_csv_path: Path


def build_run_summary(
    *,
    mode: str,
    data_path: str,
    expression_source: str,
    rows: int,
    codes: int | None,
    expressions: int,
    success_count: int,
    failed_count: int,
    total_time_seconds: float,
    load_time_seconds: float | None,
    validate_time_seconds: float | None,
    execute_time_seconds: float | None,
    write_time_seconds: float | None,
    output_path: str | None,
    notes: str | None,
    benchmark_name: str | None = None,
    exception_summary: str | None = None,
    git_like_version_marker: str | None = None,
) -> RunSummary:
    return RunSummary(
        timestamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        mode=mode,
        data_path=data_path,
        expression_source=expression_source,
        rows=rows,
        codes=codes,
        expressions=expressions,
        success_count=success_count,
        failed_count=failed_count,
        total_time_seconds=total_time_seconds,
        load_time_seconds=load_time_seconds,
        validate_time_seconds=validate_time_seconds,
        execute_time_seconds=execute_time_seconds,
        write_time_seconds=write_time_seconds,
        output_path=output_path,
        notes=notes,
        benchmark_name=benchmark_name,
        exception_summary=exception_summary,
        python_version=sys.version.split()[0],
        platform=platform_module.platform(),
        git_like_version_marker=git_like_version_marker,
    )


def resolve_benchmarks_dir(benchmarks_dir: str | Path | None = None) -> Path:
    if benchmarks_dir is not None:
        return Path(benchmarks_dir)
    return Path(__file__).resolve().parents[2] / "benchmarks"


def render_run_summary(summary: RunSummary) -> str:
    lines = [
        "[run-summary]",
        f"timestamp={summary.timestamp}",
        f"mode={summary.mode}",
        f"data_path={summary.data_path}",
        f"rows={summary.rows}",
        f"codes={summary.codes if summary.codes is not None else 'null'}",
        f"expressions={summary.expressions}",
        f"success_count={summary.success_count}",
        f"failed_count={summary.failed_count}",
        f"total_time_seconds={summary.total_time_seconds:.6f}",
        f"output_path={summary.output_path if summary.output_path is not None else 'null'}",
    ]
    return "\n".join(lines)


def write_latest_summary_json(
    summary: RunSummary,
    *,
    benchmarks_dir: str | Path | None = None,
) -> Path:
    target_dir = resolve_benchmarks_dir(benchmarks_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "latest_run.json"
    target.write_text(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def append_summary_history_csv(
    summary: RunSummary,
    *,
    benchmarks_dir: str | Path | None = None,
) -> Path:
    target_dir = resolve_benchmarks_dir(benchmarks_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "history.csv"
    needs_header = not target.exists()

    row = summary.to_dict()
    csv_row = {column: "" if row[column] is None else row[column] for column in CSV_COLUMNS}

    with target.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        if needs_header:
            writer.writeheader()
        writer.writerow(csv_row)

    return target


def persist_run_summary(
    summary: RunSummary,
    *,
    benchmarks_dir: str | Path | None = None,
) -> SummaryArtifacts:
    latest_json_path = write_latest_summary_json(summary, benchmarks_dir=benchmarks_dir)
    history_csv_path = append_summary_history_csv(summary, benchmarks_dir=benchmarks_dir)
    return SummaryArtifacts(
        latest_json_path=latest_json_path,
        history_csv_path=history_csv_path,
    )
