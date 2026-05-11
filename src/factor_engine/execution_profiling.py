from __future__ import annotations

from dataclasses import fields
from typing import Any

from factor_engine.profiling import (
    MemoryEvent,
    NativeBufferDetail,
    OutputDetail,
    PositionalPhaseDetail,
)


PROFILING_OUTPUT_FILES: tuple[str, ...] = (
    "latest_run.json",
    "history.csv",
    "latest_stage_details.jsonl",
    "latest_memory_events.jsonl",
    "latest_node_execution_details.jsonl",
    "latest_output_details.jsonl",
    "latest_native_buffer_details.jsonl",
    "latest_positional_phase_details.jsonl",
)

MEMORY_EVENT_FIELDS: tuple[str, ...] = tuple(field.name for field in fields(MemoryEvent))
OUTPUT_DETAIL_FIELDS: tuple[str, ...] = tuple(field.name for field in fields(OutputDetail))
NATIVE_BUFFER_DETAIL_FIELDS: tuple[str, ...] = tuple(
    field.name for field in fields(NativeBufferDetail)
)
POSITIONAL_PHASE_DETAIL_FIELDS: tuple[str, ...] = tuple(
    field.name for field in fields(PositionalPhaseDetail)
)


def build_memory_event(
    *,
    event_type: str,
    batch_id: str,
    order_index: int,
    frame_col_count: int,
    rss_mb: float,
    output_name: str | None = None,
    buffer_id: str | None = None,
    related_output_name: str | None = None,
    bytes_estimate: int | None = None,
    output_col_count: int | None = None,
    stage_col_count: int | None = None,
    native_buffer_alive_bytes_estimate: int | None = None,
    native_parallel_used: bool | None = None,
    parallel_worker_count: int | None = None,
) -> MemoryEvent:
    return MemoryEvent(
        event_type=event_type,
        batch_id=batch_id,
        order_index=order_index,
        frame_col_count=frame_col_count,
        rss_mb=rss_mb,
        output_name=output_name,
        buffer_id=buffer_id,
        related_output_name=related_output_name,
        bytes_estimate=bytes_estimate,
        output_col_count=output_col_count,
        stage_col_count=stage_col_count,
        native_buffer_alive_bytes_estimate=native_buffer_alive_bytes_estimate,
        native_parallel_used=native_parallel_used,
        parallel_worker_count=parallel_worker_count,
    )


def build_output_detail(
    *,
    record: Any,
    batch_id: str,
    alive_at_batch_end: bool,
    is_late_alive_output: bool,
) -> OutputDetail:
    return OutputDetail(
        output_name=record.output_name,
        batch_id=batch_id,
        created_order_index=record.created_order_index,
        attached_order_index=record.attached_order_index,
        last_required_order_index=record.last_required_order_index,
        alive_at_batch_end=alive_at_batch_end,
        is_late_alive_output=is_late_alive_output,
        frame_col_count_at_attach=record.frame_col_count_at_attach,
        rss_at_attach_mb=record.rss_at_attach_mb,
        source_column_name=record.source_column_name,
        attached_to_working_frame=record.attached_to_working_frame,
    )


def build_native_buffer_detail(
    *,
    record: Any,
    batch_id: str,
    alive_after_attach: bool,
    release_lag_steps: int | None,
) -> NativeBufferDetail:
    return NativeBufferDetail(
        buffer_id=record.buffer_id,
        batch_id=batch_id,
        related_output_name=record.related_output_name,
        created_order_index=record.created_order_index,
        attached_order_index=record.attached_order_index,
        released_order_index=record.released_order_index,
        bytes_estimate=record.bytes_estimate,
        alive_before_attach=record.alive_before_attach,
        alive_after_attach=alive_after_attach,
        release_lag_steps=release_lag_steps,
        native_parallel_used=record.native_parallel_used,
        parallel_worker_count=record.parallel_worker_count,
    )


def build_positional_phase_detail(
    *,
    run_id: str,
    batch_id: str,
    expression: str,
    output_name: str,
    function_name: str,
    rows: int,
    groups: int,
    window: int,
    child_stage_kind: str,
    prepare_sort_time_ms: float,
    child_expr_time_ms: float,
    positional_total_time_ms: float,
    positional_to_list_time_ms: float,
    positional_group_scan_time_ms: float,
    result_attach_time_ms: float,
    restore_time_ms: float,
    python_kernel_used: bool,
    native_kernel_used: bool,
    native_low_copy_bridge_used: bool,
    python_object_bridge_used: bool,
    native_parallel_used: bool,
    group_parallelism_level: int,
    group_count: int,
    avg_group_size: float,
    max_group_size: int,
    output_non_null_count: int,
    rss_before_mb: float,
    rss_after_mb: float,
    peak_rss_mb: float,
) -> PositionalPhaseDetail:
    return PositionalPhaseDetail(
        run_id=run_id,
        batch_id=batch_id,
        expression=expression,
        output_name=output_name,
        function_name=function_name,
        rows=rows,
        groups=groups,
        window=window,
        child_stage_kind=child_stage_kind,
        prepare_sort_time_ms=prepare_sort_time_ms,
        child_expr_time_ms=child_expr_time_ms,
        positional_total_time_ms=positional_total_time_ms,
        positional_to_list_time_ms=positional_to_list_time_ms,
        positional_group_scan_time_ms=positional_group_scan_time_ms,
        result_attach_time_ms=result_attach_time_ms,
        restore_time_ms=restore_time_ms,
        python_kernel_used=python_kernel_used,
        native_kernel_used=native_kernel_used,
        native_low_copy_bridge_used=native_low_copy_bridge_used,
        python_object_bridge_used=python_object_bridge_used,
        native_parallel_used=native_parallel_used,
        group_parallelism_level=group_parallelism_level,
        group_count=group_count,
        avg_group_size=avg_group_size,
        max_group_size=max_group_size,
        output_non_null_count=output_non_null_count,
        rss_before_mb=rss_before_mb,
        rss_after_mb=rss_after_mb,
        peak_rss_mb=peak_rss_mb,
    )
