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
class MemoryEvent:
    event_type: str
    batch_id: str
    order_index: int
    frame_col_count: int
    rss_mb: float
    output_name: str | None = None
    buffer_id: str | None = None
    related_output_name: str | None = None
    bytes_estimate: int | None = None
    output_col_count: int | None = None
    stage_col_count: int | None = None
    native_buffer_alive_bytes_estimate: int | None = None
    native_parallel_used: bool | None = None
    parallel_worker_count: int | None = None


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
class OutputDetail:
    output_name: str
    batch_id: str
    created_order_index: int
    attached_order_index: int | None
    last_required_order_index: int | None
    alive_at_batch_end: bool
    is_late_alive_output: bool
    frame_col_count_at_attach: int | None
    rss_at_attach_mb: float | None
    source_column_name: str | None = None
    attached_to_working_frame: bool = False


@dataclass
class NativeBufferDetail:
    buffer_id: str
    batch_id: str
    related_output_name: str
    created_order_index: int
    attached_order_index: int | None
    released_order_index: int | None
    bytes_estimate: int
    alive_before_attach: bool
    alive_after_attach: bool
    release_lag_steps: int | None
    native_parallel_used: bool = False
    parallel_worker_count: int = 1


@dataclass
class NodeExecutionDetail:
    node_id: str
    batch_id: str
    lifecycle_mode: str
    identity: str
    materialization_kind: str
    materialization_reason: str
    materialization_eligibility: str
    node_lifecycle_class: str
    consumer_count: int
    reuse_consumer_count: int
    compute_count: int
    node_store_read_count: int
    hit_count: int
    compute_time_ms: float
    store_write_time_ms: float
    store_hit_time_ms: float
    planner_producer_step: int | None = None
    planner_consumer_steps: tuple[int, ...] = ()
    planner_last_use_step: int | None = None
    planner_ref_count_initial: int = 0
    planner_drop_candidate: bool = False
    planner_drop_blocker_reason: str = ""
    materialized_at_step: int | None = None
    first_read_step: int | None = None
    last_read_step: int | None = None
    retained_until_end: bool = True
    theoretical_release_step: int | None = None
    release_lag_steps: int | None = None
    restore_assemble_step: int | None = None
    append_step: int | None = None
    finalize_step: int | None = None
    batch_end_step: int | None = None
    structural_release_lag_steps: int | None = None
    retained_past_last_read: bool = False
    finalize_retention_lag_steps: int | None = None
    potential_live_bytes_step_savings: int = 0
    l2_first_wave_candidate: bool = False
    active_drop_eligible: bool = False
    dropped_at_step: int | None = None
    drop_expected_step: int | None = None
    drop_delay_steps: int | None = None
    drop_reason: str = ""
    ref_count_remaining_final: int = 0
    drop_missed: bool = False
    drop_miss_reason: str = ""
    node_depth: int = 0
    parent_node_id: str | None = None
    dependency_chain: tuple[str, ...] = ()
    bytes_estimate: int = 0
    native_heavy_lifecycle_eligibility: str = ""
    native_heavy_blocker_reason: str = ""
    native_compute_time_ms: float = 0.0
    native_path_normalization_time_ms: float = 0.0
    native_storage_residency_bytes: int = 0
    native_node_store_read_count: int = 0
    native_logical_consumer_count: int = 0
    native_effective_use_count: int = 0
    native_fallback_eval_count: int = 0
    native_rewrite_applied: bool = False
    native_helper_usage_pattern: str = ""
    helper_column_name: str | None = None
    helper_column_created_step: int | None = None
    helper_last_use_step: int | None = None
    helper_retained_until_end: bool = True
    helper_structural_lag_steps: int = 0
    helper_bytes_estimate: int = 0
    helper_potential_bytes_step_savings: int = 0
    helper_lifecycle_state: str = ""
    helper_drop_blocker_reason: str = ""
    helper_depth: int = 0
    parent_helper_column_name: str | None = None
    child_helper_columns: tuple[str, ...] = ()
    helper_logical_last_use_step: int | None = None
    helper_structural_dependency_end_step: int | None = None
    helper_drop_candidate: bool = False
    helper_drop_candidate_kind: str = ""
    helper_logical_death_step: int | None = None
    helper_drop_safe_step: int | None = None
    helper_drop_revalidated: bool = False
    helper_dropped_at_step: int | None = None
    helper_drop_delay_steps: int | None = None
    helper_drop_reason: str = ""
    helper_drop_missed: bool = False
    helper_drop_miss_reason: str = ""
    nested_helper_candidate: bool = False
    nested_helper_trace_events: tuple[str, ...] = ()
    nested_helper_miss_reason: str = ""
    recomputation_expansion_if_inline: int = 0
    recomputation_guardrail_pass: bool = False


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
    lifecycle_mode: str = "off"
    helper_lifecycle_mode: str = "off"
    dropped_stage_count: int = 0
    planned_reusable_stage_count: int = 0
    recomputed_stage_count: int = 0
    avoided_recomputation_count: int = 0
    late_alive_stage_count: int = 0
    peak_output_col_count: int = 0
    peak_stage_col_count: int = 0
    alive_output_at_batch_end_count: int = 0
    late_alive_output_count: int = 0
    native_output_buffer_count: int = 0
    native_output_buffer_peak_bytes_estimate: int = 0
    native_buffer_alive_before_attach: int = 0
    native_buffer_alive_after_attach: int = 0
    native_buffer_release_lag: int = 0
    peak_native_buffer_bytes_estimate: int = 0
    retained_for_reuse_stage_count: int = 0
    retained_for_output_stage_count: int = 0
    parallel_enabled: bool = False
    parallel_worker_count: int = 1
    parallel_buffer_peak_estimate: int = 0
    ast_node_count: int = 0
    dag_node_count: int = 0
    deduplicated_node_count: int = 0
    shared_node_count: int = 0
    materialized_node_count: int = 0
    expensive_node_count: int = 0
    result_store_peak_entry_count: int = 0
    finalize_time_ms: float = 0.0
    node_store_compute_calls: int = 0
    estimated_unshared_compute_calls: int = 0
    compiled_output_heavy_occurrence_count: int = 0
    compiled_fallback_eval_count: int = 0
    node_store_read_count: int = 0
    reuse_consumer_count: int = 0
    node_store_compute_time_ms: float = 0.0
    compiled_output_eval_time_ms: float = 0.0
    restore_assemble_time_ms: float = 0.0
    restore_assemble_step: int = 0
    append_step: int = 0
    finalize_step: int = 0
    batch_end_step: int = 0
    lifecycle_candidate_count: int = 0
    lifecycle_releasable_node_count: int = 0
    lifecycle_peak_live_node_count: int = 0
    lifecycle_peak_live_bytes_est: int = 0
    avg_release_lag_steps: float = 0.0
    max_release_lag_steps: int = 0
    avg_structural_release_lag_steps: float = 0.0
    max_structural_release_lag_steps: int = 0
    avg_finalize_retention_lag_steps: float = 0.0
    max_finalize_retention_lag_steps: int = 0
    potential_live_bytes_step_savings: int = 0
    l2_first_wave_candidate_count: int = 0
    dropped_node_count: int = 0
    drop_hit_count: int = 0
    drop_miss_count: int = 0
    peak_live_node_count_after_drop: int = 0
    peak_live_bytes_est_before_drop: int = 0
    peak_live_bytes_est_after_drop: int = 0
    drop_delay_steps_avg: float = 0.0
    drop_delay_steps_max: int = 0
    lifecycle_effective: bool = False
    multi_node_overlap_peak: int = 0
    multi_node_peak_live_bytes_before: int = 0
    multi_node_peak_live_bytes_after: int = 0
    per_node_drop_order: tuple[str, ...] = ()
    nested_drop_order_valid: bool = True
    partial_reuse_safety_flag: bool = True
    node_compute_count: int = 0
    node_hit_count: int = 0
    total_compute_calls: int = 0
    total_store_hits: int = 0
    shared_node_hit_rate: float = 0.0
    compute_time_ms: float = 0.0
    store_write_time_ms: float = 0.0
    store_hit_time_ms: float = 0.0
    native_heavy_node_count: int = 0
    native_heavy_forbidden_count: int = 0
    native_heavy_observable_only_count: int = 0
    native_heavy_candidate_future_count: int = 0
    native_compute_time_ms: float = 0.0
    native_path_normalization_time_ms: float = 0.0
    native_storage_residency_bytes: int = 0
    native_node_store_read_count: int = 0
    native_logical_consumer_count: int = 0
    native_effective_use_count: int = 0
    native_fallback_eval_count: int = 0
    native_rewrite_applied_count: int = 0
    native_helper_usage_patterns: tuple[str, ...] = ()
    helper_column_count: int = 0
    helper_releasable_count: int = 0
    helper_blocked_count: int = 0
    helper_peak_live_bytes: int = 0
    helper_potential_savings: int = 0
    helper_blocker_reasons: tuple[str, ...] = ()
    helper_dropped_count: int = 0
    helper_drop_miss_count: int = 0
    helper_peak_live_bytes_before_drop: int = 0
    helper_peak_live_bytes_after_drop: int = 0
    helper_frame_width_before_drop: int = 0
    helper_frame_width_after_drop: int = 0
    helper_drop_delay_steps_avg: float = 0.0
    helper_drop_delay_steps_max: int = 0
    helper_lifecycle_effective: bool = False
    nested_helper_dropped_count: int = 0
    nested_helper_drop_missed_count: int = 0
    nested_helper_peak_live_bytes_before_drop: int = 0
    nested_helper_peak_live_bytes_after_drop: int = 0
    nested_helper_frame_width_before_drop: int = 0
    nested_helper_frame_width_after_drop: int = 0
    nested_helper_lifecycle_effective: bool = False
    recomputation_guardrail_candidate_count: int = 0
    recomputation_guardrail_blocked_count: int = 0
    recomputation_guardrail_allowed_count: int = 0
    recomputation_expansion_estimate: int = 0
    recomputation_expansion_actual_delta: int = 0


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
    lifecycle_mode: str = "off"
    helper_lifecycle_mode: str = "off"
    dropped_stage_count: int = 0
    total_recomputed_stage_count: int = 0
    total_avoided_recomputation_count: int = 0
    total_planned_reusable_stage_count: int = 0
    late_alive_stage_count: int = 0
    peak_output_col_count: int = 0
    peak_stage_col_count: int = 0
    alive_output_at_batch_end_count: int = 0
    late_alive_output_count: int = 0
    native_output_buffer_count: int = 0
    peak_native_buffer_bytes_estimate: int = 0
    native_buffer_alive_before_attach: int = 0
    native_buffer_alive_after_attach: int = 0
    native_buffer_release_lag: int = 0
    retained_for_reuse_stage_count: int = 0
    retained_for_output_stage_count: int = 0
    parallel_enabled: bool = False
    parallel_worker_count: int = 1
    parallel_buffer_peak_estimate: int = 0
    serial_vs_parallel_rss_delta: float | None = None
    ast_node_count: int = 0
    dag_node_count: int = 0
    deduplicated_node_count: int = 0
    shared_node_count: int = 0
    materialized_node_count: int = 0
    expensive_node_count: int = 0
    result_store_peak_entry_count: int = 0
    finalize_time_ms: float = 0.0
    node_store_compute_calls: int = 0
    estimated_unshared_compute_calls: int = 0
    compiled_output_heavy_occurrence_count: int = 0
    compiled_fallback_eval_count: int = 0
    node_store_read_count: int = 0
    reuse_consumer_count: int = 0
    node_store_compute_time_ms: float = 0.0
    compiled_output_eval_time_ms: float = 0.0
    restore_assemble_time_ms: float = 0.0
    restore_assemble_step: int = 0
    append_step: int = 0
    finalize_step: int = 0
    batch_end_step: int = 0
    lifecycle_candidate_count: int = 0
    lifecycle_releasable_node_count: int = 0
    lifecycle_peak_live_node_count: int = 0
    lifecycle_peak_live_bytes_est: int = 0
    avg_release_lag_steps: float = 0.0
    max_release_lag_steps: int = 0
    avg_structural_release_lag_steps: float = 0.0
    max_structural_release_lag_steps: int = 0
    avg_finalize_retention_lag_steps: float = 0.0
    max_finalize_retention_lag_steps: int = 0
    potential_live_bytes_step_savings: int = 0
    l2_first_wave_candidate_count: int = 0
    dropped_node_count: int = 0
    drop_hit_count: int = 0
    drop_miss_count: int = 0
    peak_live_node_count_after_drop: int = 0
    peak_live_bytes_est_before_drop: int = 0
    peak_live_bytes_est_after_drop: int = 0
    drop_delay_steps_avg: float = 0.0
    drop_delay_steps_max: int = 0
    lifecycle_effective: bool = False
    multi_node_overlap_peak: int = 0
    multi_node_peak_live_bytes_before: int = 0
    multi_node_peak_live_bytes_after: int = 0
    per_node_drop_order: list[str] | None = None
    nested_drop_order_valid: bool = True
    partial_reuse_safety_flag: bool = True
    top_releasable_nodes_by_bytes_step_savings: list[dict[str, object]] | None = None
    node_compute_count: int = 0
    node_hit_count: int = 0
    total_compute_calls: int = 0
    total_store_hits: int = 0
    shared_node_hit_rate: float = 0.0
    compute_time_ms: float = 0.0
    store_write_time_ms: float = 0.0
    store_hit_time_ms: float = 0.0
    native_heavy_node_count: int = 0
    native_heavy_forbidden_count: int = 0
    native_heavy_observable_only_count: int = 0
    native_heavy_candidate_future_count: int = 0
    native_compute_time_ms: float = 0.0
    native_path_normalization_time_ms: float = 0.0
    native_storage_residency_bytes: int = 0
    native_node_store_read_count: int = 0
    native_logical_consumer_count: int = 0
    native_effective_use_count: int = 0
    native_fallback_eval_count: int = 0
    native_rewrite_applied_count: int = 0
    native_helper_usage_patterns: list[str] | None = None
    helper_column_count: int = 0
    helper_releasable_count: int = 0
    helper_blocked_count: int = 0
    helper_peak_live_bytes: int = 0
    helper_potential_savings: int = 0
    helper_blocker_reasons: list[str] | None = None
    helper_dropped_count: int = 0
    helper_drop_miss_count: int = 0
    helper_peak_live_bytes_before_drop: int = 0
    helper_peak_live_bytes_after_drop: int = 0
    helper_frame_width_before_drop: int = 0
    helper_frame_width_after_drop: int = 0
    helper_drop_delay_steps_avg: float = 0.0
    helper_drop_delay_steps_max: int = 0
    helper_lifecycle_effective: bool = False
    nested_helper_dropped_count: int = 0
    nested_helper_drop_missed_count: int = 0
    nested_helper_peak_live_bytes_before_drop: int = 0
    nested_helper_peak_live_bytes_after_drop: int = 0
    nested_helper_frame_width_before_drop: int = 0
    nested_helper_frame_width_after_drop: int = 0
    nested_helper_lifecycle_effective: bool = False
    recomputation_guardrail_candidate_count: int = 0
    recomputation_guardrail_blocked_count: int = 0
    recomputation_guardrail_allowed_count: int = 0
    recomputation_expansion_estimate: int = 0
    recomputation_expansion_actual_delta: int = 0
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
    latest_output_details_jsonl: Path
    latest_native_buffer_details_jsonl: Path
    latest_memory_events_jsonl: Path
    latest_node_execution_details_jsonl: Path
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
        self.outputs: list[OutputDetail] = []
        self.native_buffers: list[NativeBufferDetail] = []
        self.node_executions: list[NodeExecutionDetail] = []
        self.events: list[StageEvent] = []
        self.memory_events: list[MemoryEvent] = []
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

    def add_output(self, output: OutputDetail) -> None:
        self.outputs.append(output)

    def add_native_buffer(self, native_buffer: NativeBufferDetail) -> None:
        self.native_buffers.append(native_buffer)

    def add_node_execution(self, detail: NodeExecutionDetail) -> None:
        self.node_executions.append(detail)

    def add_memory_event(self, event: MemoryEvent) -> None:
        self.memory_events.append(event)
        self.peak_rss_mb = max(self.peak_rss_mb, event.rss_mb)

    def add_batch(self, batch: BatchDetail) -> None:
        self.batches.append(batch)
        self.peak_rss_mb = max(self.peak_rss_mb, batch.peak_rss_mb)

    def add_positional_phase(self, detail: PositionalPhaseDetail) -> None:
        self.positional_phases.append(detail)
        self.peak_rss_mb = max(self.peak_rss_mb, detail.peak_rss_mb)

    def finish(self, *, result_column_count: int) -> RunProfileSummary:
        total_time_sec = time.perf_counter() - self._start
        top_releasable_nodes = [
            {
                "node_id": item.node_id,
                "batch_id": item.batch_id,
                "node_lifecycle_class": item.node_lifecycle_class,
                "materialization_reason": item.materialization_reason,
                "materialization_eligibility": item.materialization_eligibility,
                "bytes_estimate": item.bytes_estimate,
                "structural_release_lag_steps": item.structural_release_lag_steps,
                "potential_live_bytes_step_savings": item.potential_live_bytes_step_savings,
                "planner_last_use_step": item.planner_last_use_step,
                "batch_end_step": item.batch_end_step,
            }
            for item in sorted(
                self.node_executions,
                key=lambda detail: detail.potential_live_bytes_step_savings,
                reverse=True,
            )
            if item.potential_live_bytes_step_savings > 0
        ][:10]
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
            lifecycle_mode=(
                self.batches[0].lifecycle_mode
                if self.batches
                and len({item.lifecycle_mode for item in self.batches}) == 1
                else "mixed"
            ),
            helper_lifecycle_mode=(
                self.batches[0].helper_lifecycle_mode
                if self.batches
                and len({item.helper_lifecycle_mode for item in self.batches}) == 1
                else "mixed"
            ),
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
            peak_output_col_count=max((item.peak_output_col_count for item in self.batches), default=0),
            peak_stage_col_count=max((item.peak_stage_col_count for item in self.batches), default=0),
            alive_output_at_batch_end_count=sum(
                item.alive_output_at_batch_end_count for item in self.batches
            ),
            late_alive_output_count=sum(item.late_alive_output_count for item in self.batches),
            native_output_buffer_count=sum(item.native_output_buffer_count for item in self.batches),
            peak_native_buffer_bytes_estimate=max(
                (item.peak_native_buffer_bytes_estimate for item in self.batches),
                default=0,
            ),
            native_buffer_alive_before_attach=sum(
                item.native_buffer_alive_before_attach for item in self.batches
            ),
            native_buffer_alive_after_attach=sum(
                item.native_buffer_alive_after_attach for item in self.batches
            ),
            native_buffer_release_lag=max(
                (item.native_buffer_release_lag for item in self.batches),
                default=0,
            ),
            retained_for_reuse_stage_count=sum(
                item.retained_for_reuse_stage_count for item in self.batches
            ),
            retained_for_output_stage_count=sum(
                item.retained_for_output_stage_count for item in self.batches
            ),
            parallel_enabled=any(item.parallel_enabled for item in self.batches),
            parallel_worker_count=max((item.parallel_worker_count for item in self.batches), default=1),
            parallel_buffer_peak_estimate=max(
                (item.parallel_buffer_peak_estimate for item in self.batches),
                default=0,
            ),
            ast_node_count=sum(item.ast_node_count for item in self.batches),
            dag_node_count=sum(item.dag_node_count for item in self.batches),
            deduplicated_node_count=sum(item.deduplicated_node_count for item in self.batches),
            shared_node_count=sum(item.shared_node_count for item in self.batches),
            materialized_node_count=sum(item.materialized_node_count for item in self.batches),
            expensive_node_count=sum(item.expensive_node_count for item in self.batches),
            result_store_peak_entry_count=max(
                (item.result_store_peak_entry_count for item in self.batches),
                default=0,
            ),
            finalize_time_ms=sum(item.finalize_time_ms for item in self.batches),
            node_store_compute_calls=sum(item.node_store_compute_calls for item in self.batches),
            estimated_unshared_compute_calls=sum(
                item.estimated_unshared_compute_calls for item in self.batches
            ),
            compiled_output_heavy_occurrence_count=sum(
                item.compiled_output_heavy_occurrence_count for item in self.batches
            ),
            compiled_fallback_eval_count=sum(
                item.compiled_fallback_eval_count for item in self.batches
            ),
            node_store_read_count=sum(item.node_store_read_count for item in self.batches),
            reuse_consumer_count=sum(item.reuse_consumer_count for item in self.batches),
            node_store_compute_time_ms=sum(
                item.node_store_compute_time_ms for item in self.batches
            ),
            compiled_output_eval_time_ms=sum(
                item.compiled_output_eval_time_ms for item in self.batches
            ),
            restore_assemble_time_ms=sum(item.restore_assemble_time_ms for item in self.batches),
            restore_assemble_step=max(
                (item.restore_assemble_step for item in self.batches),
                default=0,
            ),
            append_step=max((item.append_step for item in self.batches), default=0),
            finalize_step=max((item.finalize_step for item in self.batches), default=0),
            batch_end_step=max((item.batch_end_step for item in self.batches), default=0),
            lifecycle_candidate_count=sum(item.lifecycle_candidate_count for item in self.batches),
            lifecycle_releasable_node_count=sum(
                item.lifecycle_releasable_node_count for item in self.batches
            ),
            lifecycle_peak_live_node_count=max(
                (item.lifecycle_peak_live_node_count for item in self.batches),
                default=0,
            ),
            lifecycle_peak_live_bytes_est=max(
                (item.lifecycle_peak_live_bytes_est for item in self.batches),
                default=0,
            ),
            avg_release_lag_steps=(
                sum(
                    item.avg_release_lag_steps * item.lifecycle_releasable_node_count
                    for item in self.batches
                )
                / sum(item.lifecycle_releasable_node_count for item in self.batches)
                if sum(item.lifecycle_releasable_node_count for item in self.batches)
                else 0.0
            ),
            max_release_lag_steps=max(
                (item.max_release_lag_steps for item in self.batches),
                default=0,
            ),
            avg_structural_release_lag_steps=(
                sum(
                    item.avg_structural_release_lag_steps
                    * item.lifecycle_releasable_node_count
                    for item in self.batches
                )
                / sum(item.lifecycle_releasable_node_count for item in self.batches)
                if sum(item.lifecycle_releasable_node_count for item in self.batches)
                else 0.0
            ),
            max_structural_release_lag_steps=max(
                (item.max_structural_release_lag_steps for item in self.batches),
                default=0,
            ),
            avg_finalize_retention_lag_steps=(
                sum(
                    item.avg_finalize_retention_lag_steps
                    * item.lifecycle_releasable_node_count
                    for item in self.batches
                )
                / sum(item.lifecycle_releasable_node_count for item in self.batches)
                if sum(item.lifecycle_releasable_node_count for item in self.batches)
                else 0.0
            ),
            max_finalize_retention_lag_steps=max(
                (item.max_finalize_retention_lag_steps for item in self.batches),
                default=0,
            ),
            potential_live_bytes_step_savings=sum(
                item.potential_live_bytes_step_savings for item in self.batches
            ),
            l2_first_wave_candidate_count=sum(
                item.l2_first_wave_candidate_count for item in self.batches
            ),
            dropped_node_count=sum(item.dropped_node_count for item in self.batches),
            drop_hit_count=sum(item.drop_hit_count for item in self.batches),
            drop_miss_count=sum(item.drop_miss_count for item in self.batches),
            peak_live_node_count_after_drop=max(
                (item.peak_live_node_count_after_drop for item in self.batches),
                default=0,
            ),
            peak_live_bytes_est_before_drop=max(
                (item.peak_live_bytes_est_before_drop for item in self.batches),
                default=0,
            ),
            peak_live_bytes_est_after_drop=max(
                (item.peak_live_bytes_est_after_drop for item in self.batches),
                default=0,
            ),
            drop_delay_steps_avg=(
                sum(item.drop_delay_steps_avg * item.drop_hit_count for item in self.batches)
                / sum(item.drop_hit_count for item in self.batches)
                if sum(item.drop_hit_count for item in self.batches)
                else 0.0
            ),
            drop_delay_steps_max=max(
                (item.drop_delay_steps_max for item in self.batches),
                default=0,
            ),
            lifecycle_effective=any(item.lifecycle_effective for item in self.batches),
            multi_node_overlap_peak=max(
                (item.multi_node_overlap_peak for item in self.batches),
                default=0,
            ),
            multi_node_peak_live_bytes_before=max(
                (item.multi_node_peak_live_bytes_before for item in self.batches),
                default=0,
            ),
            multi_node_peak_live_bytes_after=max(
                (item.multi_node_peak_live_bytes_after for item in self.batches),
                default=0,
            ),
            per_node_drop_order=[
                node_id
                for item in self.batches
                for node_id in item.per_node_drop_order
            ],
            nested_drop_order_valid=all(
                item.nested_drop_order_valid for item in self.batches
            ),
            partial_reuse_safety_flag=all(
                item.partial_reuse_safety_flag for item in self.batches
            ),
            top_releasable_nodes_by_bytes_step_savings=top_releasable_nodes,
            node_compute_count=sum(item.node_compute_count for item in self.batches),
            node_hit_count=sum(item.node_hit_count for item in self.batches),
            total_compute_calls=sum(item.total_compute_calls for item in self.batches),
            total_store_hits=sum(item.total_store_hits for item in self.batches),
            shared_node_hit_rate=(
                sum(item.total_store_hits for item in self.batches)
                / (
                    sum(item.total_store_hits for item in self.batches)
                    + sum(item.total_compute_calls for item in self.batches)
                )
                if (
                    sum(item.total_store_hits for item in self.batches)
                    + sum(item.total_compute_calls for item in self.batches)
                )
                else 0.0
            ),
            compute_time_ms=sum(item.compute_time_ms for item in self.batches),
            store_write_time_ms=sum(item.store_write_time_ms for item in self.batches),
            store_hit_time_ms=sum(item.store_hit_time_ms for item in self.batches),
            native_heavy_node_count=sum(item.native_heavy_node_count for item in self.batches),
            native_heavy_forbidden_count=sum(
                item.native_heavy_forbidden_count for item in self.batches
            ),
            native_heavy_observable_only_count=sum(
                item.native_heavy_observable_only_count for item in self.batches
            ),
            native_heavy_candidate_future_count=sum(
                item.native_heavy_candidate_future_count for item in self.batches
            ),
            native_compute_time_ms=sum(item.native_compute_time_ms for item in self.batches),
            native_path_normalization_time_ms=sum(
                item.native_path_normalization_time_ms for item in self.batches
            ),
            native_storage_residency_bytes=max(
                (item.native_storage_residency_bytes for item in self.batches),
                default=0,
            ),
            native_node_store_read_count=sum(
                item.native_node_store_read_count for item in self.batches
            ),
            native_logical_consumer_count=sum(
                item.native_logical_consumer_count for item in self.batches
            ),
            native_effective_use_count=sum(item.native_effective_use_count for item in self.batches),
            native_fallback_eval_count=sum(item.native_fallback_eval_count for item in self.batches),
            native_rewrite_applied_count=sum(
                item.native_rewrite_applied_count for item in self.batches
            ),
            native_helper_usage_patterns=sorted(
                {
                    pattern
                    for item in self.batches
                    for pattern in item.native_helper_usage_patterns
                    if pattern
                }
            ),
            helper_column_count=sum(item.helper_column_count for item in self.batches),
            helper_releasable_count=sum(item.helper_releasable_count for item in self.batches),
            helper_blocked_count=sum(item.helper_blocked_count for item in self.batches),
            helper_peak_live_bytes=max(
                (item.helper_peak_live_bytes for item in self.batches),
                default=0,
            ),
            helper_potential_savings=sum(item.helper_potential_savings for item in self.batches),
            helper_blocker_reasons=sorted(
                {
                    reason
                    for item in self.batches
                    for reason in item.helper_blocker_reasons
                    if reason
                }
            ),
            helper_dropped_count=sum(item.helper_dropped_count for item in self.batches),
            helper_drop_miss_count=sum(item.helper_drop_miss_count for item in self.batches),
            helper_peak_live_bytes_before_drop=max(
                (item.helper_peak_live_bytes_before_drop for item in self.batches),
                default=0,
            ),
            helper_peak_live_bytes_after_drop=max(
                (item.helper_peak_live_bytes_after_drop for item in self.batches),
                default=0,
            ),
            helper_frame_width_before_drop=max(
                (item.helper_frame_width_before_drop for item in self.batches),
                default=0,
            ),
            helper_frame_width_after_drop=max(
                (item.helper_frame_width_after_drop for item in self.batches),
                default=0,
            ),
            helper_drop_delay_steps_avg=(
                sum(item.helper_drop_delay_steps_avg * item.helper_dropped_count for item in self.batches)
                / sum(item.helper_dropped_count for item in self.batches)
                if sum(item.helper_dropped_count for item in self.batches)
                else 0.0
            ),
            helper_drop_delay_steps_max=max(
                (item.helper_drop_delay_steps_max for item in self.batches),
                default=0,
            ),
            helper_lifecycle_effective=any(
                item.helper_lifecycle_effective for item in self.batches
            ),
            nested_helper_dropped_count=sum(
                item.nested_helper_dropped_count for item in self.batches
            ),
            nested_helper_drop_missed_count=sum(
                item.nested_helper_drop_missed_count for item in self.batches
            ),
            nested_helper_peak_live_bytes_before_drop=max(
                (item.nested_helper_peak_live_bytes_before_drop for item in self.batches),
                default=0,
            ),
            nested_helper_peak_live_bytes_after_drop=max(
                (item.nested_helper_peak_live_bytes_after_drop for item in self.batches),
                default=0,
            ),
            nested_helper_frame_width_before_drop=max(
                (item.nested_helper_frame_width_before_drop for item in self.batches),
                default=0,
            ),
            nested_helper_frame_width_after_drop=max(
                (item.nested_helper_frame_width_after_drop for item in self.batches),
                default=0,
            ),
            nested_helper_lifecycle_effective=any(
                item.nested_helper_lifecycle_effective for item in self.batches
            ),
            recomputation_guardrail_candidate_count=sum(
                item.recomputation_guardrail_candidate_count for item in self.batches
            ),
            recomputation_guardrail_blocked_count=sum(
                item.recomputation_guardrail_blocked_count for item in self.batches
            ),
            recomputation_guardrail_allowed_count=sum(
                item.recomputation_guardrail_allowed_count for item in self.batches
            ),
            recomputation_expansion_estimate=sum(
                item.recomputation_expansion_estimate for item in self.batches
            ),
            recomputation_expansion_actual_delta=sum(
                item.recomputation_expansion_actual_delta for item in self.batches
            ),
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
        outputs = target_dir / "latest_output_details.jsonl"
        native_buffers = target_dir / "latest_native_buffer_details.jsonl"
        memory_events = target_dir / "latest_memory_events.jsonl"
        node_executions = target_dir / "latest_node_execution_details.jsonl"
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
        self._write_jsonl(outputs, self.outputs)
        self._write_jsonl(native_buffers, self.native_buffers)
        self._write_jsonl(memory_events, self.memory_events)
        self._write_jsonl(node_executions, self.node_executions)
        report.write_text(self.render_markdown_report(), encoding="utf-8")

        return ProfileArtifacts(
            latest_run_json=latest_run,
            history_csv=history,
            latest_batch_details_jsonl=batches,
            latest_stage_details_jsonl=stages,
            latest_stage_events_jsonl=events,
            latest_positional_phase_details_jsonl=positional_phases,
            latest_output_details_jsonl=outputs,
            latest_native_buffer_details_jsonl=native_buffers,
            latest_memory_events_jsonl=memory_events,
            latest_node_execution_details_jsonl=node_executions,
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
            "| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for batch in self.batches:
            lines.append(
                f"| `{batch.batch_id}` | `{batch.route}` | {batch.expression_count} | "
                f"{batch.stage_count} | {batch.dropped_stage_count} | "
                f"{batch.peak_frame_col_count} | {batch.peak_stage_col_count} | "
                f"{batch.peak_output_col_count} | {batch.final_frame_col_count} | "
                f"{batch.alive_stage_at_batch_end_count} | "
                f"{batch.alive_output_at_batch_end_count} | "
                f"{batch.native_output_buffer_peak_bytes_estimate} | {batch.peak_rss_mb:.2f} |"
            )

        lines.extend(
            [
                "",
                "## DAG / CSE",
                "",
                "| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for batch in self.batches:
            lines.append(
                f"| `{batch.batch_id}` | {batch.ast_node_count} | {batch.dag_node_count} | "
                f"{batch.deduplicated_node_count} | {batch.shared_node_count} | "
                f"{batch.materialized_node_count} | {batch.expensive_node_count} | "
                f"{batch.estimated_unshared_compute_calls} | {batch.total_compute_calls} | "
                f"{batch.node_store_compute_calls} | "
                f"{batch.compiled_output_heavy_occurrence_count} | "
                f"{batch.node_store_read_count} | {batch.reuse_consumer_count} | "
                f"{batch.shared_node_hit_rate:.3f} | "
                f"{batch.node_store_compute_time_ms:.3f} | "
                f"{batch.compiled_output_eval_time_ms:.3f} | "
                f"{batch.restore_assemble_time_ms:.3f} | {batch.append_time_ms:.3f} | "
                f"{batch.finalize_time_ms:.3f} |"
            )

        lines.extend(
            [
                "",
                "## L1 Lifecycle Observability",
                "",
                "| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for batch in self.batches:
            lines.append(
                f"| `{batch.batch_id}` | `{batch.lifecycle_mode}` | "
                f"{batch.lifecycle_effective} | "
                f"{batch.lifecycle_candidate_count} | "
                f"{batch.lifecycle_releasable_node_count} | "
                f"{batch.lifecycle_peak_live_node_count} | "
                f"{batch.peak_live_bytes_est_before_drop} | "
                f"{batch.peak_live_bytes_est_after_drop} | "
                f"{batch.dropped_node_count} | "
                f"{batch.drop_miss_count} | "
                f"`{','.join(batch.per_node_drop_order)}` | "
                f"{batch.nested_drop_order_valid} | "
                f"{batch.partial_reuse_safety_flag} | "
                f"{batch.batch_end_step} | "
                f"{batch.avg_structural_release_lag_steps:.3f} | "
                f"{batch.max_structural_release_lag_steps} | "
                f"{batch.avg_finalize_retention_lag_steps:.3f} | "
                f"{batch.max_finalize_retention_lag_steps} | "
                f"{batch.potential_live_bytes_step_savings} | "
                f"{batch.l2_first_wave_candidate_count} |"
            )

        if any(batch.native_heavy_node_count for batch in self.batches):
            lines.extend(
                [
                    "",
                    "## L3A Native-Heavy Lifecycle Observability",
                    "",
                    "| batch | native nodes | forbidden | observable only | candidate future | native compute ms | path normalization ms | storage bytes | store reads | logical consumers | effective uses | fallback evals | rewrites | helper patterns |",
                    "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
                ]
            )
            for batch in self.batches:
                if batch.native_heavy_node_count == 0:
                    continue
                lines.append(
                    f"| `{batch.batch_id}` | {batch.native_heavy_node_count} | "
                    f"{batch.native_heavy_forbidden_count} | "
                    f"{batch.native_heavy_observable_only_count} | "
                    f"{batch.native_heavy_candidate_future_count} | "
                    f"{batch.native_compute_time_ms:.3f} | "
                    f"{batch.native_path_normalization_time_ms:.3f} | "
                    f"{batch.native_storage_residency_bytes} | "
                    f"{batch.native_node_store_read_count} | "
                    f"{batch.native_logical_consumer_count} | "
                    f"{batch.native_effective_use_count} | "
                    f"{batch.native_fallback_eval_count} | "
                    f"{batch.native_rewrite_applied_count} | "
                    f"`{','.join(batch.native_helper_usage_patterns)}` |"
                )

        if any(batch.helper_column_count for batch in self.batches):
            lines.extend(
                [
                    "",
                    "## L3B Helper Column Lifecycle Observability",
                    "",
                    "| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |",
                    "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
                ]
            )
            for batch in self.batches:
                if batch.helper_column_count == 0:
                    continue
                lines.append(
                    f"| `{batch.batch_id}` | `{batch.helper_lifecycle_mode}` | "
                    f"{batch.helper_lifecycle_effective} | "
                    f"{batch.helper_column_count} | "
                    f"{batch.helper_releasable_count} | "
                    f"{batch.helper_blocked_count} | "
                    f"{batch.helper_peak_live_bytes} | "
                    f"{batch.helper_peak_live_bytes_before_drop} | "
                    f"{batch.helper_peak_live_bytes_after_drop} | "
                    f"{batch.helper_dropped_count} | "
                    f"{batch.helper_drop_miss_count} | "
                    f"{batch.helper_frame_width_before_drop} | "
                    f"{batch.helper_frame_width_after_drop} | "
                    f"{batch.helper_drop_delay_steps_avg:.3f} | "
                    f"{batch.helper_potential_savings} | "
                    f"`{','.join(batch.helper_blocker_reasons)}` |"
                )

        top_releasable = (
            self.summary.top_releasable_nodes_by_bytes_step_savings
            if self.summary is not None
            else []
        )
        if top_releasable:
            lines.extend(
                [
                    "",
                    "## Top Releasable Nodes By Bytes-Step Savings",
                    "",
                    "| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |",
                    "| --- | --- | --- | --- | --- | ---: | ---: | ---: |",
                ]
            )
            for item in top_releasable:
                lines.append(
                    f"| `{item['node_id']}` | `{item['batch_id']}` | "
                    f"`{item['node_lifecycle_class']}` | "
                    f"`{item['materialization_reason']}` | "
                    f"`{item['materialization_eligibility']}` | "
                    f"{item['bytes_estimate']} | "
                    f"{item['structural_release_lag_steps']} | "
                    f"{item['potential_live_bytes_step_savings']} |"
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

        lines.extend(
            [
                "",
                "## Output Retention",
                "",
                "| output | source | created | attached | last required | late alive | working-frame attach |",
                "| --- | --- | ---: | ---: | ---: | --- | --- |",
            ]
        )
        for output in self.outputs:
            lines.append(
                f"| `{output.output_name}` | `{output.source_column_name}` | "
                f"{output.created_order_index} | {output.attached_order_index} | "
                f"{output.last_required_order_index} | {output.is_late_alive_output} | "
                f"{output.attached_to_working_frame} |"
            )

        if self.native_buffers:
            lines.extend(
                [
                    "",
                    "## Native Buffers",
                    "",
                    "| buffer | output | bytes | created | attached | released | release lag | parallel | workers |",
                    "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
                ]
            )
            for buffer in self.native_buffers:
                lines.append(
                    f"| `{buffer.buffer_id}` | `{buffer.related_output_name}` | "
                    f"{buffer.bytes_estimate} | {buffer.created_order_index} | "
                    f"{buffer.attached_order_index} | {buffer.released_order_index} | "
                    f"{buffer.release_lag_steps} | {buffer.native_parallel_used} | "
                    f"{buffer.parallel_worker_count} |"
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
