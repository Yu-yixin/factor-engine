from __future__ import annotations

import csv
import ctypes
from ctypes import wintypes
import json
import os
import platform
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def current_rss_mb() -> float:
    try:
        import psutil  # type: ignore[import-not-found]

        return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    except Exception:
        pass

    if os.name == "nt":
        try:
            class ProcessMemoryCounters(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            counters = ProcessMemoryCounters()
            counters.cb = ctypes.sizeof(ProcessMemoryCounters)
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.GetCurrentProcess.restype = wintypes.HANDLE
            psapi = ctypes.WinDLL("psapi", use_last_error=True)
            psapi.GetProcessMemoryInfo.argtypes = [
                wintypes.HANDLE,
                ctypes.POINTER(ProcessMemoryCounters),
                wintypes.DWORD,
            ]
            psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
            handle = kernel32.GetCurrentProcess()
            ok = psapi.GetProcessMemoryInfo(
                handle,
                ctypes.byref(counters),
                counters.cb,
            )
            if ok:
                return counters.WorkingSetSize / (1024 * 1024)
        except Exception:
            pass

    try:
        import resource

        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return float(usage) / 1024
    except Exception:
        return 0.0


@dataclass
class StageEvent:
    event_type: str
    stage_id: str
    batch_id: str
    order_index: int
    stage_kind: str
    expr_key: str
    frame_col_count: int
    rss_mb: float
    consumer_kind: str | None = None
    alive_at_batch_end: bool | None = None
    is_drop_candidate_at_batch_end: bool | None = None
    planned_consumer_count_total: int | None = None
    planned_consumer_count_remaining: int | None = None
    actual_consume_count: int | None = None
    planned_last_use_order_index: int | None = None
    kept_alive_for_planned_reuse: bool | None = None
    dropped_after_planned_last_use: bool | None = None
    recomputed_after_drop: bool | None = None


@dataclass
class StageDetail:
    stage_id: str
    batch_id: str
    expr_key: str
    stage_kind: str
    producer_route: str
    created_order_index: int
    consumer_count_total_estimate: int
    last_use_order_index_estimate: int | None
    alive_at_batch_end: bool
    column_name: str
    frame_col_count_at_create: int
    frame_col_count_at_last_use_estimate: int | None
    rss_at_create_mb: float
    rss_at_last_use_estimate_mb: float | None
    is_short_lived_candidate: bool
    is_drop_candidate_at_batch_end: bool
    dropped: bool = False
    planned_consumer_count_total: int = 0
    planned_last_use_order_index: int | None = None
    actual_consume_count: int = 0
    recomputed_after_drop: bool = False
    kept_alive_for_planned_reuse: bool = False
    dropped_after_planned_last_use: bool = False


@dataclass
class BatchDetail:
    batch_id: str
    route: str
    expression_count: int
    rows: int
    groups: int
    batch_total_time_ms: float
    prepare_sort_time_ms: float
    stage_materialize_time_ms: float
    restore_time_ms: float
    append_time_ms: float
    rss_before_mb: float
    rss_after_mb: float
    peak_rss_mb: float
    base_frame_col_count: int
    peak_frame_col_count: int
    final_frame_col_count: int
    stage_count: int
    peak_live_stage_count_estimate: int
    alive_stage_at_batch_end_count: int
    materialized_stage_count: int
    positional_stage_count: int
    staged_prefix_stage_count: int
    dropped_stage_count: int = 0
    planned_reusable_stage_count: int = 0
    recomputed_stage_count: int = 0
    avoided_recomputation_count: int = 0
    late_alive_stage_count: int = 0


@dataclass
class PositionalPhaseDetail:
    run_id: str
    batch_id: str
    expression: str
    output_name: str
    function_name: str
    rows: int
    groups: int
    window: int
    child_stage_kind: str
    prepare_sort_time_ms: float
    child_expr_time_ms: float
    positional_total_time_ms: float
    positional_to_list_time_ms: float
    positional_group_scan_time_ms: float
    result_attach_time_ms: float
    restore_time_ms: float
    python_kernel_used: bool
    native_kernel_used: bool
    group_count: int
    avg_group_size: float
    max_group_size: int
    output_non_null_count: int
    rss_before_mb: float
    rss_after_mb: float
    peak_rss_mb: float
    native_low_copy_bridge_used: bool = False
    python_object_bridge_used: bool = False
    native_parallel_used: bool = False
    group_parallelism_level: int = 1


@dataclass
class RunProfileSummary:
    run_id: str
    timestamp: str
    benchmark_name: str
    dataset_name: str
    row_count: int
    group_count: int
    input_column_count: int
    expression_count: int
    mode: str
    total_time_sec: float
    peak_rss_mb: float
    result_column_count: int
    total_stage_count: int
    peak_live_stage_count_estimate: int
    peak_frame_col_count: int
    alive_stage_at_batch_end_count: int
    ordered_batch_count: int
    materialized_stage_count: int
    positional_stage_count: int
    staged_prefix_stage_count: int
    dropped_stage_count: int = 0
    total_recomputed_stage_count: int = 0
    total_avoided_recomputation_count: int = 0
    total_planned_reusable_stage_count: int = 0
    late_alive_stage_count: int = 0
    python_version: str | None = None
    platform: str | None = None


@dataclass(frozen=True)
class ProfileArtifacts:
    latest_run_json: Path
    history_csv: Path
    latest_batch_details_jsonl: Path
    latest_stage_details_jsonl: Path
    latest_stage_events_jsonl: Path
    latest_positional_phase_details_jsonl: Path
    benchmark_report_md: Path


class StageLifecycleProfiler:
    def __init__(
        self,
        *,
        benchmark_name: str,
        dataset_name: str,
        mode: str,
        row_count: int,
        group_count: int,
        input_column_count: int,
        expression_count: int,
    ) -> None:
        self.run_id = uuid4().hex
        self.benchmark_name = benchmark_name
        self.dataset_name = dataset_name
        self.mode = mode
        self.row_count = row_count
        self.group_count = group_count
        self.input_column_count = input_column_count
        self.expression_count = expression_count
        self._start = time.perf_counter()
        self.peak_rss_mb = current_rss_mb()
        self.batches: list[BatchDetail] = []
        self.stages: list[StageDetail] = []
        self.events: list[StageEvent] = []
        self.positional_phases: list[PositionalPhaseDetail] = []
        self.summary: RunProfileSummary | None = None

    def observe_rss(self) -> float:
        rss = current_rss_mb()
        self.peak_rss_mb = max(self.peak_rss_mb, rss)
        return rss

    def add_event(self, event: StageEvent) -> None:
        self.events.append(event)
        self.peak_rss_mb = max(self.peak_rss_mb, event.rss_mb)

    def add_stage(self, stage: StageDetail) -> None:
        self.stages.append(stage)

    def add_batch(self, batch: BatchDetail) -> None:
        self.batches.append(batch)
        self.peak_rss_mb = max(self.peak_rss_mb, batch.peak_rss_mb)

    def add_positional_phase(self, detail: PositionalPhaseDetail) -> None:
        self.positional_phases.append(detail)
        self.peak_rss_mb = max(self.peak_rss_mb, detail.peak_rss_mb)

    def finish(self, *, result_column_count: int) -> RunProfileSummary:
        total_time_sec = time.perf_counter() - self._start
        summary = RunProfileSummary(
            run_id=self.run_id,
            timestamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            benchmark_name=self.benchmark_name,
            dataset_name=self.dataset_name,
            row_count=self.row_count,
            group_count=self.group_count,
            input_column_count=self.input_column_count,
            expression_count=self.expression_count,
            mode=self.mode,
            total_time_sec=total_time_sec,
            peak_rss_mb=self.peak_rss_mb,
            result_column_count=result_column_count,
            total_stage_count=len(self.stages),
            peak_live_stage_count_estimate=max(
                (item.peak_live_stage_count_estimate for item in self.batches),
                default=0,
            ),
            peak_frame_col_count=max((item.peak_frame_col_count for item in self.batches), default=0),
            alive_stage_at_batch_end_count=sum(
                item.alive_stage_at_batch_end_count for item in self.batches
            ),
            ordered_batch_count=len(self.batches),
            materialized_stage_count=sum(item.materialized_stage_count for item in self.batches),
            positional_stage_count=sum(item.positional_stage_count for item in self.batches),
            staged_prefix_stage_count=sum(item.staged_prefix_stage_count for item in self.batches),
            dropped_stage_count=sum(item.dropped_stage_count for item in self.batches),
            total_recomputed_stage_count=sum(item.recomputed_stage_count for item in self.batches),
            total_avoided_recomputation_count=sum(
                item.avoided_recomputation_count for item in self.batches
            ),
            total_planned_reusable_stage_count=sum(
                item.planned_reusable_stage_count for item in self.batches
            ),
            late_alive_stage_count=sum(item.late_alive_stage_count for item in self.batches),
            python_version=platform.python_version(),
            platform=platform.platform(),
        )
        self.summary = summary
        return summary

    def persist(self, output_dir: str | Path) -> ProfileArtifacts:
        if self.summary is None:
            raise RuntimeError("finish() must be called before persist()")

        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        latest_run = target_dir / "latest_run.json"
        history = target_dir / "history.csv"
        batches = target_dir / "latest_batch_details.jsonl"
        stages = target_dir / "latest_stage_details.jsonl"
        events = target_dir / "latest_stage_events.jsonl"
        positional_phases = target_dir / "latest_positional_phase_details.jsonl"
        report = target_dir / "benchmark_report.md"

        latest_run.write_text(
            json.dumps(asdict(self.summary), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self._append_history(history)
        self._write_jsonl(batches, self.batches)
        self._write_jsonl(stages, self.stages)
        self._write_jsonl(events, self.events)
        self._write_jsonl(positional_phases, self.positional_phases)
        report.write_text(self.render_markdown_report(), encoding="utf-8")

        return ProfileArtifacts(
            latest_run_json=latest_run,
            history_csv=history,
            latest_batch_details_jsonl=batches,
            latest_stage_details_jsonl=stages,
            latest_stage_events_jsonl=events,
            latest_positional_phase_details_jsonl=positional_phases,
            benchmark_report_md=report,
        )

    def render_markdown_report(self) -> str:
        if self.summary is None:
            raise RuntimeError("finish() must be called before render_markdown_report()")

        lines = [
            "# Stage Lifecycle Benchmark Report",
            "",
            f"- run_id: `{self.summary.run_id}`",
            f"- benchmark: `{self.summary.benchmark_name}`",
            f"- dataset: `{self.summary.dataset_name}`",
            f"- rows: `{self.summary.row_count}`",
            f"- groups: `{self.summary.group_count}`",
            f"- expressions: `{self.summary.expression_count}`",
            f"- total_time_sec: `{self.summary.total_time_sec:.6f}`",
            f"- peak_rss_mb: `{self.summary.peak_rss_mb:.2f}`",
            "",
            "## Batch Details",
            "",
            "| batch | route | exprs | stages | dropped | peak cols | final cols | alive at end | peak rss mb |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for batch in self.batches:
            lines.append(
                f"| `{batch.batch_id}` | `{batch.route}` | {batch.expression_count} | "
                f"{batch.stage_count} | {batch.dropped_stage_count} | "
                f"{batch.peak_frame_col_count} | {batch.final_frame_col_count} | "
                f"{batch.alive_stage_at_batch_end_count} | {batch.peak_rss_mb:.2f} |"
            )

        lines.extend(
            [
                "",
                "## Drop Candidates",
                "",
                "| stage | kind | column | consumers | alive at end | dropped |",
                "| --- | --- | --- | ---: | --- | --- |",
            ]
        )
        for stage in self.stages:
            if not stage.is_drop_candidate_at_batch_end and not stage.dropped:
                continue
            lines.append(
                f"| `{stage.stage_id}` | `{stage.stage_kind}` | `{stage.column_name}` | "
                f"{stage.consumer_count_total_estimate} | {stage.alive_at_batch_end} | {stage.dropped} |"
            )

        lines.extend(
            [
                "",
                "## Planned Lifecycle",
                "",
                "| batch | planned reusable | avoided recompute | recomputed | late alive |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for batch in self.batches:
            lines.append(
                f"| `{batch.batch_id}` | {batch.planned_reusable_stage_count} | "
                f"{batch.avoided_recomputation_count} | {batch.recomputed_stage_count} | "
                f"{batch.late_alive_stage_count} |"
            )

        if self.positional_phases:
            lines.extend(
                [
                    "",
                    "## Positional Phases",
                    "",
                    "| function | rows | groups | window | child ms | bridge ms | scan ms | attach ms | python | native | low-copy | parallel |",
                    "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |",
                ]
            )
            for phase in self.positional_phases:
                lines.append(
                    f"| `{phase.function_name}` | {phase.rows} | {phase.groups} | "
                    f"{phase.window} | {phase.child_expr_time_ms:.3f} | "
                    f"{phase.positional_to_list_time_ms:.3f} | "
                    f"{phase.positional_group_scan_time_ms:.3f} | "
                    f"{phase.result_attach_time_ms:.3f} | {phase.python_kernel_used} | "
                    f"{phase.native_kernel_used} | {phase.native_low_copy_bridge_used} | "
                    f"{phase.native_parallel_used} |"
                )

        return "\n".join(lines) + "\n"

    def _append_history(self, path: Path) -> None:
        row = asdict(self.summary)
        fieldnames = list(row)
        needs_header = not path.exists()
        with path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            if needs_header:
                writer.writeheader()
            writer.writerow(row)

    @staticmethod
    def _write_jsonl(path: Path, rows: list[object]) -> None:
        with path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(asdict(row), ensure_ascii=False) + "\n")
