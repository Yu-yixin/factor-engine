from __future__ import annotations

from dataclasses import asdict
from types import SimpleNamespace

from factor_engine.execution_profiling import (
    MEMORY_EVENT_FIELDS,
    NATIVE_BUFFER_DETAIL_FIELDS,
    OUTPUT_DETAIL_FIELDS,
    POSITIONAL_PHASE_DETAIL_FIELDS,
    PROFILING_OUTPUT_FILES,
    build_memory_event,
    build_native_buffer_detail,
    build_output_detail,
    build_positional_phase_detail,
)


def test_profiling_output_file_contract_lists_current_outputs():
    assert PROFILING_OUTPUT_FILES == (
        "latest_run.json",
        "history.csv",
        "latest_stage_details.jsonl",
        "latest_memory_events.jsonl",
        "latest_node_execution_details.jsonl",
        "latest_output_details.jsonl",
        "latest_native_buffer_details.jsonl",
        "latest_positional_phase_details.jsonl",
    )


def test_memory_event_builder_preserves_schema_and_defaults():
    event = build_memory_event(
        event_type="output_attach",
        batch_id="batch-1",
        order_index=7,
        frame_col_count=11,
        rss_mb=12.5,
    )

    assert tuple(asdict(event)) == MEMORY_EVENT_FIELDS
    assert event.output_name is None
    assert event.native_parallel_used is None
    assert event.parallel_worker_count is None


def test_output_detail_builder_preserves_schema():
    record = SimpleNamespace(
        output_name="alpha",
        created_order_index=1,
        attached_order_index=3,
        last_required_order_index=5,
        frame_col_count_at_attach=8,
        rss_at_attach_mb=42.0,
        source_column_name="__stage_alpha",
        attached_to_working_frame=True,
    )

    detail = build_output_detail(
        record=record,
        batch_id="batch-1",
        alive_at_batch_end=True,
        is_late_alive_output=True,
    )

    assert tuple(asdict(detail)) == OUTPUT_DETAIL_FIELDS
    assert detail.output_name == "alpha"
    assert detail.source_column_name == "__stage_alpha"
    assert detail.is_late_alive_output is True


def test_native_buffer_detail_builder_preserves_schema():
    record = SimpleNamespace(
        buffer_id="native-1",
        related_output_name="alpha",
        created_order_index=2,
        attached_order_index=4,
        released_order_index=6,
        bytes_estimate=1024,
        alive_before_attach=True,
        native_parallel_used=True,
        parallel_worker_count=4,
    )

    detail = build_native_buffer_detail(
        record=record,
        batch_id="batch-1",
        alive_after_attach=True,
        release_lag_steps=1,
    )

    assert tuple(asdict(detail)) == NATIVE_BUFFER_DETAIL_FIELDS
    assert detail.buffer_id == "native-1"
    assert detail.alive_after_attach is True
    assert detail.release_lag_steps == 1


def test_positional_phase_detail_builder_preserves_schema():
    detail = build_positional_phase_detail(
        run_id="run-1",
        batch_id="batch-1",
        expression="argmax(close, 3)",
        output_name="alpha",
        function_name="argmax",
        rows=10,
        groups=2,
        window=3,
        child_stage_kind="staged",
        prepare_sort_time_ms=1.0,
        child_expr_time_ms=2.0,
        positional_total_time_ms=3.0,
        positional_to_list_time_ms=0.5,
        positional_group_scan_time_ms=0.75,
        result_attach_time_ms=0.25,
        restore_time_ms=0.1,
        python_kernel_used=False,
        native_kernel_used=True,
        native_low_copy_bridge_used=True,
        python_object_bridge_used=False,
        native_parallel_used=True,
        group_parallelism_level=4,
        group_count=2,
        avg_group_size=5.0,
        max_group_size=6,
        output_non_null_count=8,
        rss_before_mb=20.0,
        rss_after_mb=21.0,
        peak_rss_mb=21.0,
    )

    assert tuple(asdict(detail)) == POSITIONAL_PHASE_DETAIL_FIELDS
    assert detail.native_kernel_used is True
    assert detail.python_kernel_used is False
    assert detail.output_non_null_count == 8
