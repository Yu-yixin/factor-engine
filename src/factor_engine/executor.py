from __future__ import annotations

"""Execution coordinator for planned factor expressions.

The route-specific execution shells live in `execution_*.py` modules. This
module keeps public evaluate/evaluate_many orchestration, compatibility
wrappers, planner handoff, and the still-coupled ordered batch coordinator.
"""

from collections.abc import Sequence
from dataclasses import dataclass
import time
from typing import Literal

import polars as pl

from factor_engine.ast_nodes import (
    BinaryOpNode,
    BooleanNode,
    CallNode,
    Expr,
    ListNode,
    NumberNode,
    UnaryOpNode,
    VariableNode,
)
from factor_engine.dag import NodeResultStore, NodeResultStoreEntry
from factor_engine.dag import DagNode
from factor_engine.execution_dag import (
    count_materializable_node_occurrences,
    dag_identity_for_expr,
    increment_planned_consumer,
    initialize_dag_execution_context,
    merge_node_hit_counts,
    rewrite_expr_with_materialized_nodes,
)
from factor_engine.execution_cse import materialize_shared_dag_nodes_on_sorted_df
from factor_engine.execution_lifecycle import (
    append_helper_trace_event,
    assert_lifecycle_step_model,
    materialized_helper_has_nested_dependency,
    nested_drop_order_valid,
    revalidate_helper_drop,
)
from factor_engine.errors import ExecutionError
from factor_engine.executor_utils import (
    expect_numeric_literal,
    expect_positive_integer_list_literal,
    expect_positive_numeric_literal,
    expect_scalar_number,
    expect_window_at_least,
    temporary_helper_name,
)
from factor_engine.execution_profiling import (
    build_memory_event,
    build_native_buffer_detail,
    build_output_detail,
)
from factor_engine.execution_ordering import (
    PreparedFrame,
    SegmentSpecKey,
    build_prepared_frame,
)
from factor_engine.execution_ordered import (
    evaluate_many_row_aligned_time_ordered,
    evaluate_row_aligned_time_ordered,
)
from factor_engine.execution_materialized import (
    evaluate_many_staged_columns,
    evaluate_materialized_ordered_column,
    evaluate_staged_column,
)
from factor_engine.execution_materialization import apply_dag_materialization_runtime_summary
from factor_engine.execution_output import (
    append_ordered_output_columns,
    restore_selected_columns,
)
from factor_engine.execution_positional import (
    attach_positional_kernel_from_stage,
    evaluate_positional_kernel,
    evaluate_positional_ordered_column,
    materialize_positional_call_on_sorted_df,
    scan_group_positional_extreme,
)
from factor_engine.execution_row_aligned import (
    evaluate_many_row_aligned_no_time_order,
    evaluate_row_aligned_no_time_order,
)
from factor_engine.execution_segmented import (
    build_equal_segment_id_expr,
    build_length_segment_id_expr,
    ensure_segment_lengths_cover_groups,
    evaluate_many_segmented_columns,
    evaluate_segmented_column,
    get_segmented_view,
    prepare_segmented_sorted_df,
)
from factor_engine.fourier import fourier_transform_frame
from factor_engine.lifecycle import (
    FirstWaveCandidateInput,
    FrameProjectionMode,
    FusionMode,
    HelperFirstWaveCandidateInput,
    HelperLifecycleMode,
    HelperSecondWaveNestedCandidateInput,
    LifecycleMode,
    MaterializationThresholdMode,
    NativeHeavyLifecycleInput,
    OutputAttachMode,
    PlannerCseMode,
    classify_native_heavy_lifecycle,
    collect_helper_drop_candidate_kind,
    helper_lifecycle_effective,
    is_first_wave_candidate,
    is_helper_lifecycle_active,
    is_lifecycle_active,
    lifecycle_effective,
    native_helper_usage_pattern,
    normalize_frame_projection_mode,
    normalize_fusion_mode,
    normalize_helper_lifecycle_mode,
    normalize_lifecycle_mode,
    normalize_materialization_threshold_mode,
    normalize_output_attach_mode,
    normalize_planner_cse_mode,
)
from factor_engine.planner import (
    BatchExecutionPlan,
    BatchPlanningItem,
    ExecutionPlan,
    ExecutionPlanner,
    MaterializedOrderedPlan,
    StagedChainPlan,
    StagedCrossSectionStep,
)
from factor_engine.profiling import (
    BatchDetail,
    NodeExecutionDetail,
    PositionalPhaseDetail,
    StageLifecycleProfiler,
    current_rss_mb,
)
from factor_engine.native_positional import evaluate_native_positional_kernel
from factor_engine.registry import get_function_spec
from factor_engine.registry import canonical_function_name
from factor_engine.stage_registry import StageRegistry
from factor_engine.validator import ExecutionProfile, ValidationResult


# Root argmax/argmin calls use the dedicated grouped kernel. This threshold only
# applies to the legacy expression fallback used inside compiled compositions.
SHORT_WINDOW_THRESHOLD = 8


@dataclass
class OutputRecord:
    output_name: str
    created_order_index: int
    source_column_name: str | None
    attached_order_index: int | None = None
    last_required_order_index: int | None = None
    frame_col_count_at_attach: int | None = None
    rss_at_attach_mb: float | None = None
    attached_to_working_frame: bool = False


@dataclass
class NativeBufferRecord:
    buffer_id: str
    related_output_name: str
    created_order_index: int
    bytes_estimate: int
    alive_before_attach: bool
    native_parallel_used: bool
    parallel_worker_count: int
    attached_order_index: int | None = None
    released_order_index: int | None = None


@dataclass
class OrderedBatchRuntime:
    batch_id: str
    profiler: StageLifecycleProfiler | None
    registry: StageRegistry
    lifecycle_mode: LifecycleMode
    helper_lifecycle_mode: HelperLifecycleMode
    helper_lifecycle_workload: str
    expression_count: int
    rows: int
    groups: int
    batch_started_at: float
    rss_before_mb: float
    base_frame_col_count: int
    prepare_sort_time_ms: float
    peak_frame_col_count: int
    peak_rss_mb: float
    stage_materialize_time_ms: float = 0.0
    restore_time_ms: float = 0.0
    append_time_ms: float = 0.0
    planned_stage_consumers: dict[tuple, int] | None = None
    peak_output_col_count: int = 0
    peak_stage_col_count: int = 0
    native_output_buffer_peak_bytes_estimate: int = 0
    parallel_enabled: bool = False
    parallel_worker_count: int = 1
    ast_node_count: int = 0
    dag_node_count: int = 0
    deduplicated_node_count: int = 0
    shared_node_count: int = 0
    materialized_node_count: int = 0
    expensive_node_count: int = 0
    result_store_peak_entry_count: int = 0
    estimated_unshared_compute_calls: int = 0
    compiled_output_heavy_occurrence_count: int = 0
    compiled_fallback_eval_count: int = 0
    node_store_compute_calls: int = 0
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

    def observe_frame(self, frame: pl.DataFrame) -> None:
        self.peak_frame_col_count = max(self.peak_frame_col_count, len(frame.columns))
        frame_columns = set(frame.columns)
        live_stage_columns = {
            record.column_name
            for record in self.registry.records.values()
            if record.is_alive and record.column_name in frame_columns
        }
        live_output_columns = {
            record.output_name
            for record in getattr(self, "output_records", {}).values()
            if record.attached_to_working_frame and record.output_name in frame_columns
        }
        self.peak_stage_col_count = max(self.peak_stage_col_count, len(live_stage_columns))
        self.peak_output_col_count = max(self.peak_output_col_count, len(live_output_columns))
        rss = current_rss_mb()
        self.peak_rss_mb = max(self.peak_rss_mb, rss)
        if self.profiler is not None:
            self.profiler.peak_rss_mb = max(self.profiler.peak_rss_mb, rss)

    def __post_init__(self) -> None:
        self.output_records: dict[str, OutputRecord] = {}
        self.native_buffer_records: dict[str, NativeBufferRecord] = {}
        self._native_buffer_alive_bytes_estimate = 0

    @property
    def lifecycle_active(self) -> bool:
        return is_lifecycle_active(self.lifecycle_mode)

    def next_order_index(self) -> int:
        return self.registry.next_order_index()

    def _add_memory_event(
        self,
        *,
        event_type: str,
        order_index: int,
        frame: pl.DataFrame,
        output_name: str | None = None,
        buffer_id: str | None = None,
        related_output_name: str | None = None,
        bytes_estimate: int | None = None,
        native_parallel_used: bool | None = None,
        parallel_worker_count: int | None = None,
    ) -> None:
        if self.profiler is None:
            return
        frame_columns = set(frame.columns)
        stage_col_count = sum(
            1
            for record in self.registry.records.values()
            if record.is_alive and record.column_name in frame_columns
        )
        output_col_count = sum(
            1
            for record in self.output_records.values()
            if record.attached_to_working_frame and record.output_name in frame_columns
        )
        self.profiler.add_memory_event(
            build_memory_event(
                event_type=event_type,
                batch_id=self.batch_id,
                order_index=order_index,
                frame_col_count=len(frame.columns),
                rss_mb=current_rss_mb(),
                output_name=output_name,
                buffer_id=buffer_id,
                related_output_name=related_output_name,
                bytes_estimate=bytes_estimate,
                output_col_count=output_col_count,
                stage_col_count=stage_col_count,
                native_buffer_alive_bytes_estimate=self._native_buffer_alive_bytes_estimate,
                native_parallel_used=native_parallel_used,
                parallel_worker_count=parallel_worker_count,
            )
        )

    def register_output_created(
        self,
        output_name: str,
        *,
        source_column_name: str | None,
        frame: pl.DataFrame,
    ) -> None:
        if output_name in self.output_records:
            return
        order_index = self.next_order_index()
        self.output_records[output_name] = OutputRecord(
            output_name=output_name,
            created_order_index=order_index,
            source_column_name=source_column_name,
        )
        self._add_memory_event(
            event_type="output_created",
            order_index=order_index,
            frame=frame,
            output_name=output_name,
        )

    def mark_output_attached(
        self,
        output_name: str,
        *,
        frame: pl.DataFrame,
        attached_to_working_frame: bool,
    ) -> None:
        record = self.output_records.get(output_name)
        if record is None:
            self.register_output_created(output_name, source_column_name=output_name, frame=frame)
            record = self.output_records[output_name]
        order_index = self.next_order_index()
        record.attached_order_index = order_index
        record.last_required_order_index = order_index
        record.frame_col_count_at_attach = len(frame.columns)
        record.rss_at_attach_mb = current_rss_mb()
        record.attached_to_working_frame = attached_to_working_frame
        self._add_memory_event(
            event_type="output_attached",
            order_index=order_index,
            frame=frame,
            output_name=output_name,
        )

    def mark_output_released(self, output_name: str, *, frame: pl.DataFrame) -> None:
        record = self.output_records.get(output_name)
        if record is None:
            return
        order_index = self.next_order_index()
        record.attached_to_working_frame = False
        self._add_memory_event(
            event_type="output_released",
            order_index=order_index,
            frame=frame,
            output_name=output_name,
        )

    def register_native_buffer_created(
        self,
        *,
        related_output_name: str,
        bytes_estimate: int,
        frame: pl.DataFrame,
        native_parallel_used: bool,
        parallel_worker_count: int,
    ) -> str:
        order_index = self.next_order_index()
        buffer_id = f"{self.batch_id}:native_buffer:{len(self.native_buffer_records) + 1}"
        self.native_buffer_records[buffer_id] = NativeBufferRecord(
            buffer_id=buffer_id,
            related_output_name=related_output_name,
            created_order_index=order_index,
            bytes_estimate=bytes_estimate,
            alive_before_attach=True,
            native_parallel_used=native_parallel_used,
            parallel_worker_count=parallel_worker_count,
        )
        self._native_buffer_alive_bytes_estimate += bytes_estimate
        self.native_output_buffer_peak_bytes_estimate = max(
            self.native_output_buffer_peak_bytes_estimate,
            self._native_buffer_alive_bytes_estimate,
        )
        self.parallel_enabled = self.parallel_enabled or native_parallel_used
        self.parallel_worker_count = max(self.parallel_worker_count, parallel_worker_count)
        self._add_memory_event(
            event_type="native_buffer_created",
            order_index=order_index,
            frame=frame,
            buffer_id=buffer_id,
            related_output_name=related_output_name,
            bytes_estimate=bytes_estimate,
            native_parallel_used=native_parallel_used,
            parallel_worker_count=parallel_worker_count,
        )
        return buffer_id

    def mark_native_buffer_attached(self, buffer_id: str, *, frame: pl.DataFrame) -> None:
        record = self.native_buffer_records.get(buffer_id)
        if record is None:
            return
        order_index = self.next_order_index()
        record.attached_order_index = order_index
        self._add_memory_event(
            event_type="native_buffer_attached",
            order_index=order_index,
            frame=frame,
            buffer_id=buffer_id,
            related_output_name=record.related_output_name,
            bytes_estimate=record.bytes_estimate,
            native_parallel_used=record.native_parallel_used,
            parallel_worker_count=record.parallel_worker_count,
        )

    def mark_native_buffer_released(self, buffer_id: str, *, frame: pl.DataFrame) -> None:
        record = self.native_buffer_records.get(buffer_id)
        if record is None or record.released_order_index is not None:
            return
        order_index = self.next_order_index()
        record.released_order_index = order_index
        self._native_buffer_alive_bytes_estimate = max(
            0,
            self._native_buffer_alive_bytes_estimate - record.bytes_estimate,
        )
        self._add_memory_event(
            event_type="native_buffer_released",
            order_index=order_index,
            frame=frame,
            buffer_id=buffer_id,
            related_output_name=record.related_output_name,
            bytes_estimate=record.bytes_estimate,
            native_parallel_used=record.native_parallel_used,
            parallel_worker_count=record.parallel_worker_count,
        )

    def register_stage(
        self,
        *,
        expr_key: object,
        column_name: str,
        stage_kind: str,
        producer_route: str,
        frame: pl.DataFrame,
        cache_key: tuple | None = None,
    ) -> None:
        self.observe_frame(frame)
        self.registry.register_stage(
            expr_key=expr_key,
            column_name=column_name,
            stage_kind=stage_kind,
            producer_route=producer_route,
            frame_col_count=len(frame.columns),
            cache_key=cache_key,
        )
        if cache_key is not None and self.planned_stage_consumers is not None:
            planned_count = self.planned_stage_consumers.get(cache_key)
            if planned_count is not None:
                self.registry.set_expected_consumers(column_name, planned_count)

    def consume_stage(
        self,
        column_name: str,
        *,
        consumer_kind: str,
        frame: pl.DataFrame,
    ) -> None:
        self.observe_frame(frame)
        self.registry.record_consume(
            column_name,
            consumer_kind=consumer_kind,
            frame_col_count=len(frame.columns),
        )

    def stage_kind_for_column(self, column_name: str) -> str:
        stage_id = self.registry.column_to_stage_id.get(column_name)
        if stage_id is None:
            return "unknown"
        return self.registry.records[stage_id].stage_kind

    def add_positional_phase(self, detail: PositionalPhaseDetail) -> None:
        if self.profiler is not None:
            self.profiler.add_positional_phase(detail)

    def sweep(
        self,
        frame: pl.DataFrame,
        *,
        stage_cache: dict[tuple, str],
        output_names: set[str],
    ) -> pl.DataFrame:
        swept = self.registry.sweep_drop_candidates(
            frame,
            stage_cache=stage_cache,
            output_names=output_names,
            enabled=self.lifecycle_active,
        )
        self.observe_frame(swept)
        return swept

    def finish(
        self,
        *,
        frame: pl.DataFrame,
        output_names: set[str],
        output_source_columns: set[str] | None = None,
    ) -> None:
        self.observe_frame(frame)
        if self.profiler is not None:
            for phase in self.profiler.positional_phases:
                if phase.batch_id == self.batch_id:
                    phase.restore_time_ms = self.restore_time_ms
        details = self.registry.snapshot_batch_end(
            frame_col_count=len(frame.columns),
            output_names=output_names,
        )
        if self.profiler is None:
            return

        alive_at_end = sum(1 for item in details if item.alive_at_batch_end)
        materialized = sum(1 for item in details if item.stage_kind.startswith("materialized"))
        positional = sum(1 for item in details if item.stage_kind.startswith("positional"))
        staged_prefix = sum(1 for item in details if item.stage_kind.startswith("staged"))
        planned_reusable = sum(1 for item in details if item.planned_consumer_count_total > 1)
        retained_for_reuse = sum(1 for item in details if item.kept_alive_for_planned_reuse)
        output_source_columns = output_source_columns or set()
        retained_for_output = sum(
            1
            for item in details
            if item.alive_at_batch_end and item.column_name in output_source_columns
        )
        late_alive = sum(
            1
            for item in details
            if item.alive_at_batch_end and item.planned_consumer_count_total > 0
        )
        alive_outputs = len(self.output_records)
        batch_end_order_index = self.next_order_index()
        for record in self.output_records.values():
            if record.last_required_order_index is None:
                record.last_required_order_index = batch_end_order_index
            is_late_alive = (
                record.attached_order_index is not None
                and record.last_required_order_index is not None
                and record.attached_order_index < record.last_required_order_index
            )
            self.profiler.add_output(
                build_output_detail(
                    record=record,
                    batch_id=self.batch_id,
                    alive_at_batch_end=True,
                    is_late_alive_output=is_late_alive,
                )
            )
        native_buffer_release_lag = 0
        native_alive_before_attach = 0
        native_alive_after_attach = 0
        for record in self.native_buffer_records.values():
            if record.alive_before_attach:
                native_alive_before_attach += 1
            release_lag = None
            alive_after_attach = False
            if record.attached_order_index is not None:
                if record.released_order_index is None:
                    alive_after_attach = True
                else:
                    release_lag = max(0, record.released_order_index - record.attached_order_index - 1)
                    alive_after_attach = release_lag > 0
                    native_buffer_release_lag = max(native_buffer_release_lag, release_lag)
            if alive_after_attach:
                native_alive_after_attach += 1
            self.profiler.add_native_buffer(
                build_native_buffer_detail(
                    record=record,
                    batch_id=self.batch_id,
                    alive_after_attach=alive_after_attach,
                    release_lag_steps=release_lag,
                )
            )
        self.profiler.add_batch(
            BatchDetail(
                batch_id=self.batch_id,
                route="ordered_batch",
                expression_count=self.expression_count,
                rows=self.rows,
                groups=self.groups,
                lifecycle_mode=self.lifecycle_mode,
                helper_lifecycle_mode=self.helper_lifecycle_mode,
                batch_total_time_ms=(time.perf_counter() - self.batch_started_at) * 1000,
                prepare_sort_time_ms=self.prepare_sort_time_ms,
                stage_materialize_time_ms=self.stage_materialize_time_ms,
                restore_time_ms=self.restore_time_ms,
                append_time_ms=self.append_time_ms,
                rss_before_mb=self.rss_before_mb,
                rss_after_mb=current_rss_mb(),
                peak_rss_mb=self.peak_rss_mb,
                base_frame_col_count=self.base_frame_col_count,
                peak_frame_col_count=self.peak_frame_col_count,
                final_frame_col_count=len(frame.columns),
                stage_count=len(details),
                peak_live_stage_count_estimate=self.registry.peak_live_stage_count,
                alive_stage_at_batch_end_count=alive_at_end,
                materialized_stage_count=materialized,
                positional_stage_count=positional,
                staged_prefix_stage_count=staged_prefix,
                dropped_stage_count=self.registry.dropped_stage_count,
                planned_reusable_stage_count=planned_reusable,
                recomputed_stage_count=self.registry.recomputed_stage_count,
                avoided_recomputation_count=self.registry.avoided_recomputation_count,
                late_alive_stage_count=late_alive,
                peak_output_col_count=self.peak_output_col_count,
                peak_stage_col_count=self.peak_stage_col_count,
                alive_output_at_batch_end_count=alive_outputs,
                late_alive_output_count=sum(
                    1
                    for record in self.output_records.values()
                    if record.attached_order_index is not None
                    and record.last_required_order_index is not None
                    and record.attached_order_index < record.last_required_order_index
                ),
                native_output_buffer_count=len(self.native_buffer_records),
                native_output_buffer_peak_bytes_estimate=(
                    self.native_output_buffer_peak_bytes_estimate
                ),
                native_buffer_alive_before_attach=native_alive_before_attach,
                native_buffer_alive_after_attach=native_alive_after_attach,
                native_buffer_release_lag=native_buffer_release_lag,
                peak_native_buffer_bytes_estimate=self.native_output_buffer_peak_bytes_estimate,
                retained_for_reuse_stage_count=retained_for_reuse,
                retained_for_output_stage_count=retained_for_output,
                parallel_enabled=self.parallel_enabled,
                parallel_worker_count=self.parallel_worker_count,
                parallel_buffer_peak_estimate=(
                    self.native_output_buffer_peak_bytes_estimate
                    if self.parallel_enabled
                    else 0
                ),
                ast_node_count=self.ast_node_count,
                dag_node_count=self.dag_node_count,
                deduplicated_node_count=self.deduplicated_node_count,
                shared_node_count=self.shared_node_count,
                materialized_node_count=self.materialized_node_count,
                expensive_node_count=self.expensive_node_count,
                result_store_peak_entry_count=self.result_store_peak_entry_count,
                finalize_time_ms=self.restore_assemble_time_ms + self.append_time_ms,
                node_store_compute_calls=self.node_store_compute_calls,
                estimated_unshared_compute_calls=self.estimated_unshared_compute_calls,
                compiled_output_heavy_occurrence_count=(
                    self.compiled_output_heavy_occurrence_count
                ),
                compiled_fallback_eval_count=self.compiled_fallback_eval_count,
                node_store_read_count=self.node_store_read_count,
                reuse_consumer_count=self.reuse_consumer_count,
                node_store_compute_time_ms=self.node_store_compute_time_ms,
                compiled_output_eval_time_ms=self.compiled_output_eval_time_ms,
                restore_assemble_time_ms=self.restore_assemble_time_ms,
                restore_assemble_step=self.restore_assemble_step,
                append_step=self.append_step,
                finalize_step=self.finalize_step,
                batch_end_step=self.batch_end_step,
                lifecycle_candidate_count=self.lifecycle_candidate_count,
                lifecycle_releasable_node_count=self.lifecycle_releasable_node_count,
                lifecycle_peak_live_node_count=self.lifecycle_peak_live_node_count,
                lifecycle_peak_live_bytes_est=self.lifecycle_peak_live_bytes_est,
                avg_release_lag_steps=self.avg_release_lag_steps,
                max_release_lag_steps=self.max_release_lag_steps,
                avg_structural_release_lag_steps=self.avg_structural_release_lag_steps,
                max_structural_release_lag_steps=self.max_structural_release_lag_steps,
                avg_finalize_retention_lag_steps=self.avg_finalize_retention_lag_steps,
                max_finalize_retention_lag_steps=self.max_finalize_retention_lag_steps,
                potential_live_bytes_step_savings=self.potential_live_bytes_step_savings,
                l2_first_wave_candidate_count=self.l2_first_wave_candidate_count,
                dropped_node_count=self.dropped_node_count,
                drop_hit_count=self.drop_hit_count,
                drop_miss_count=self.drop_miss_count,
                peak_live_node_count_after_drop=self.peak_live_node_count_after_drop,
                peak_live_bytes_est_before_drop=self.peak_live_bytes_est_before_drop,
                peak_live_bytes_est_after_drop=self.peak_live_bytes_est_after_drop,
                drop_delay_steps_avg=self.drop_delay_steps_avg,
                drop_delay_steps_max=self.drop_delay_steps_max,
                lifecycle_effective=self.lifecycle_effective,
                multi_node_overlap_peak=self.multi_node_overlap_peak,
                multi_node_peak_live_bytes_before=self.multi_node_peak_live_bytes_before,
                multi_node_peak_live_bytes_after=self.multi_node_peak_live_bytes_after,
                per_node_drop_order=self.per_node_drop_order,
                nested_drop_order_valid=self.nested_drop_order_valid,
                partial_reuse_safety_flag=self.partial_reuse_safety_flag,
                node_compute_count=self.node_compute_count,
                node_hit_count=self.node_hit_count,
                total_compute_calls=self.total_compute_calls,
                total_store_hits=self.total_store_hits,
                shared_node_hit_rate=self.shared_node_hit_rate,
                compute_time_ms=self.compute_time_ms,
                store_write_time_ms=self.store_write_time_ms,
                store_hit_time_ms=self.store_hit_time_ms,
                native_heavy_node_count=self.native_heavy_node_count,
                native_heavy_forbidden_count=self.native_heavy_forbidden_count,
                native_heavy_observable_only_count=self.native_heavy_observable_only_count,
                native_heavy_candidate_future_count=self.native_heavy_candidate_future_count,
                native_compute_time_ms=self.native_compute_time_ms,
                native_path_normalization_time_ms=self.native_path_normalization_time_ms,
                native_storage_residency_bytes=self.native_storage_residency_bytes,
                native_node_store_read_count=self.native_node_store_read_count,
                native_logical_consumer_count=self.native_logical_consumer_count,
                native_effective_use_count=self.native_effective_use_count,
                native_fallback_eval_count=self.native_fallback_eval_count,
                native_rewrite_applied_count=self.native_rewrite_applied_count,
                native_helper_usage_patterns=self.native_helper_usage_patterns,
                helper_column_count=self.helper_column_count,
                helper_releasable_count=self.helper_releasable_count,
                helper_blocked_count=self.helper_blocked_count,
                helper_peak_live_bytes=self.helper_peak_live_bytes,
                helper_potential_savings=self.helper_potential_savings,
                helper_blocker_reasons=self.helper_blocker_reasons,
                helper_dropped_count=self.helper_dropped_count,
                helper_drop_miss_count=self.helper_drop_miss_count,
                helper_peak_live_bytes_before_drop=self.helper_peak_live_bytes_before_drop,
                helper_peak_live_bytes_after_drop=self.helper_peak_live_bytes_after_drop,
                helper_frame_width_before_drop=self.helper_frame_width_before_drop,
                helper_frame_width_after_drop=self.helper_frame_width_after_drop,
                helper_drop_delay_steps_avg=self.helper_drop_delay_steps_avg,
                helper_drop_delay_steps_max=self.helper_drop_delay_steps_max,
                helper_lifecycle_effective=self.helper_lifecycle_effective,
                nested_helper_dropped_count=self.nested_helper_dropped_count,
                nested_helper_drop_missed_count=self.nested_helper_drop_missed_count,
                nested_helper_peak_live_bytes_before_drop=(
                    self.nested_helper_peak_live_bytes_before_drop
                ),
                nested_helper_peak_live_bytes_after_drop=(
                    self.nested_helper_peak_live_bytes_after_drop
                ),
                nested_helper_frame_width_before_drop=self.nested_helper_frame_width_before_drop,
                nested_helper_frame_width_after_drop=self.nested_helper_frame_width_after_drop,
                nested_helper_lifecycle_effective=self.nested_helper_lifecycle_effective,
                recomputation_guardrail_candidate_count=(
                    self.recomputation_guardrail_candidate_count
                ),
                recomputation_guardrail_blocked_count=(
                    self.recomputation_guardrail_blocked_count
                ),
                recomputation_guardrail_allowed_count=(
                    self.recomputation_guardrail_allowed_count
                ),
                recomputation_expansion_estimate=self.recomputation_expansion_estimate,
                recomputation_expansion_actual_delta=(
                    self.recomputation_expansion_actual_delta
                ),
            )
        )


class Executor:
    def __init__(
        self,
        df: pl.DataFrame,
        time_col: str = "time",
        code_col: str = "code",
        profile_recorder: StageLifecycleProfiler | None = None,
        lifecycle_enabled: bool = False,
        lifecycle_mode: str | None = None,
        helper_lifecycle_mode: str | None = None,
        output_attach_mode: str | None = None,
        frame_projection_mode: str | None = None,
        materialization_threshold_mode: str | None = None,
        recomputation_guardrail_max_expansion: int = 0,
        planner_cse_mode: str | None = None,
        fusion_mode: str | None = None,
        dag_cse_enabled: bool = True,
    ):
        self.df = df
        self.time_col = time_col
        self.code_col = code_col
        self.profile_recorder = profile_recorder
        self.lifecycle_mode = normalize_lifecycle_mode(
            lifecycle=lifecycle_enabled,
            lifecycle_mode=lifecycle_mode,
        )
        self.helper_lifecycle_mode = normalize_helper_lifecycle_mode(
            helper_lifecycle_mode=helper_lifecycle_mode,
        )
        self.output_attach_mode: OutputAttachMode = normalize_output_attach_mode(
            output_attach_mode=output_attach_mode,
        )
        self.frame_projection_mode: FrameProjectionMode = normalize_frame_projection_mode(
            frame_projection_mode=frame_projection_mode,
        )
        self.materialization_threshold_mode: MaterializationThresholdMode = (
            normalize_materialization_threshold_mode(
                materialization_threshold_mode=materialization_threshold_mode,
            )
        )
        self.recomputation_guardrail_max_expansion = recomputation_guardrail_max_expansion
        self.planner_cse_mode: PlannerCseMode = normalize_planner_cse_mode(
            planner_cse_mode=planner_cse_mode,
        )
        self.fusion_mode: FusionMode = normalize_fusion_mode(
            fusion_mode=fusion_mode,
        )
        self.helper_lifecycle_workload = self._infer_helper_lifecycle_workload()
        self.dag_cse_enabled = dag_cse_enabled
        self._prepared_frame: PreparedFrame | None = None
        self._planner = ExecutionPlanner(time_col=self.time_col, code_col=self.code_col)
        self._segment_id_name = self._temporary_helper_name("__segment_id")
        self._code_pos_name = self._temporary_helper_name(
            "__code_pos",
            reserved={self._segment_id_name},
        )
        self._code_len_name = self._temporary_helper_name(
            "__code_len",
            reserved={self._segment_id_name, self._code_pos_name},
        )

    def _infer_helper_lifecycle_workload(self) -> str:
        if self.profile_recorder is None:
            return ""
        benchmark_name = self.profile_recorder.benchmark_name
        for workload in ("multi_shared_nodes", "partial_reuse", "repeated_heavy"):
            if workload in benchmark_name:
                return workload
        return ""

    def _temporary_helper_name(
        self,
        base_name: str,
        *,
        reserved: set[str] | None = None,
    ) -> str:
        return temporary_helper_name(base_name, set(self.df.columns), reserved=reserved)

    def compile(self, expr: Expr) -> pl.Expr:
        return self._compile_expr(expr)

    def evaluate(
        self,
        expr: Expr,
        output_name: str = "result",
        validation: ValidationResult | None = None,
        plan: ExecutionPlan | None = None,
    ) -> pl.DataFrame:
        # Column expressions keep the original row shape; table expressions do not.
        if validation is not None and validation.result_kind == "table":
            return self._evaluate_table(expr, validation)

        if validation is None:
            profile = self._infer_execution_profile(expr)
        else:
            profile = validation.profile

        if plan is None:
            result_kind = validation.result_kind if validation is not None else "column"
            plan = self._planner.build_plan(
                expr,
                ValidationResult(
                    result_kind=result_kind,
                    profile=profile,
                    backend=validation.backend if validation is not None else None,
                ),
            )

        return self._evaluate_column(expr, output_name=output_name, profile=profile, plan=plan)

    def evaluate_compiled(
        self,
        compiled: pl.Expr,
        *,
        output_name: str = "result",
        validation: ValidationResult,
    ) -> pl.DataFrame:
        if validation.result_kind != "column":
            raise ExecutionError("evaluate_compiled() only supports column expressions")

        return self._evaluate_compiled_column(
            compiled,
            output_name=output_name,
            profile=validation.profile,
        )

    def evaluate_many(
        self,
        items: list[tuple[str, Expr, ValidationResult, ExecutionPlan | None]],
    ) -> pl.DataFrame:
        compiled_no_time_items: list[tuple[str, ValidationResult, pl.Expr]] = []
        compiled_time_items: list[tuple[str, Expr, ValidationResult, pl.Expr]] = []
        planning_items: list[BatchPlanningItem] = []

        for output_name, expr, validation, plan in items:
            item_plan = plan or self._planner.build_plan(expr, validation)
            planning_items.append(
                BatchPlanningItem(
                    output_name=output_name,
                    expr=expr,
                    validation=validation,
                    plan=item_plan,
                )
            )
            if item_plan.route == "compiled":
                if validation.profile.needs_time_order:
                    compiled_time_items.append((output_name, expr, validation, self.compile(expr)))
                else:
                    compiled_no_time_items.append((output_name, validation, self.compile(expr)))

        deferred_planning_items = [
            item
            for item in planning_items
            if item.plan.route != "compiled" or item.validation.profile.needs_time_order
        ]
        batch_plan = self._planner.build_batch_plan(deferred_planning_items)
        result_df = self.df
        if compiled_no_time_items:
            result_df = Executor(
                result_df,
                time_col=self.time_col,
                code_col=self.code_col,
                profile_recorder=self.profile_recorder,
                lifecycle_mode=self.lifecycle_mode,
                dag_cse_enabled=self.dag_cse_enabled,
            ).evaluate_many_compiled(compiled_no_time_items)

        if (
            compiled_time_items
            or batch_plan.segmented_items
            or batch_plan.staged_items
            or batch_plan.materialized_ordered_items
            or batch_plan.positional_items
        ):
            result_df = Executor(
                result_df,
                time_col=self.time_col,
                code_col=self.code_col,
                profile_recorder=self.profile_recorder,
                lifecycle_mode=self.lifecycle_mode,
                dag_cse_enabled=self.dag_cse_enabled,
            ).evaluate_many_planned(
                batch_plan,
                compiled_time_items=compiled_time_items,
            )

        original_columns = list(self.df.columns)
        appended_columns = [output_name for output_name, _, _, _ in items if output_name not in original_columns]
        return result_df.select([*original_columns, *appended_columns])

    def evaluate_many_planned(
        self,
        batch_plan: BatchExecutionPlan,
        *,
        compiled_time_items: list[tuple[str, Expr, ValidationResult, pl.Expr]] | None = None,
    ) -> pl.DataFrame:
        result_df = self.df
        ordered_compiled_items = compiled_time_items or []

        if batch_plan.segmented_items:
            result_df = Executor(
                result_df,
                time_col=self.time_col,
                code_col=self.code_col,
                profile_recorder=self.profile_recorder,
                lifecycle_mode=self.lifecycle_mode,
                helper_lifecycle_mode=self.helper_lifecycle_mode,
                dag_cse_enabled=self.dag_cse_enabled,
            )._evaluate_many_segmented_columns(
                [
                    (item.output_name, item.expr, item.validation)
                    for item in batch_plan.segmented_items
                ]
            )

        if (
            ordered_compiled_items
            or batch_plan.staged_items
            or batch_plan.materialized_ordered_items
            or batch_plan.positional_items
        ):
            result_df = Executor(
                result_df,
                time_col=self.time_col,
                code_col=self.code_col,
                profile_recorder=self.profile_recorder,
                lifecycle_mode=self.lifecycle_mode,
                helper_lifecycle_mode=self.helper_lifecycle_mode,
                dag_cse_enabled=self.dag_cse_enabled,
            )._evaluate_many_ordered_batch_plan(
                batch_plan,
                compiled_time_items=ordered_compiled_items,
            )

        original_columns = list(self.df.columns)
        appended_columns = [
            item.output_name
            for item in (
                *batch_plan.segmented_items,
                *batch_plan.staged_items,
                *batch_plan.materialized_ordered_items,
                *batch_plan.positional_items,
            )
            if item.output_name not in original_columns
        ]
        appended_columns.extend(
            [
                output_name
                for output_name, _expr, _validation, _compiled in ordered_compiled_items
                if output_name not in original_columns and output_name not in appended_columns
            ]
        )
        return result_df.select([*original_columns, *appended_columns])

    def evaluate_many_compiled(
        self,
        items: list[tuple[str, ValidationResult, pl.Expr]],
    ) -> pl.DataFrame:
        if not items:
            return self.df

        no_time_order_items: list[tuple[str, pl.Expr]] = []
        time_ordered_items: list[tuple[str, pl.Expr]] = []

        for output_name, validation, compiled in items:
            if validation.result_kind != "column":
                raise ExecutionError("evaluate_many_compiled() only supports column expressions")

            if validation.profile.needs_time_order:
                time_ordered_items.append((output_name, compiled))
            else:
                no_time_order_items.append((output_name, compiled))

        result_df = self.df

        if no_time_order_items:
            result_df = self._evaluate_many_row_aligned_no_time_order(
                result_df,
                no_time_order_items,
            )

        if time_ordered_items:
            ordered_columns = self._evaluate_many_row_aligned_time_ordered(time_ordered_items)
            result_df = result_df.with_columns(
                [ordered_columns.get_column(output_name) for output_name, _ in time_ordered_items]
            )

        original_columns = list(self.df.columns)
        appended_columns = [output_name for output_name, _, _ in items if output_name not in original_columns]
        return result_df.select([*original_columns, *appended_columns])

    def _evaluate_column(
        self,
        expr: Expr,
        *,
        output_name: str,
        profile: ExecutionProfile,
        plan: ExecutionPlan,
    ) -> pl.DataFrame:
        if plan.route == "segmented":
            return self._evaluate_segmented_column(expr, output_name=output_name)

        if plan.route == "staged":
            if plan.staged is None:
                raise ExecutionError("Internal error: staged plan missing staged specification")
            return self._evaluate_staged_column(plan.staged, output_name=output_name)

        if plan.route == "materialized_ordered":
            if plan.materialized_ordered is None:
                raise ExecutionError(
                    "Internal error: materialized ordered plan is missing plan specification"
                )
            return self._evaluate_materialized_ordered_column(
                plan.materialized_ordered,
                output_name=output_name,
            )

        if plan.route == "positional_ordered":
            return self._evaluate_positional_ordered_column(expr, output_name=output_name)

        compiled = self.compile(expr)
        return self._evaluate_compiled_column(
            compiled,
            output_name=output_name,
            profile=profile,
        )

    def _evaluate_compiled_column(
        self,
        compiled: pl.Expr,
        *,
        output_name: str,
        profile: ExecutionProfile,
    ) -> pl.DataFrame:
        if profile.needs_time_order:
            return self._evaluate_row_aligned_time_ordered(compiled, output_name=output_name)

        return self._evaluate_row_aligned_no_time_order(compiled, output_name=output_name)

    def _evaluate_row_aligned_no_time_order(
        self,
        compiled: pl.Expr,
        *,
        output_name: str,
    ) -> pl.DataFrame:
        return evaluate_row_aligned_no_time_order(
            self.df,
            compiled,
            output_name=output_name,
        )

    def _evaluate_row_aligned_time_ordered(
        self,
        compiled: pl.Expr,
        *,
        output_name: str,
    ) -> pl.DataFrame:
        prepared = self._get_prepared_frame()
        return evaluate_row_aligned_time_ordered(
            prepared,
            compiled,
            output_name=output_name,
        )

    def _evaluate_many_row_aligned_no_time_order(
        self,
        base_df: pl.DataFrame,
        items: list[tuple[str, pl.Expr]],
    ) -> pl.DataFrame:
        return evaluate_many_row_aligned_no_time_order(base_df, items)

    def _evaluate_many_row_aligned_time_ordered(
        self,
        items: list[tuple[str, pl.Expr]],
    ) -> pl.DataFrame:
        prepared = self._get_prepared_frame()
        return evaluate_many_row_aligned_time_ordered(prepared, items)

    def _evaluate_segmented_column(
        self,
        expr: Expr,
        *,
        output_name: str,
    ) -> pl.DataFrame:
        prepared = self._get_prepared_frame()
        return evaluate_segmented_column(
            prepared,
            self.df,
            expr,
            output_name=output_name,
            get_segment_spec_key=self._get_segment_spec_key,
            get_segmented_view_for_key=self._get_segmented_view,
            compile_expr=self._compile_expr,
        )

    def _evaluate_many_segmented_columns(
        self,
        items: list[tuple[str, Expr, ValidationResult]],
    ) -> pl.DataFrame:
        if not items:
            return self.df

        prepared = self._get_prepared_frame()
        return evaluate_many_segmented_columns(
            prepared,
            self.df,
            items,
            get_segment_spec_key=self._get_segment_spec_key,
            get_segmented_view_for_key=self._get_segmented_view,
            compile_expr=self._compile_expr,
        )

    def _evaluate_staged_column(
        self,
        staged_plan: StagedChainPlan,
        *,
        output_name: str,
    ) -> pl.DataFrame:
        prepared = self._get_prepared_frame()
        return evaluate_staged_column(
            prepared,
            self.df,
            output_name=output_name,
            materialize_staged_chain=lambda sorted_df: self._materialize_staged_chain_on_sorted_df(
                sorted_df,
                staged_plan=staged_plan,
                reserved_names=set(sorted_df.columns),
                stage_cache={},
            ),
        )

    def _evaluate_many_staged_columns(
        self,
        items: list[tuple[str, StagedChainPlan]],
    ) -> pl.DataFrame:
        if not items:
            return self.df

        prepared = self._get_prepared_frame()
        return evaluate_many_staged_columns(
            prepared,
            self.df,
            items,
            materialize_staged_chain=(
                lambda sorted_df, staged_plan, reserved_names, stage_cache: (
                    self._materialize_staged_chain_on_sorted_df(
                        sorted_df,
                        staged_plan=staged_plan,
                        reserved_names=reserved_names,
                        stage_cache=stage_cache,
                    )
                )
            ),
        )

    def _plan_ordered_batch_stage_consumers(
        self,
        batch_plan: BatchExecutionPlan,
    ) -> dict[tuple, int]:
        planned: dict[tuple, int] = {}

        def add(cache_key: tuple | None) -> None:
            if cache_key is not None:
                planned[cache_key] = planned.get(cache_key, 0) + 1

        for item in batch_plan.positional_items:
            self._collect_explicit_stage_consumers(item.expr, planned)
            add(self._explicit_stage_cache_key(item.expr))

        for item in batch_plan.materialized_ordered_items:
            self._collect_explicit_stage_consumers(item.expr, planned)
            add(self._explicit_stage_cache_key(item.expr))

        for binding in batch_plan.staged_output_bindings:
            add(binding.cache_key)

        return planned

    def _collect_explicit_stage_consumers(
        self,
        expr: Expr,
        planned: dict[tuple, int],
    ) -> None:
        profile = self._infer_execution_profile(expr)
        plan = self._planner.build_plan(
            expr,
            ValidationResult(result_kind="column", profile=profile, backend=None),
        )

        if plan.route == "positional_ordered":
            if isinstance(expr, CallNode) and len(expr.args) == 2:
                child_expr = expr.args[0]
                self._increment_planned_consumer(planned, self._explicit_stage_cache_key(child_expr))
                self._collect_explicit_stage_consumers(child_expr, planned)
            return

        if plan.route == "materialized_ordered" and plan.materialized_ordered is not None:
            for input_expr in plan.materialized_ordered.input_exprs:
                self._increment_planned_consumer(planned, self._explicit_stage_cache_key(input_expr))
                self._collect_explicit_stage_consumers(input_expr, planned)

    @staticmethod
    def _increment_planned_consumer(planned: dict[tuple, int], cache_key: tuple | None) -> None:
        increment_planned_consumer(planned, cache_key)

    def _explicit_stage_cache_key(self, expr: Expr) -> tuple | None:
        profile = self._infer_execution_profile(expr)
        plan = self._planner.build_plan(
            expr,
            ValidationResult(result_kind="column", profile=profile, backend=None),
        )

        if plan.route == "compiled":
            return ("expr", self._planner.expr_key(expr))

        if plan.route == "positional_ordered":
            if not isinstance(expr, CallNode) or len(expr.args) != 2:
                return None
            window = self._expect_positive_numeric_literal(expr.args[1], expr.name)
            return (
                "positional_kernel",
                expr.name,
                self._planner.expr_key(expr.args[0]),
                window,
            )

        if plan.route == "materialized_ordered" and plan.materialized_ordered is not None:
            materialized = plan.materialized_ordered
            return (
                "materialized_ordered",
                materialized.func_name,
                tuple(self._planner.expr_key(input_expr) for input_expr in materialized.input_exprs),
                materialized.window,
            )

        if plan.route == "staged" and plan.staged is not None:
            source_key = self._planner.expr_key(plan.staged.source_expr)
            if not plan.staged.steps:
                return ("source", source_key)
            prefix_keys = tuple(
                self._planner.staged_step_key(step)
                for step in plan.staged.steps
            )
            return ("chain", source_key, prefix_keys)

        return None

    def _dag_identity_for_expr(self, expr: Expr) -> tuple:
        return dag_identity_for_expr(
            expr,
            time_col=self.time_col,
            code_col=self.code_col,
            materialization_threshold_mode=self.materialization_threshold_mode,
            recomputation_guardrail_max_expansion=self.recomputation_guardrail_max_expansion,
            planner_cse_mode=self.planner_cse_mode,
            fusion_mode=self.fusion_mode,
        )

    def _rewrite_expr_with_materialized_nodes(
        self,
        expr: Expr,
        *,
        materialized_column_by_identity: dict[tuple, str],
        dag_nodes_by_identity: dict[tuple, DagNode],
        skip_identity: tuple | None = None,
    ) -> tuple[Expr, dict[str, int]]:
        return rewrite_expr_with_materialized_nodes(
            expr,
            materialized_column_by_identity=materialized_column_by_identity,
            dag_nodes_by_identity=dag_nodes_by_identity,
            identity_for_expr=self._dag_identity_for_expr,
            skip_identity=skip_identity,
        )

    @staticmethod
    def _merge_node_hit_counts(target: dict[str, int], source: dict[str, int]) -> None:
        merge_node_hit_counts(target, source)

    def _count_materializable_node_occurrences(
        self,
        expr: Expr,
        *,
        dag_nodes_by_identity: dict[tuple, DagNode],
        node_lifecycle_class: str | None = None,
    ) -> int:
        return count_materializable_node_occurrences(
            expr,
            dag_nodes_by_identity=dag_nodes_by_identity,
            identity_for_expr=self._dag_identity_for_expr,
            node_lifecycle_class_for_identity=self._node_lifecycle_class,
            node_lifecycle_class=node_lifecycle_class,
        )

    def _materialize_shared_dag_nodes_on_sorted_df(
        self,
        sorted_df: pl.DataFrame,
        *,
        dag_nodes: Sequence[DagNode],
        reserved_names: set[str],
        stage_cache: dict[tuple, str],
        result_store: NodeResultStore,
        materialized_column_by_identity: dict[tuple, str],
        dag_nodes_by_identity: dict[tuple, DagNode],
        lifecycle_plans_by_node_id: dict[str, object],
        runtime: OrderedBatchRuntime | None,
    ) -> tuple[pl.DataFrame, dict[tuple, str]]:
        return materialize_shared_dag_nodes_on_sorted_df(
            sorted_df,
            dag_nodes=dag_nodes,
            reserved_names=reserved_names,
            stage_cache=stage_cache,
            result_store=result_store,
            materialized_column_by_identity=materialized_column_by_identity,
            dag_nodes_by_identity=dag_nodes_by_identity,
            lifecycle_plans_by_node_id=lifecycle_plans_by_node_id,
            runtime=runtime,
            lifecycle_active=is_lifecycle_active(self.lifecycle_mode),
            dag_cse_enabled=self.dag_cse_enabled,
            rewrite_expr_with_materialized_nodes=self._rewrite_expr_with_materialized_nodes,
            compile_expr=self._compile_expr,
            temporary_helper_name=self._temporary_helper_name,
            node_lifecycle_class=self._node_lifecycle_class,
        )

    def _materialized_helper_has_nested_dependency(
        self,
        *,
        result_store: NodeResultStore,
        lifecycle_plans_by_node_id: dict[str, object],
    ) -> bool:
        return materialized_helper_has_nested_dependency(
            result_store=result_store,
            lifecycle_plans_by_node_id=lifecycle_plans_by_node_id,
        )

    @staticmethod
    def _append_helper_trace_event(stats, event: str) -> None:
        append_helper_trace_event(stats, event)

    def _prepare_helper_lifecycle_metadata(
        self,
        *,
        result_store: NodeResultStore,
        runtime: OrderedBatchRuntime,
        lifecycle_plans_by_node_id: dict[str, object],
        restore_assemble_step: int,
        finalize_step: int,
        batch_end_step: int,
        output_source_columns: set[str],
    ) -> None:
        nested_dependency_present = self._materialized_helper_has_nested_dependency(
            result_store=result_store,
            lifecycle_plans_by_node_id=lifecycle_plans_by_node_id,
        )
        parent_helper_by_node_id: dict[str, str] = {}
        child_helpers_by_node_id: dict[str, list[str]] = {}
        helper_stats_by_column: dict[str, object] = {}
        for stats in result_store.stats.values():
            if stats.compute_count <= 0 or stats.helper_column_name is None:
                continue
            helper_stats_by_column[stats.helper_column_name] = stats
            lifecycle_plan = lifecycle_plans_by_node_id.get(stats.node_id)
            parent_node_id = (
                getattr(lifecycle_plan, "parent_node_id", None)
                if lifecycle_plan is not None
                else None
            )
            if parent_node_id is not None:
                parent_stats = result_store.stats.get(parent_node_id)
                if parent_stats is not None and parent_stats.helper_column_name is not None:
                    parent_helper_by_node_id[stats.node_id] = parent_stats.helper_column_name
                    child_helpers_by_node_id.setdefault(parent_node_id, []).append(
                        stats.helper_column_name
                    )
        for stats in result_store.stats.values():
            entry = result_store.get(stats.node_id)
            if stats.compute_count <= 0 or stats.helper_column_name is None:
                continue
            lifecycle_plan = lifecycle_plans_by_node_id.get(stats.node_id)
            helper_last_use_step = max(
                [
                    value
                    for value in (
                        stats.theoretical_release_step,
                        stats.last_read_step,
                        finalize_step if stats.helper_column_name in output_source_columns else None,
                    )
                    if value is not None
                ],
                default=stats.helper_column_created_step or 0,
            )
            helper_blocker_reason = ""
            if stats.helper_column_name in output_source_columns:
                helper_blocker_reason = "final_output_dependency"
            elif entry is not None and entry.materialization_kind != "shared_intermediate":
                helper_blocker_reason = (
                    "final_output_dependency"
                    if entry.materialization_kind == "final"
                    else "execution_order_uncertain"
                )
            helper_lag = max(0, batch_end_step - helper_last_use_step)
            stats.helper_last_use_step = helper_last_use_step
            stats.helper_logical_last_use_step = (
                stats.last_read_step
                if stats.last_read_step is not None
                else stats.theoretical_release_step
            )
            stats.helper_structural_dependency_end_step = max(
                [
                    value
                    for value in (
                        stats.helper_logical_last_use_step,
                        stats.theoretical_release_step,
                        (
                            getattr(
                                lifecycle_plans_by_node_id.get(
                                    getattr(lifecycle_plan, "parent_node_id", None)
                                ),
                                "last_use_step",
                                None,
                            )
                            if lifecycle_plan is not None
                            else None
                        ),
                    )
                    if value is not None
                ],
                default=helper_last_use_step,
            )
            stats.helper_logical_death_step = helper_last_use_step
            stats.helper_drop_safe_step = restore_assemble_step
            stats.helper_depth = (
                getattr(lifecycle_plan, "node_depth", 0)
                if lifecycle_plan is not None
                else 0
            )
            stats.parent_helper_column_name = parent_helper_by_node_id.get(stats.node_id)
            stats.child_helper_columns = tuple(
                sorted(child_helpers_by_node_id.get(stats.node_id, ()))
            )
            helper_lag = max(0, batch_end_step - stats.helper_structural_dependency_end_step)
            stats.helper_structural_lag_steps = helper_lag
            stats.helper_potential_bytes_step_savings = stats.helper_bytes_estimate * helper_lag
            stats.helper_drop_blocker_reason = helper_blocker_reason
            if helper_blocker_reason:
                stats.helper_lifecycle_state = (
                    "structurally_required"
                    if helper_blocker_reason
                    in {"final_output_dependency", "late_select_dependency"}
                    else "drop_blocked"
                )
            elif helper_lag > 0:
                stats.helper_lifecycle_state = "logically_dead"
            else:
                stats.helper_lifecycle_state = "active"
            first_wave_candidate = HelperFirstWaveCandidateInput(
                helper_lifecycle_state=stats.helper_lifecycle_state,
                helper_drop_blocker_reason=stats.helper_drop_blocker_reason,
                helper_structural_lag_steps=stats.helper_structural_lag_steps,
                helper_bytes_estimate=stats.helper_bytes_estimate,
                materialization_kind=stats.materialization_kind,
                materialization_eligibility=stats.materialization_eligibility,
                node_lifecycle_class=self._node_lifecycle_class(stats.identity),
                workload_name=runtime.helper_lifecycle_workload,
                nested_dependency_present=nested_dependency_present,
            )
            second_wave_candidate = HelperSecondWaveNestedCandidateInput(
                helper_lifecycle_state=stats.helper_lifecycle_state,
                helper_drop_blocker_reason=stats.helper_drop_blocker_reason,
                helper_structural_lag_steps=stats.helper_structural_lag_steps,
                helper_bytes_estimate=stats.helper_bytes_estimate,
                materialization_kind=stats.materialization_kind,
                materialization_eligibility=stats.materialization_eligibility,
                node_lifecycle_class=self._node_lifecycle_class(stats.identity),
                parent_helper_column_name=stats.parent_helper_column_name,
                child_helper_columns=stats.child_helper_columns,
                parent_child_count=(
                    len(
                        child_helpers_by_node_id.get(
                            getattr(lifecycle_plan, "parent_node_id", None),
                            (),
                        )
                    )
                    if lifecycle_plan is not None
                    and getattr(lifecycle_plan, "parent_node_id", None) is not None
                    else 0
                ),
                materialized_helper_count=len(helper_stats_by_column),
                nested_output_pinned=any(
                    helper_name in output_source_columns
                    or (
                        helper_stats_by_column[helper_name].materialization_kind
                        != "shared_intermediate"
                    )
                    for helper_name in (
                        *(stats.child_helper_columns),
                        *(
                            (stats.parent_helper_column_name,)
                            if stats.parent_helper_column_name is not None
                            else ()
                        ),
                    )
                    if helper_name in helper_stats_by_column
                ),
                helper_structural_dependency_end_step=(
                    stats.helper_structural_dependency_end_step
                ),
                helper_drop_safe_step=stats.helper_drop_safe_step,
                node_store_read_count=stats.node_store_read_count,
                reuse_consumer_count=stats.reuse_consumer_count,
            )
            is_candidate, candidate_kind, miss_reason = collect_helper_drop_candidate_kind(
                mode=runtime.helper_lifecycle_mode,
                first_wave_candidate=first_wave_candidate,
                second_wave_candidate=second_wave_candidate,
            )
            stats.helper_drop_candidate = is_candidate
            stats.helper_drop_candidate_kind = candidate_kind
            stats.nested_helper_candidate = candidate_kind == "second_wave_nested"
            stats.nested_helper_miss_reason = "" if is_candidate else miss_reason
            if candidate_kind == "second_wave_nested":
                self._append_helper_trace_event(stats, "nested_helper_candidate")
            elif runtime.helper_lifecycle_mode == "second_wave_nested":
                self._append_helper_trace_event(stats, "nested_helper_drop_missed")

    def _revalidate_helper_drop(
        self,
        *,
        stats,
        frame: pl.DataFrame,
        output_source_columns: set[str],
    ) -> tuple[bool, str]:
        return revalidate_helper_drop(
            stats=stats,
            frame=frame,
            output_source_columns=output_source_columns,
        )

    def _drop_first_wave_helper_columns(
        self,
        *,
        frame: pl.DataFrame,
        result_store: NodeResultStore,
        runtime: OrderedBatchRuntime,
        stage_cache: dict[tuple, str],
        output_source_columns: set[str],
    ) -> pl.DataFrame:
        helper_stats = [
            stats
            for stats in result_store.stats.values()
            if stats.compute_count > 0 and stats.helper_column_name is not None
        ]
        runtime.helper_peak_live_bytes_before_drop = sum(
            stats.helper_bytes_estimate for stats in helper_stats
        )
        runtime.helper_peak_live_bytes_after_drop = runtime.helper_peak_live_bytes_before_drop
        runtime.helper_frame_width_before_drop = len(frame.columns)
        runtime.helper_frame_width_after_drop = len(frame.columns)
        nested_helper_stats = [
            stats
            for stats in helper_stats
            if stats.parent_helper_column_name is not None
            or stats.child_helper_columns
            or stats.nested_helper_candidate
            or stats.nested_helper_miss_reason
        ]
        runtime.nested_helper_peak_live_bytes_before_drop = sum(
            stats.helper_bytes_estimate for stats in nested_helper_stats
        )
        runtime.nested_helper_peak_live_bytes_after_drop = (
            runtime.nested_helper_peak_live_bytes_before_drop
        )
        runtime.nested_helper_frame_width_before_drop = len(frame.columns)
        runtime.nested_helper_frame_width_after_drop = len(frame.columns)

        if not is_helper_lifecycle_active(runtime.helper_lifecycle_mode):
            for stats in helper_stats:
                if stats.parent_helper_column_name is not None or stats.child_helper_columns:
                    stats.nested_helper_miss_reason = "mode_disabled"
                    self._append_helper_trace_event(stats, "nested_helper_drop_missed")
            return frame

        drop_columns: list[str] = []
        for stats in helper_stats:
            if not stats.helper_drop_candidate:
                continue
            stats.helper_drop_revalidated = True
            allowed, miss_reason = self._revalidate_helper_drop(
                stats=stats,
                frame=frame,
                output_source_columns=output_source_columns,
            )
            if not allowed:
                stats.helper_drop_missed = True
                stats.helper_drop_miss_reason = miss_reason
                if stats.helper_drop_candidate_kind == "second_wave_nested":
                    stats.nested_helper_miss_reason = miss_reason
                    self._append_helper_trace_event(stats, "nested_helper_revalidate_fail")
                elif stats.parent_helper_column_name is not None or stats.child_helper_columns:
                    stats.nested_helper_miss_reason = miss_reason
                    self._append_helper_trace_event(stats, "nested_helper_drop_missed")
                continue
            if stats.helper_drop_candidate_kind == "second_wave_nested":
                self._append_helper_trace_event(stats, "nested_helper_revalidate_pass")
            if stats.helper_column_name is not None:
                drop_columns.append(stats.helper_column_name)

        if not drop_columns:
            runtime.helper_drop_miss_count = sum(
                1 for stats in helper_stats if stats.helper_drop_missed
            )
            runtime.nested_helper_drop_missed_count = sum(
                1
                for stats in nested_helper_stats
                if stats.helper_drop_missed or stats.nested_helper_miss_reason
            )
            return frame

        drop_set = set(drop_columns)
        for stats in helper_stats:
            if stats.helper_column_name not in drop_set:
                continue
            dropped_at_step = stats.helper_drop_safe_step
            stats.helper_dropped_at_step = dropped_at_step
            stats.helper_drop_delay_steps = (
                max(0, dropped_at_step - stats.helper_drop_safe_step)
                if dropped_at_step is not None and stats.helper_drop_safe_step is not None
                else None
            )
            stats.helper_drop_reason = "batch_safe_projection"
            stats.helper_retained_until_end = False
            if stats.helper_drop_candidate_kind == "second_wave_nested":
                self._append_helper_trace_event(stats, "nested_helper_dropped")

        for cache_key, column_name in list(stage_cache.items()):
            if column_name in drop_set:
                stage_cache.pop(cache_key, None)
        for record in runtime.registry.records.values():
            if record.column_name in drop_set:
                record.is_alive = False
                record.is_dropped = True
                record.dropped_after_planned_last_use = True

        remaining_columns = [column for column in frame.columns if column not in drop_set]
        dropped_frame = frame.select(remaining_columns)
        runtime.observe_frame(dropped_frame)

        dropped_stats = [
            stats for stats in helper_stats if stats.helper_dropped_at_step is not None
        ]
        missed_stats = [stats for stats in helper_stats if stats.helper_drop_missed]
        runtime.helper_dropped_count = len(dropped_stats)
        runtime.helper_drop_miss_count = len(missed_stats)
        runtime.helper_peak_live_bytes_after_drop = sum(
            stats.helper_bytes_estimate
            for stats in helper_stats
            if stats.helper_dropped_at_step is None
        )
        runtime.helper_frame_width_after_drop = len(dropped_frame.columns)
        helper_drop_delays = [
            stats.helper_drop_delay_steps
            for stats in dropped_stats
            if stats.helper_drop_delay_steps is not None
        ]
        runtime.helper_drop_delay_steps_avg = (
            sum(helper_drop_delays) / len(helper_drop_delays)
            if helper_drop_delays
            else 0.0
        )
        runtime.helper_drop_delay_steps_max = max(helper_drop_delays, default=0)
        runtime.helper_lifecycle_effective = helper_lifecycle_effective(
            helper_dropped_count=runtime.helper_dropped_count,
            helper_drop_miss_count=runtime.helper_drop_miss_count,
            helper_peak_live_bytes_before_drop=runtime.helper_peak_live_bytes_before_drop,
            helper_peak_live_bytes_after_drop=runtime.helper_peak_live_bytes_after_drop,
            helper_drop_delay_steps_max=runtime.helper_drop_delay_steps_max,
        )
        nested_dropped_stats = [
            stats
            for stats in nested_helper_stats
            if stats.helper_dropped_at_step is not None
            and stats.helper_drop_candidate_kind == "second_wave_nested"
        ]
        nested_missed_stats = [
            stats
            for stats in nested_helper_stats
            if stats.helper_drop_missed or stats.nested_helper_miss_reason
        ]
        runtime.nested_helper_dropped_count = len(nested_dropped_stats)
        runtime.nested_helper_drop_missed_count = len(nested_missed_stats)
        runtime.nested_helper_peak_live_bytes_after_drop = sum(
            stats.helper_bytes_estimate
            for stats in nested_helper_stats
            if stats.helper_dropped_at_step is None
        )
        runtime.nested_helper_frame_width_after_drop = len(dropped_frame.columns)
        runtime.nested_helper_lifecycle_effective = (
            runtime.helper_lifecycle_mode == "second_wave_nested"
            and runtime.nested_helper_dropped_count > 0
        )
        return dropped_frame

    def _record_result_store_profile(
        self,
        *,
        result_store: NodeResultStore,
        runtime: OrderedBatchRuntime,
        lifecycle_plans_by_node_id: dict[str, object],
        restore_assemble_step: int,
        append_step: int,
        finalize_step: int,
        batch_end_step: int,
        output_source_columns: set[str] | None = None,
    ) -> None:
        runtime.restore_assemble_step = restore_assemble_step
        runtime.append_step = append_step
        runtime.finalize_step = finalize_step
        runtime.batch_end_step = batch_end_step
        result_store.mark_drop_misses()
        runtime.result_store_peak_entry_count = result_store.peak_entry_count
        runtime.node_compute_count = sum(
            1 for item in result_store.stats.values() if item.compute_count > 0
        )
        runtime.node_hit_count = sum(1 for item in result_store.stats.values() if item.hit_count > 0)
        runtime.node_store_compute_calls = result_store.total_compute_calls()
        runtime.total_compute_calls = (
            runtime.node_store_compute_calls + runtime.compiled_output_heavy_occurrence_count
        )
        runtime.total_store_hits = result_store.total_store_hits()
        runtime.node_store_read_count = result_store.total_node_store_reads()
        runtime.reuse_consumer_count = result_store.total_reuse_consumers()
        runtime.shared_node_hit_rate = result_store.shared_hit_rate()
        runtime.node_store_compute_time_ms = result_store.total_compute_time_ms()
        runtime.compute_time_ms = runtime.node_store_compute_time_ms
        runtime.store_write_time_ms = result_store.total_store_write_time_ms()
        runtime.store_hit_time_ms = result_store.total_store_hit_time_ms()
        runtime.lifecycle_candidate_count = sum(
            1
            for plan in lifecycle_plans_by_node_id.values()
            if getattr(plan, "drop_candidate", False)
        )
        releasable_stats = [
            stats
            for stats in result_store.stats.values()
            if stats.theoretical_release_step is not None
            and stats.theoretical_release_step <= batch_end_step
        ]
        runtime.lifecycle_releasable_node_count = len(releasable_stats)
        runtime.lifecycle_peak_live_node_count = len(
            [stats for stats in result_store.stats.values() if stats.compute_count > 0]
        )
        runtime.lifecycle_peak_live_bytes_est = sum(
            stats.bytes_estimate
            for stats in result_store.stats.values()
            if stats.compute_count > 0
        )
        runtime.peak_live_bytes_est_before_drop = runtime.lifecycle_peak_live_bytes_est
        live_after_drop_stats = [
            stats
            for stats in result_store.stats.values()
            if stats.compute_count > 0 and stats.dropped_at_step is None
        ]
        runtime.peak_live_node_count_after_drop = len(live_after_drop_stats)
        runtime.peak_live_bytes_est_after_drop = sum(
            stats.bytes_estimate for stats in live_after_drop_stats
        )
        runtime.multi_node_overlap_peak = runtime.lifecycle_peak_live_node_count
        runtime.multi_node_peak_live_bytes_before = runtime.peak_live_bytes_est_before_drop
        runtime.multi_node_peak_live_bytes_after = runtime.peak_live_bytes_est_after_drop
        structural_release_lags = [
            max(0, batch_end_step - stats.theoretical_release_step)
            for stats in releasable_stats
            if stats.theoretical_release_step is not None
        ]
        finalize_retention_lags = [
            max(0, finalize_step - stats.theoretical_release_step)
            for stats in releasable_stats
            if stats.theoretical_release_step is not None
        ]
        runtime.avg_release_lag_steps = (
            sum(structural_release_lags) / len(structural_release_lags)
            if structural_release_lags
            else 0.0
        )
        runtime.max_release_lag_steps = max(structural_release_lags, default=0)
        runtime.avg_structural_release_lag_steps = runtime.avg_release_lag_steps
        runtime.max_structural_release_lag_steps = runtime.max_release_lag_steps
        runtime.avg_finalize_retention_lag_steps = (
            sum(finalize_retention_lags) / len(finalize_retention_lags)
            if finalize_retention_lags
            else 0.0
        )
        runtime.max_finalize_retention_lag_steps = max(finalize_retention_lags, default=0)

        potential_savings_by_node: dict[str, int] = {}
        l2_first_wave_candidate_by_node: dict[str, bool] = {}
        native_eligibility_by_node: dict[str, str] = {}
        native_blocker_by_node: dict[str, str] = {}
        native_rewrite_applied_by_node: dict[str, bool] = {}
        native_helper_usage_pattern_by_node: dict[str, str] = {}
        output_source_columns = output_source_columns or set()
        self._prepare_helper_lifecycle_metadata(
            result_store=result_store,
            runtime=runtime,
            lifecycle_plans_by_node_id=lifecycle_plans_by_node_id,
            restore_assemble_step=restore_assemble_step,
            finalize_step=finalize_step,
            batch_end_step=batch_end_step,
            output_source_columns=output_source_columns,
        )
        for stats in result_store.stats.values():
            lifecycle_plan = lifecycle_plans_by_node_id.get(stats.node_id)
            node_lifecycle_class = self._node_lifecycle_class(stats.identity)
            structural_lag = (
                max(0, batch_end_step - stats.theoretical_release_step)
                if stats.theoretical_release_step is not None
                else 0
            )
            potential_savings = stats.bytes_estimate * structural_lag
            potential_savings_by_node[stats.node_id] = potential_savings
            l2_first_wave_candidate_by_node[stats.node_id] = (
                is_first_wave_candidate(
                    FirstWaveCandidateInput(
                        materialization_eligibility=stats.materialization_eligibility,
                        drop_candidate=(
                            getattr(lifecycle_plan, "drop_candidate", False)
                            if lifecycle_plan is not None
                            else False
                        ),
                        drop_blocker_reason=(
                            getattr(lifecycle_plan, "drop_blocker_reason", "")
                            if lifecycle_plan is not None
                            else "missing_lifecycle_plan"
                        ),
                        structural_release_lag_steps=structural_lag,
                        node_lifecycle_class=node_lifecycle_class,
                        bytes_estimate=stats.bytes_estimate,
                    )
                )
            )
            if node_lifecycle_class == "native_heavy":
                rewrite_applied = stats.node_store_read_count > 0
                eligibility, blocker_reason = classify_native_heavy_lifecycle(
                    NativeHeavyLifecycleInput(
                        is_native_heavy=True,
                        materialized=stats.compute_count > 0,
                        rewrite_applied=rewrite_applied,
                        logical_consumer_count=stats.reuse_consumer_count,
                        effective_use_count=stats.node_store_read_count,
                    )
                )
                native_eligibility_by_node[stats.node_id] = eligibility
                native_blocker_by_node[stats.node_id] = blocker_reason
                native_rewrite_applied_by_node[stats.node_id] = rewrite_applied
                native_helper_usage_pattern_by_node[stats.node_id] = native_helper_usage_pattern(
                    logical_consumer_count=stats.reuse_consumer_count,
                    effective_use_count=stats.node_store_read_count,
                )
        runtime.potential_live_bytes_step_savings = sum(potential_savings_by_node.values())
        runtime.l2_first_wave_candidate_count = sum(l2_first_wave_candidate_by_node.values())
        native_stats = [
            stats
            for stats in result_store.stats.values()
            if self._node_lifecycle_class(stats.identity) == "native_heavy"
        ]
        runtime.native_heavy_node_count = len(native_stats)
        runtime.native_heavy_forbidden_count = sum(
            1
            for stats in native_stats
            if native_eligibility_by_node.get(stats.node_id) == "forbidden"
        )
        runtime.native_heavy_observable_only_count = sum(
            1
            for stats in native_stats
            if native_eligibility_by_node.get(stats.node_id) == "observable_only"
        )
        runtime.native_heavy_candidate_future_count = sum(
            1
            for stats in native_stats
            if native_eligibility_by_node.get(stats.node_id) == "candidate_future"
        )
        runtime.native_compute_time_ms = sum(stats.compute_time_ms for stats in native_stats)
        runtime.native_path_normalization_time_ms = sum(
            stats.store_hit_time_ms for stats in native_stats
        )
        runtime.native_storage_residency_bytes = sum(stats.bytes_estimate for stats in native_stats)
        runtime.native_node_store_read_count = sum(
            stats.node_store_read_count for stats in native_stats
        )
        runtime.native_logical_consumer_count = sum(
            stats.reuse_consumer_count for stats in native_stats
        )
        runtime.native_effective_use_count = runtime.native_node_store_read_count
        runtime.native_rewrite_applied_count = sum(
            1 for stats in native_stats if native_rewrite_applied_by_node.get(stats.node_id, False)
        )
        runtime.native_helper_usage_patterns = tuple(
            sorted(
                {
                    pattern
                    for pattern in native_helper_usage_pattern_by_node.values()
                    if pattern
                }
            )
        )
        helper_stats = [
            stats
            for stats in result_store.stats.values()
            if stats.compute_count > 0 and stats.helper_column_name is not None
        ]
        runtime.helper_column_count = len(helper_stats)
        runtime.helper_releasable_count = sum(
            1
            for stats in helper_stats
            if stats.helper_lifecycle_state == "logically_dead"
            and stats.helper_drop_blocker_reason == ""
        )
        runtime.helper_blocked_count = sum(
            1 for stats in helper_stats if stats.helper_drop_blocker_reason
        )
        runtime.helper_peak_live_bytes = sum(stats.helper_bytes_estimate for stats in helper_stats)
        runtime.helper_potential_savings = sum(
            stats.helper_potential_bytes_step_savings for stats in helper_stats
        )
        runtime.helper_blocker_reasons = tuple(
            sorted(
                {
                    stats.helper_drop_blocker_reason
                    for stats in helper_stats
                    if stats.helper_drop_blocker_reason
                }
            )
        )
        if runtime.helper_peak_live_bytes_before_drop == 0:
            runtime.helper_peak_live_bytes_before_drop = runtime.helper_peak_live_bytes
            runtime.helper_peak_live_bytes_after_drop = runtime.helper_peak_live_bytes
        if runtime.helper_frame_width_before_drop == 0:
            runtime.helper_frame_width_before_drop = runtime.peak_frame_col_count
            runtime.helper_frame_width_after_drop = runtime.peak_frame_col_count
        helper_dropped_stats = [
            stats for stats in helper_stats if stats.helper_dropped_at_step is not None
        ]
        helper_missed_stats = [stats for stats in helper_stats if stats.helper_drop_missed]
        runtime.helper_dropped_count = len(helper_dropped_stats)
        runtime.helper_drop_miss_count = len(helper_missed_stats)
        if helper_dropped_stats or helper_missed_stats:
            runtime.helper_peak_live_bytes_after_drop = sum(
                stats.helper_bytes_estimate
                for stats in helper_stats
                if stats.helper_dropped_at_step is None
            )
            helper_drop_delays = [
                stats.helper_drop_delay_steps
                for stats in helper_dropped_stats
                if stats.helper_drop_delay_steps is not None
            ]
            runtime.helper_drop_delay_steps_avg = (
                sum(helper_drop_delays) / len(helper_drop_delays)
                if helper_drop_delays
                else 0.0
            )
            runtime.helper_drop_delay_steps_max = max(helper_drop_delays, default=0)
            runtime.helper_lifecycle_effective = helper_lifecycle_effective(
                helper_dropped_count=runtime.helper_dropped_count,
                helper_drop_miss_count=runtime.helper_drop_miss_count,
                helper_peak_live_bytes_before_drop=runtime.helper_peak_live_bytes_before_drop,
                helper_peak_live_bytes_after_drop=runtime.helper_peak_live_bytes_after_drop,
                helper_drop_delay_steps_max=runtime.helper_drop_delay_steps_max,
            )
        nested_helper_stats = [
            stats
            for stats in helper_stats
            if stats.parent_helper_column_name is not None
            or stats.child_helper_columns
            or stats.nested_helper_candidate
            or stats.nested_helper_miss_reason
        ]
        if runtime.nested_helper_peak_live_bytes_before_drop == 0:
            runtime.nested_helper_peak_live_bytes_before_drop = sum(
                stats.helper_bytes_estimate for stats in nested_helper_stats
            )
            runtime.nested_helper_peak_live_bytes_after_drop = (
                runtime.nested_helper_peak_live_bytes_before_drop
            )
        if runtime.nested_helper_frame_width_before_drop == 0:
            runtime.nested_helper_frame_width_before_drop = runtime.helper_frame_width_before_drop
            runtime.nested_helper_frame_width_after_drop = runtime.helper_frame_width_after_drop
        nested_dropped_stats = [
            stats
            for stats in nested_helper_stats
            if stats.helper_dropped_at_step is not None
            and stats.helper_drop_candidate_kind == "second_wave_nested"
        ]
        nested_missed_stats = [
            stats
            for stats in nested_helper_stats
            if stats.helper_drop_missed or stats.nested_helper_miss_reason
        ]
        runtime.nested_helper_dropped_count = len(nested_dropped_stats)
        runtime.nested_helper_drop_missed_count = len(nested_missed_stats)
        if nested_dropped_stats or nested_missed_stats:
            runtime.nested_helper_peak_live_bytes_after_drop = sum(
                stats.helper_bytes_estimate
                for stats in nested_helper_stats
                if stats.helper_dropped_at_step is None
            )
            runtime.nested_helper_lifecycle_effective = (
                runtime.helper_lifecycle_mode == "second_wave_nested"
                and runtime.nested_helper_dropped_count > 0
            )
        dropped_stats = [
            stats for stats in result_store.stats.values() if stats.dropped_at_step is not None
        ]
        missed_stats = [stats for stats in result_store.stats.values() if stats.drop_missed]
        runtime.dropped_node_count = len(dropped_stats)
        runtime.drop_hit_count = len(dropped_stats)
        runtime.drop_miss_count = len(missed_stats)
        drop_delays = [
            stats.drop_delay_steps
            for stats in dropped_stats
            if stats.drop_delay_steps is not None
        ]
        runtime.drop_delay_steps_avg = (
            sum(drop_delays) / len(drop_delays) if drop_delays else 0.0
        )
        runtime.drop_delay_steps_max = max(drop_delays, default=0)
        runtime.per_node_drop_order = tuple(
            stats.node_id
            for stats in sorted(
                dropped_stats,
                key=lambda item: (
                    item.dropped_at_step if item.dropped_at_step is not None else 10**12,
                    item.node_id,
                ),
            )
        )
        runtime.nested_drop_order_valid = self._nested_drop_order_valid(
            result_store=result_store,
            lifecycle_plans_by_node_id=lifecycle_plans_by_node_id,
        )
        runtime.partial_reuse_safety_flag = all(
            (
                stats.dropped_at_step is None
                or (
                    stats.last_read_step is not None
                    and stats.dropped_at_step >= stats.last_read_step
                    and stats.ref_count_remaining == 0
                )
            )
            for stats in result_store.stats.values()
        ) and not runtime.drop_miss_count
        runtime.lifecycle_effective = lifecycle_effective(
            dropped_node_count=runtime.dropped_node_count,
            drop_miss_count=runtime.drop_miss_count,
            peak_live_bytes_est_before_drop=runtime.peak_live_bytes_est_before_drop,
            peak_live_bytes_est_after_drop=runtime.peak_live_bytes_est_after_drop,
            drop_delay_steps_max=runtime.drop_delay_steps_max,
        )
        self._assert_lifecycle_step_model(
            result_store=result_store,
            lifecycle_plans_by_node_id=lifecycle_plans_by_node_id,
            restore_assemble_step=restore_assemble_step,
            append_step=append_step,
            finalize_step=finalize_step,
            batch_end_step=batch_end_step,
            nested_drop_order_valid=runtime.nested_drop_order_valid,
        )

        if runtime.profiler is None:
            return
        for stats in result_store.stats.values():
            node_lifecycle_class = self._node_lifecycle_class(stats.identity)
            if (
                stats.compute_count == 0
                and stats.hit_count == 0
                and node_lifecycle_class != "native_heavy"
            ):
                continue
            lifecycle_plan = lifecycle_plans_by_node_id.get(stats.node_id)
            structural_release_lag = (
                max(0, batch_end_step - stats.theoretical_release_step)
                if stats.theoretical_release_step is not None
                else None
            )
            finalize_retention_lag = (
                max(0, finalize_step - stats.theoretical_release_step)
                if stats.theoretical_release_step is not None
                else None
            )
            retained_past_last_read = (
                stats.retained_until_end
                and stats.last_read_step is not None
                and batch_end_step > stats.last_read_step
            )
            runtime.profiler.add_node_execution(
                NodeExecutionDetail(
                    node_id=stats.node_id,
                    batch_id=runtime.batch_id,
                    lifecycle_mode=runtime.lifecycle_mode,
                    identity=repr(stats.identity),
                    materialization_kind=stats.materialization_kind,
                    materialization_reason=stats.materialization_reason,
                    materialization_eligibility=stats.materialization_eligibility,
                    node_lifecycle_class=node_lifecycle_class,
                    consumer_count=stats.consumer_count,
                    reuse_consumer_count=stats.reuse_consumer_count,
                    compute_count=stats.compute_count,
                    node_store_read_count=stats.node_store_read_count,
                    hit_count=stats.hit_count,
                    compute_time_ms=stats.compute_time_ms,
                    store_write_time_ms=stats.store_write_time_ms,
                    store_hit_time_ms=stats.store_hit_time_ms,
                    planner_producer_step=(
                        getattr(lifecycle_plan, "producer_step", None)
                        if lifecycle_plan is not None
                        else None
                    ),
                    planner_consumer_steps=(
                        getattr(lifecycle_plan, "consumer_steps", ())
                        if lifecycle_plan is not None
                        else ()
                    ),
                    planner_last_use_step=(
                        getattr(lifecycle_plan, "last_use_step", None)
                        if lifecycle_plan is not None
                        else None
                    ),
                    planner_ref_count_initial=(
                        getattr(lifecycle_plan, "ref_count_initial", 0)
                        if lifecycle_plan is not None
                        else 0
                    ),
                    planner_drop_candidate=(
                        getattr(lifecycle_plan, "drop_candidate", False)
                        if lifecycle_plan is not None
                        else False
                    ),
                    planner_drop_blocker_reason=(
                        getattr(lifecycle_plan, "drop_blocker_reason", "")
                        if lifecycle_plan is not None
                        else ""
                    ),
                    materialized_at_step=stats.materialized_at_step,
                    first_read_step=stats.first_read_step,
                    last_read_step=stats.last_read_step,
                    retained_until_end=stats.retained_until_end,
                    theoretical_release_step=stats.theoretical_release_step,
                    release_lag_steps=structural_release_lag,
                    restore_assemble_step=restore_assemble_step,
                    append_step=append_step,
                    finalize_step=finalize_step,
                    batch_end_step=batch_end_step,
                    structural_release_lag_steps=structural_release_lag,
                    retained_past_last_read=retained_past_last_read,
                    finalize_retention_lag_steps=finalize_retention_lag,
                    potential_live_bytes_step_savings=potential_savings_by_node.get(
                        stats.node_id,
                        0,
                    ),
                    l2_first_wave_candidate=l2_first_wave_candidate_by_node.get(
                        stats.node_id,
                        False,
                    ),
                    active_drop_eligible=stats.active_drop_eligible,
                    dropped_at_step=stats.dropped_at_step,
                    drop_expected_step=stats.drop_expected_step,
                    drop_delay_steps=stats.drop_delay_steps,
                    drop_reason=stats.drop_reason,
                    ref_count_remaining_final=stats.ref_count_remaining,
                    drop_missed=stats.drop_missed,
                    drop_miss_reason=stats.drop_miss_reason,
                    node_depth=(
                        getattr(lifecycle_plan, "node_depth", 0)
                        if lifecycle_plan is not None
                        else 0
                    ),
                    parent_node_id=(
                        getattr(lifecycle_plan, "parent_node_id", None)
                        if lifecycle_plan is not None
                        else None
                    ),
                    dependency_chain=(
                        getattr(lifecycle_plan, "dependency_chain", ())
                        if lifecycle_plan is not None
                        else ()
                    ),
                    bytes_estimate=stats.bytes_estimate,
                    native_heavy_lifecycle_eligibility=native_eligibility_by_node.get(
                        stats.node_id,
                        "",
                    ),
                    native_heavy_blocker_reason=native_blocker_by_node.get(
                        stats.node_id,
                        "",
                    ),
                    native_compute_time_ms=(
                        stats.compute_time_ms if node_lifecycle_class == "native_heavy" else 0.0
                    ),
                    native_path_normalization_time_ms=(
                        stats.store_hit_time_ms if node_lifecycle_class == "native_heavy" else 0.0
                    ),
                    native_storage_residency_bytes=(
                        stats.bytes_estimate if node_lifecycle_class == "native_heavy" else 0
                    ),
                    native_node_store_read_count=(
                        stats.node_store_read_count if node_lifecycle_class == "native_heavy" else 0
                    ),
                    native_logical_consumer_count=(
                        stats.reuse_consumer_count if node_lifecycle_class == "native_heavy" else 0
                    ),
                    native_effective_use_count=(
                        stats.node_store_read_count if node_lifecycle_class == "native_heavy" else 0
                    ),
                    native_fallback_eval_count=(
                        runtime.native_fallback_eval_count
                        if node_lifecycle_class == "native_heavy"
                        and stats.node_store_read_count == 0
                        else 0
                    ),
                    native_rewrite_applied=native_rewrite_applied_by_node.get(
                        stats.node_id,
                        False,
                    ),
                    native_helper_usage_pattern=native_helper_usage_pattern_by_node.get(
                        stats.node_id,
                        "",
                    ),
                    helper_column_name=stats.helper_column_name,
                    helper_column_created_step=stats.helper_column_created_step,
                    helper_last_use_step=stats.helper_last_use_step,
                    helper_retained_until_end=stats.helper_retained_until_end,
                    helper_structural_lag_steps=stats.helper_structural_lag_steps,
                    helper_bytes_estimate=stats.helper_bytes_estimate,
                    helper_potential_bytes_step_savings=(
                        stats.helper_potential_bytes_step_savings
                    ),
                    helper_lifecycle_state=stats.helper_lifecycle_state,
                    helper_drop_blocker_reason=stats.helper_drop_blocker_reason,
                    helper_depth=stats.helper_depth,
                    parent_helper_column_name=stats.parent_helper_column_name,
                    child_helper_columns=stats.child_helper_columns,
                    helper_logical_last_use_step=stats.helper_logical_last_use_step,
                    helper_structural_dependency_end_step=(
                        stats.helper_structural_dependency_end_step
                    ),
                    helper_drop_candidate=stats.helper_drop_candidate,
                    helper_drop_candidate_kind=stats.helper_drop_candidate_kind,
                    helper_logical_death_step=stats.helper_logical_death_step,
                    helper_drop_safe_step=stats.helper_drop_safe_step,
                    helper_drop_revalidated=stats.helper_drop_revalidated,
                    helper_dropped_at_step=stats.helper_dropped_at_step,
                    helper_drop_delay_steps=stats.helper_drop_delay_steps,
                    helper_drop_reason=stats.helper_drop_reason,
                    helper_drop_missed=stats.helper_drop_missed,
                    helper_drop_miss_reason=stats.helper_drop_miss_reason,
                    nested_helper_candidate=stats.nested_helper_candidate,
                    nested_helper_trace_events=stats.nested_helper_trace_events,
                    nested_helper_miss_reason=stats.nested_helper_miss_reason,
                    recomputation_expansion_if_inline=(
                        stats.recomputation_expansion_if_inline
                    ),
                    recomputation_guardrail_pass=stats.recomputation_guardrail_pass,
                )
            )

    @staticmethod
    def _nested_drop_order_valid(
        *,
        result_store: NodeResultStore,
        lifecycle_plans_by_node_id: dict[str, object],
    ) -> bool:
        return nested_drop_order_valid(
            result_store=result_store,
            lifecycle_plans_by_node_id=lifecycle_plans_by_node_id,
        )

    def _assert_lifecycle_step_model(
        self,
        *,
        result_store: NodeResultStore,
        lifecycle_plans_by_node_id: dict[str, object],
        restore_assemble_step: int,
        append_step: int,
        finalize_step: int,
        batch_end_step: int,
        nested_drop_order_valid: bool,
    ) -> None:
        assert_lifecycle_step_model(
            result_store=result_store,
            lifecycle_plans_by_node_id=lifecycle_plans_by_node_id,
            restore_assemble_step=restore_assemble_step,
            append_step=append_step,
            finalize_step=finalize_step,
            batch_end_step=batch_end_step,
            nested_drop_order_valid=nested_drop_order_valid,
            lifecycle_mode=self.lifecycle_mode,
        )

    @staticmethod
    def _node_lifecycle_class(identity: tuple) -> str:
        if len(identity) >= 2 and identity[0] == "call":
            function_name = identity[1]
            if function_name in {"argmax", "argmin"}:
                return "native_heavy"
            if len(identity) >= 3:
                route_sensitive = identity[2]
                if isinstance(route_sensitive, tuple) and len(route_sensitive) >= 4:
                    execution_kind = route_sensitive[1]
                    window_kind = route_sensitive[2]
                    if window_kind in {"rolling", "positional", "segmented"}:
                        return "shared_heavy"
                    if execution_kind in {"time_series", "cross_sectional"}:
                        return "ordered"
        return "other"

    def _project_frame_for_output_expressions(
        self,
        frame: pl.DataFrame,
        *,
        row_index_name: str,
        output_expressions: list[tuple[str, pl.Expr]],
    ) -> pl.DataFrame:
        if self.frame_projection_mode != "dependency_driven":
            return frame
        required_columns: set[str] = {row_index_name}
        try:
            for _output_name, expr in output_expressions:
                required_columns.update(str(name) for name in expr.meta.root_names())
        except Exception:
            # Projection is an optimization boundary. If root discovery is not
            # available for a future expression type, keep the full frame.
            return frame

        frame_columns = set(frame.columns)
        if not required_columns <= frame_columns:
            return frame
        projected_columns = [column for column in frame.columns if column in required_columns]
        if len(projected_columns) == len(frame.columns):
            return frame
        return frame.select(projected_columns)

    def _evaluate_many_ordered_batch_plan(
        self,
        batch_plan: BatchExecutionPlan,
        *,
        compiled_time_items: list[tuple[str, Expr, ValidationResult, pl.Expr]],
    ) -> pl.DataFrame:
        if (
            not compiled_time_items
            and not batch_plan.staged_items
            and not batch_plan.materialized_ordered_items
            and not batch_plan.positional_items
        ):
            return self.df

        batch_started_at = time.perf_counter()
        rss_before = current_rss_mb()
        prepare_started_at = time.perf_counter()
        prepared = self._get_prepared_frame()
        prepare_sort_time_ms = (time.perf_counter() - prepare_started_at) * 1000
        sorted_df = prepared.sorted_df
        reserved_names = set(sorted_df.columns)
        stage_cache: dict[tuple, str] = {}
        output_names: list[str] = []
        output_expressions: list[tuple[str, pl.Expr]] = []
        output_source_columns: set[str] = set()
        dag_context = initialize_dag_execution_context(batch_plan.dag)
        result_store = dag_context.result_store
        dag_nodes_by_output = dag_context.dag_nodes_by_output
        dag_identity_by_node_id = dag_context.dag_identity_by_node_id
        dag_nodes_by_identity = dag_context.dag_nodes_by_identity
        lifecycle_plans_by_node_id = dag_context.lifecycle_plans_by_node_id
        lifecycle_read_cursor_by_node_id = dag_context.lifecycle_read_cursor_by_node_id
        materialized_column_by_identity = dag_context.materialized_column_by_identity
        planned_stage_consumers = self._plan_ordered_batch_stage_consumers(batch_plan)
        runtime: OrderedBatchRuntime | None = None
        if (
            self.profile_recorder is not None
            or is_lifecycle_active(self.lifecycle_mode)
            or is_helper_lifecycle_active(self.helper_lifecycle_mode)
        ):
            batch_index = len(self.profile_recorder.batches) + 1 if self.profile_recorder else 1
            batch_id = (
                f"{self.profile_recorder.run_id}:batch:{batch_index}"
                if self.profile_recorder is not None
                else f"batch:{batch_index}"
            )
            runtime = OrderedBatchRuntime(
                batch_id=batch_id,
                profiler=self.profile_recorder,
                registry=StageRegistry(batch_id=batch_id, profiler=self.profile_recorder),
                lifecycle_mode=self.lifecycle_mode,
                helper_lifecycle_mode=self.helper_lifecycle_mode,
                helper_lifecycle_workload=self.helper_lifecycle_workload,
                expression_count=(
                    len(compiled_time_items)
                    + len(batch_plan.staged_items)
                    + len(batch_plan.materialized_ordered_items)
                    + len(batch_plan.positional_items)
                ),
                rows=sorted_df.height,
                groups=sorted_df.get_column(self.code_col).n_unique(),
                batch_started_at=batch_started_at,
                rss_before_mb=rss_before,
                base_frame_col_count=len(sorted_df.columns),
                prepare_sort_time_ms=prepare_sort_time_ms,
                peak_frame_col_count=len(sorted_df.columns),
                peak_rss_mb=rss_before,
                planned_stage_consumers=planned_stage_consumers,
            )
            if batch_plan.dag is not None:
                apply_dag_materialization_runtime_summary(runtime, batch_plan.dag)

        if compiled_time_items:
            if runtime is not None:
                for output_name, _expr, _validation, _compiled in compiled_time_items:
                    runtime.register_output_created(
                        output_name,
                        source_column_name=None,
                        frame=sorted_df,
                    )

        stage_started_at = time.perf_counter()
        if self.dag_cse_enabled and batch_plan.dag is not None and compiled_time_items:
            sorted_df, stage_cache = self._materialize_shared_dag_nodes_on_sorted_df(
                sorted_df,
                dag_nodes=batch_plan.dag.nodes,
                reserved_names=reserved_names,
                stage_cache=stage_cache,
                result_store=result_store,
                materialized_column_by_identity=materialized_column_by_identity,
                dag_nodes_by_identity=dag_nodes_by_identity,
                lifecycle_plans_by_node_id=lifecycle_plans_by_node_id,
                runtime=runtime,
            )

        if compiled_time_items:
            for output_name, expr, _validation, compiled in compiled_time_items:
                output_expr = compiled
                executed_expr = expr
                if self.dag_cse_enabled and materialized_column_by_identity:
                    rewritten_expr, hits = self._rewrite_expr_with_materialized_nodes(
                        expr,
                        materialized_column_by_identity=materialized_column_by_identity,
                        dag_nodes_by_identity=dag_nodes_by_identity,
                    )
                    for node_id, count in hits.items():
                        lifecycle_plan = lifecycle_plans_by_node_id.get(node_id)
                        consumer_steps = (
                            getattr(lifecycle_plan, "consumer_steps", ())
                            if lifecycle_plan is not None
                            else ()
                        )
                        cursor = lifecycle_read_cursor_by_node_id.get(node_id, 0)
                        planned_steps = consumer_steps[cursor : cursor + count]
                        read_step = (
                            max(planned_steps)
                            if planned_steps
                            else (
                                consumer_steps[min(cursor, len(consumer_steps) - 1)]
                                if consumer_steps
                                else None
                            )
                        )
                        lifecycle_read_cursor_by_node_id[node_id] = cursor + max(count, 1)
                        result_store.record_reads(
                            node_id,
                            read_count=count,
                            consumer_count=1,
                            read_step=read_step,
                        )
                        result_store.record_planned_consumption(
                            node_id,
                            step=read_step,
                            multiplicity=len(planned_steps) if planned_steps else count,
                            active_drop_enabled=is_lifecycle_active(self.lifecycle_mode),
                        )
                    output_expr = self._compile_expr(rewritten_expr)
                    executed_expr = rewritten_expr

                if batch_plan.dag is not None:
                    heavy_occurrence_count = self._count_materializable_node_occurrences(
                        executed_expr,
                        dag_nodes_by_identity=dag_nodes_by_identity,
                    )
                    native_heavy_occurrence_count = self._count_materializable_node_occurrences(
                        executed_expr,
                        dag_nodes_by_identity=dag_nodes_by_identity,
                        node_lifecycle_class="native_heavy",
                    )
                    runtime_heavy_count = heavy_occurrence_count if runtime is not None else 0
                    if runtime is not None:
                        runtime.compiled_output_heavy_occurrence_count += runtime_heavy_count
                        if heavy_occurrence_count > 0:
                            runtime.compiled_fallback_eval_count += 1
                        if native_heavy_occurrence_count > 0:
                            runtime.native_fallback_eval_count += 1

                output_names.append(output_name)
                output_expressions.append((output_name, output_expr))
                node_id = dag_nodes_by_output.get(output_name, f"compiled_time_output:{output_name}")
                result_store.put(
                    NodeResultStoreEntry(
                        node_id=node_id,
                        identity=dag_identity_by_node_id.get(node_id, ("compiled_time_output", output_name)),
                        materialization_kind="final",
                        materialization_reason="none",
                        output_name=output_name,
                        is_final_output=True,
                    )
                )

        for item in batch_plan.positional_items:
            sorted_df, final_stage_name, stage_cache = self._materialize_positional_call_on_sorted_df(
                sorted_df,
                expr=item.expr,
                reserved_names=reserved_names,
                stage_cache=stage_cache,
                runtime=runtime,
                output_name=item.output_name,
            )
            if runtime is not None:
                runtime.consume_stage(
                    final_stage_name,
                    consumer_kind="deferred_output",
                    frame=sorted_df,
                )
                runtime.register_output_created(
                    item.output_name,
                    source_column_name=final_stage_name,
                    frame=sorted_df,
                )
            output_names.append(item.output_name)
            output_expressions.append((item.output_name, pl.col(final_stage_name)))
            output_source_columns.add(final_stage_name)
            node_id = dag_nodes_by_output.get(item.output_name, f"output:{item.output_name}")
            result_store.put(
                NodeResultStoreEntry(
                    node_id=node_id,
                    identity=dag_identity_by_node_id.get(node_id, ("output", item.output_name)),
                    materialization_kind="final",
                    output_name=item.output_name,
                    column_name=final_stage_name,
                    is_final_output=True,
                )
            )
            if runtime is not None:
                runtime.observe_frame(sorted_df)
                sorted_df = runtime.sweep(
                    sorted_df,
                    stage_cache=stage_cache,
                    output_names=output_source_columns | set(materialized_column_by_identity.values()),
                )

        for item in batch_plan.materialized_ordered_items:
            if item.plan.materialized_ordered is None:
                raise ExecutionError(
                    "Internal error: materialized ordered batch item is missing plan specification"
                )
            sorted_df, final_stage_name, stage_cache = self._materialize_ordered_plan_on_sorted_df(
                sorted_df,
                materialized_plan=item.plan.materialized_ordered,
                reserved_names=reserved_names,
                stage_cache=stage_cache,
                runtime=runtime,
                output_name=item.output_name,
            )
            if runtime is not None:
                runtime.consume_stage(
                    final_stage_name,
                    consumer_kind="deferred_output",
                    frame=sorted_df,
                )
                runtime.register_output_created(
                    item.output_name,
                    source_column_name=final_stage_name,
                    frame=sorted_df,
                )
            output_names.append(item.output_name)
            output_expressions.append((item.output_name, pl.col(final_stage_name)))
            output_source_columns.add(final_stage_name)
            node_id = dag_nodes_by_output.get(item.output_name, f"output:{item.output_name}")
            result_store.put(
                NodeResultStoreEntry(
                    node_id=node_id,
                    identity=dag_identity_by_node_id.get(node_id, ("output", item.output_name)),
                    materialization_kind="final",
                    output_name=item.output_name,
                    column_name=final_stage_name,
                    is_final_output=True,
                )
            )
            if runtime is not None:
                runtime.observe_frame(sorted_df)
                sorted_df = runtime.sweep(
                    sorted_df,
                    stage_cache=stage_cache,
                    output_names=output_source_columns | set(materialized_column_by_identity.values()),
                )

        for staged_node in batch_plan.staged_nodes:
            stage_name = stage_cache.get(staged_node.cache_key)
            if stage_name is not None:
                continue

            stage_name = self._temporary_helper_name("__stage_value", reserved=reserved_names)
            if staged_node.kind == "source":
                if staged_node.expr is None:
                    raise ExecutionError("Internal error: staged source node is missing expression")
                sorted_df = sorted_df.with_columns(self._compile_expr(staged_node.expr).alias(stage_name))
            else:
                if staged_node.depends_on_cache_key is None or staged_node.step is None:
                    raise ExecutionError("Internal error: staged prefix node is missing dependency data")
                input_stage_name = stage_cache[staged_node.depends_on_cache_key]
                if runtime is not None:
                    runtime.consume_stage(input_stage_name, consumer_kind="staged_prefix", frame=sorted_df)
                sorted_df = sorted_df.with_columns(
                    self._build_staged_cross_section_expr(
                        staged_node.step,
                        stage_name=input_stage_name,
                    ).alias(stage_name)
                )

            reserved_names.add(stage_name)
            stage_cache[staged_node.cache_key] = stage_name
            if runtime is not None:
                runtime.register_stage(
                    expr_key=staged_node.cache_key,
                    column_name=stage_name,
                    stage_kind="staged_prefix" if staged_node.kind == "prefix" else "ordered_helper",
                    producer_route="staged",
                    frame=sorted_df,
                    cache_key=staged_node.cache_key,
                )

        for binding in batch_plan.staged_output_bindings:
            source_column = stage_cache[binding.cache_key]
            if runtime is not None:
                runtime.consume_stage(
                    source_column,
                    consumer_kind="deferred_output",
                    frame=sorted_df,
                )
                runtime.register_output_created(
                    binding.output_name,
                    source_column_name=source_column,
                    frame=sorted_df,
                )
            output_names.append(binding.output_name)
            output_expressions.append((binding.output_name, pl.col(source_column)))
            output_source_columns.add(source_column)
            node_id = dag_nodes_by_output.get(binding.output_name, f"output:{binding.output_name}")
            result_store.put(
                NodeResultStoreEntry(
                    node_id=node_id,
                    identity=dag_identity_by_node_id.get(node_id, ("output", binding.output_name)),
                    materialization_kind="final",
                    output_name=binding.output_name,
                    column_name=source_column,
                    is_final_output=True,
                )
            )
            if runtime is not None:
                runtime.observe_frame(sorted_df)

        if runtime is not None:
            runtime.stage_materialize_time_ms = (time.perf_counter() - stage_started_at) * 1000
            sorted_df = runtime.sweep(
                sorted_df,
                stage_cache=stage_cache,
                output_names=output_source_columns | set(materialized_column_by_identity.values()),
            )

        prepared.sorted_df = sorted_df
        restore_assemble_step = 0
        append_step = 0
        finalize_step = 0
        batch_end_step = 0
        ordered_outputs_with_row: pl.DataFrame | None = None
        sorted_df = self._project_frame_for_output_expressions(
            sorted_df,
            row_index_name=prepared.row_index_name,
            output_expressions=output_expressions,
        )
        if runtime is not None:
            runtime.observe_frame(sorted_df)
        if self.output_attach_mode in {"finalize_select", "last_use_select"}:
            compiled_eval_started_at = time.perf_counter()
            ordered_outputs_with_row = sorted_df.select(
                [
                    prepared.row_index_name,
                    *[expr.alias(output_name) for output_name, expr in output_expressions],
                ]
            )
            if runtime is not None:
                runtime.compiled_output_eval_time_ms = (
                    time.perf_counter() - compiled_eval_started_at
                ) * 1000
                runtime.observe_frame(sorted_df)
        else:
            compiled_eval_started_at = time.perf_counter()
            sorted_df = sorted_df.with_columns(
                [expr.alias(output_name) for output_name, expr in output_expressions]
            )
            if runtime is not None:
                runtime.compiled_output_eval_time_ms = (
                    time.perf_counter() - compiled_eval_started_at
                ) * 1000
                runtime.observe_frame(sorted_df)
        if runtime is not None:
            last_consumer_step = max(
                (
                    step
                    for plan in lifecycle_plans_by_node_id.values()
                    for step in getattr(plan, "consumer_steps", ())
                ),
                default=0,
            )
            restore_assemble_step = last_consumer_step + 1
            append_step = restore_assemble_step + 1
            finalize_step = append_step + 1
            batch_end_step = finalize_step + 1
            self._prepare_helper_lifecycle_metadata(
                result_store=result_store,
                runtime=runtime,
                lifecycle_plans_by_node_id=lifecycle_plans_by_node_id,
                restore_assemble_step=restore_assemble_step,
                finalize_step=finalize_step,
                batch_end_step=batch_end_step,
                output_source_columns=output_source_columns,
            )
            sorted_df = self._drop_first_wave_helper_columns(
                frame=sorted_df,
                result_store=result_store,
                runtime=runtime,
                stage_cache=stage_cache,
                output_source_columns=output_source_columns,
            )
        prepared.sorted_df = sorted_df
        restore_started_at = time.perf_counter()
        if ordered_outputs_with_row is not None:
            ordered_outputs = restore_selected_columns(
                ordered_outputs_with_row,
                prepared.row_index_name,
                output_names,
            )
        else:
            ordered_outputs = prepared.restore_output_columns(output_names)
        if runtime is not None:
            runtime.restore_assemble_time_ms = (time.perf_counter() - restore_started_at) * 1000
            runtime.restore_time_ms = runtime.restore_assemble_time_ms
            sorted_df = runtime.sweep(
                sorted_df,
                stage_cache=stage_cache,
                output_names=set(),
            )
        temporary_output_names = [
            output_name
            for output_name in output_names
            if output_name not in self.df.columns and output_name in sorted_df.columns
        ]
        if temporary_output_names:
            sorted_df = sorted_df.drop(temporary_output_names)
            if runtime is not None:
                runtime.observe_frame(sorted_df)
        append_started_at = time.perf_counter()
        result = append_ordered_output_columns(self.df, ordered_outputs, output_names)
        if runtime is not None:
            runtime.append_time_ms = (time.perf_counter() - append_started_at) * 1000
            self._record_result_store_profile(
                result_store=result_store,
                runtime=runtime,
                lifecycle_plans_by_node_id=lifecycle_plans_by_node_id,
                restore_assemble_step=restore_assemble_step,
                append_step=append_step,
                finalize_step=finalize_step,
                batch_end_step=batch_end_step,
                output_source_columns=output_source_columns,
            )
            for output_name in output_names:
                runtime.mark_output_attached(
                    output_name,
                    frame=result,
                    attached_to_working_frame=False,
                )
            runtime.finish(
                frame=sorted_df,
                output_names=set(output_names),
                output_source_columns=output_source_columns,
            )
        return result

    def _evaluate_materialized_ordered_column(
        self,
        materialized_plan: MaterializedOrderedPlan,
        *,
        output_name: str,
    ) -> pl.DataFrame:
        prepared = self._get_prepared_frame()
        return evaluate_materialized_ordered_column(
            prepared,
            self.df,
            output_name=output_name,
            materialize_ordered_plan=lambda sorted_df: self._materialize_ordered_plan_on_sorted_df(
                sorted_df,
                materialized_plan=materialized_plan,
                reserved_names=set(sorted_df.columns),
                stage_cache={},
            ),
        )

    def _evaluate_positional_ordered_column(
        self,
        expr: Expr,
        *,
        output_name: str,
    ) -> pl.DataFrame:
        prepared = self._get_prepared_frame()
        return evaluate_positional_ordered_column(
            prepared,
            self.df,
            expr,
            output_name=output_name,
            materialize_positional_call=lambda sorted_df: self._materialize_positional_call_on_sorted_df(
                sorted_df,
                expr=expr,
                reserved_names=set(sorted_df.columns),
                stage_cache={},
            ),
        )

    def _materialize_positional_call_on_sorted_df(
        self,
        sorted_df: pl.DataFrame,
        *,
        expr: Expr,
        reserved_names: set[str],
        stage_cache: dict[tuple, str],
        runtime: OrderedBatchRuntime | None = None,
        output_name: str | None = None,
    ) -> tuple[pl.DataFrame, str, dict[tuple, str]]:
        return materialize_positional_call_on_sorted_df(
            sorted_df,
            expr=expr,
            reserved_names=reserved_names,
            stage_cache=stage_cache,
            runtime=runtime,
            output_name=output_name,
            expect_positive_numeric_literal=self._expect_positive_numeric_literal,
            expr_key=self._planner.expr_key,
            materialize_expr_on_sorted_df=self._materialize_expr_on_sorted_df,
            temporary_helper_name=self._temporary_helper_name,
            attach_positional_kernel_from_stage=self._attach_positional_kernel_from_stage,
        )

    def _attach_positional_kernel_from_stage(
        self,
        sorted_df: pl.DataFrame,
        *,
        value_stage_name: str,
        result_stage_name: str,
        window: int,
        mode: Literal["argmax", "argmin"],
        runtime: OrderedBatchRuntime | None = None,
        expression: str = "",
        output_name: str = "",
        child_expr_time_ms: float = 0.0,
    ) -> pl.DataFrame:
        return attach_positional_kernel_from_stage(
            sorted_df,
            value_stage_name=value_stage_name,
            result_stage_name=result_stage_name,
            window=window,
            mode=mode,
            code_col=self.code_col,
            evaluate_positional_kernel=self._evaluate_positional_kernel,
            current_rss_mb=current_rss_mb,
            runtime=runtime,
            expression=expression,
            output_name=output_name,
            child_expr_time_ms=child_expr_time_ms,
        )

    def _evaluate_positional_kernel(
        self,
        value_series: pl.Series,
        group_codes: pl.Series,
        window: int,
        *,
        mode: Literal["argmax", "argmin"],
    ) -> tuple[pl.Series, dict[str, float | int | bool]]:
        return evaluate_positional_kernel(
            value_series,
            group_codes,
            window,
            mode=mode,
            native_kernel=evaluate_native_positional_kernel,
        )

    def _scan_group_positional_extreme(
        self,
        values: Sequence[object],
        start: int,
        end: int,
        window: int,
        *,
        mode: Literal["argmax", "argmin"],
        output: list[int | None],
    ) -> None:
        scan_group_positional_extreme(
            values,
            start,
            end,
            window,
            mode=mode,
            output=output,
        )

    def _materialize_ordered_plan_on_sorted_df(
        self,
        sorted_df: pl.DataFrame,
        *,
        materialized_plan: MaterializedOrderedPlan,
        reserved_names: set[str],
        stage_cache: dict[tuple, str],
        runtime: OrderedBatchRuntime | None = None,
        output_name: str | None = None,
    ) -> tuple[pl.DataFrame, str, dict[tuple, str]]:
        input_stage_names: list[str] = []
        for input_expr in materialized_plan.input_exprs:
            sorted_df, stage_name, stage_cache = self._materialize_expr_on_sorted_df(
                sorted_df,
                expr=input_expr,
                reserved_names=reserved_names,
                stage_cache=stage_cache,
                runtime=runtime,
            )
            input_stage_names.append(stage_name)

        result_cache_key = (
            "materialized_ordered",
            materialized_plan.func_name,
            tuple(self._planner.expr_key(expr) for expr in materialized_plan.input_exprs),
            materialized_plan.window,
        )
        result_stage_name = stage_cache.get(result_cache_key)
        if result_stage_name is None:
            result_stage_name = self._temporary_helper_name("__stage_value", reserved=reserved_names)
            # materialized_ordered is a language-level semantic path:
            # materialize child inputs first, then execute the ordered root
            # over those plain intermediate columns under the parent's contract.
            if len(input_stage_names) == 1 and materialized_plan.func_name in {"argmax", "argmin"}:
                sorted_df = self._attach_positional_kernel_from_stage(
                    sorted_df,
                    value_stage_name=input_stage_names[0],
                    result_stage_name=result_stage_name,
                    window=materialized_plan.window,
                    mode=materialized_plan.func_name,
                    runtime=runtime,
                    expression=repr(result_cache_key),
                    output_name=output_name or result_stage_name,
                )
            elif len(input_stage_names) == 1:
                if runtime is not None:
                    runtime.consume_stage(
                        input_stage_names[0],
                        consumer_kind="materialized_ordered_root",
                        frame=sorted_df,
                    )
                compiled = self._build_materialized_single_input_ordered_expr(
                    materialized_plan.func_name,
                    stage_name=input_stage_names[0],
                    window=materialized_plan.window,
                )
            elif materialized_plan.func_name == "corr":
                if runtime is not None:
                    runtime.consume_stage(
                        input_stage_names[0],
                        consumer_kind="materialized_ordered_root",
                        frame=sorted_df,
                    )
                    runtime.consume_stage(
                        input_stage_names[1],
                        consumer_kind="materialized_ordered_root",
                        frame=sorted_df,
                    )
                compiled = pl.rolling_corr(
                    pl.col(input_stage_names[0]),
                    pl.col(input_stage_names[1]),
                    window_size=materialized_plan.window,
                    min_samples=2,
                ).over(self.code_col)
            elif materialized_plan.func_name == "cov":
                if runtime is not None:
                    runtime.consume_stage(
                        input_stage_names[0],
                        consumer_kind="materialized_ordered_root",
                        frame=sorted_df,
                    )
                    runtime.consume_stage(
                        input_stage_names[1],
                        consumer_kind="materialized_ordered_root",
                        frame=sorted_df,
                    )
                compiled = pl.rolling_cov(
                    pl.col(input_stage_names[0]),
                    pl.col(input_stage_names[1]),
                    window_size=materialized_plan.window,
                    min_samples=2,
                ).over(self.code_col)
            else:
                raise ExecutionError(
                    f"Unsupported materialized ordered function: {materialized_plan.func_name}"
                )
            if len(input_stage_names) != 1 or materialized_plan.func_name not in {"argmax", "argmin"}:
                sorted_df = sorted_df.with_columns(compiled.alias(result_stage_name))
            if runtime is not None:
                runtime.register_stage(
                    expr_key=result_cache_key,
                    column_name=result_stage_name,
                    stage_kind="materialized_result",
                    producer_route="materialized_ordered",
                    frame=sorted_df,
                    cache_key=result_cache_key,
                )
            reserved_names.add(result_stage_name)
            stage_cache[result_cache_key] = result_stage_name

        return sorted_df, result_stage_name, stage_cache

    def _build_materialized_single_input_ordered_expr(
        self,
        func_name: str,
        *,
        stage_name: str,
        window: int,
    ) -> pl.Expr:
        value_expr = pl.col(stage_name)

        if func_name == "ts_mean":
            return value_expr.rolling_mean(window_size=window, min_samples=1).over(self.code_col)
        if func_name == "ts_min":
            return value_expr.rolling_min(window_size=window, min_samples=1).over(self.code_col)
        if func_name == "ts_max":
            return value_expr.rolling_max(window_size=window, min_samples=1).over(self.code_col)
        if func_name == "ts_median":
            return value_expr.rolling_median(window_size=window, min_samples=1).over(self.code_col)
        if func_name == "ts_sum":
            return value_expr.rolling_sum(window_size=window, min_samples=1).over(self.code_col)
        if func_name == "ts_std":
            return value_expr.rolling_std(window_size=window, min_samples=2).over(self.code_col)
        if func_name == "ts_rank":
            return value_expr.rolling_rank(
                window_size=window,
                method="average",
                min_samples=1,
            ).over(self.code_col)
        if func_name == "argmax":
            return self._build_positional_rolling_extremum_expr(
                value_expr,
                window=window,
                mode="argmax",
            )
        if func_name == "argmin":
            return self._build_positional_rolling_extremum_expr(
                value_expr,
                window=window,
                mode="argmin",
            )
        if func_name == "skew":
            return value_expr.rolling_skew(window_size=window, min_samples=3).over(self.code_col)
        if func_name == "kurt":
            return value_expr.rolling_kurtosis(
                window_size=window,
                fisher=True,
                bias=True,
                min_samples=4,
            ).over(self.code_col)

        raise ExecutionError(f"Unsupported materialized single-input ordered function: {func_name}")

    def _materialize_expr_on_sorted_df(
        self,
        sorted_df: pl.DataFrame,
        *,
        expr: Expr,
        reserved_names: set[str],
        stage_cache: dict[tuple, str],
        runtime: OrderedBatchRuntime | None = None,
    ) -> tuple[pl.DataFrame, str, dict[tuple, str]]:
        profile = self._infer_execution_profile(expr)
        plan = self._planner.build_plan(
            expr,
            ValidationResult(result_kind="column", profile=profile, backend=None),
        )

        if plan.route == "staged":
            if plan.staged is None:
                raise ExecutionError("Internal error: staged materialization plan is missing chain")
            return self._materialize_staged_chain_on_sorted_df(
                sorted_df,
                staged_plan=plan.staged,
                reserved_names=reserved_names,
                stage_cache=stage_cache,
                runtime=runtime,
            )

        if plan.route == "compiled":
            cache_key = ("expr", self._planner.expr_key(expr))
            stage_name = stage_cache.get(cache_key)
            if stage_name is None:
                stage_name = self._temporary_helper_name("__stage_value", reserved=reserved_names)
                sorted_df = sorted_df.with_columns(self._compile_expr(expr).alias(stage_name))
                reserved_names.add(stage_name)
                stage_cache[cache_key] = stage_name
                if runtime is not None:
                    runtime.register_stage(
                        expr_key=cache_key,
                        column_name=stage_name,
                        stage_kind="materialized_child",
                        producer_route="compiled_child",
                        frame=sorted_df,
                        cache_key=cache_key,
                    )
            return sorted_df, stage_name, stage_cache

        if plan.route == "positional_ordered":
            return self._materialize_positional_call_on_sorted_df(
                sorted_df,
                expr=expr,
                reserved_names=reserved_names,
                stage_cache=stage_cache,
                runtime=runtime,
            )

        raise ExecutionError(
            "Materialized ordered execution currently supports compiled, staged, and positional input expressions only"
        )

    def _materialize_staged_chain_on_sorted_df(
        self,
        sorted_df: pl.DataFrame,
        *,
        staged_plan: StagedChainPlan,
        reserved_names: set[str],
        stage_cache: dict[tuple, str],
        runtime: OrderedBatchRuntime | None = None,
    ) -> tuple[pl.DataFrame, str, dict[tuple, str]]:
        source_key = self._planner.expr_key(staged_plan.source_expr)
        source_cache_key = ("source", source_key)
        current_stage_name = stage_cache.get(source_cache_key)
        if current_stage_name is None:
            current_stage_name = self._temporary_helper_name("__stage_value", reserved=reserved_names)
            sorted_df = sorted_df.with_columns(
                self._compile_expr(staged_plan.source_expr).alias(current_stage_name)
            )
            reserved_names.add(current_stage_name)
            stage_cache[source_cache_key] = current_stage_name
            if runtime is not None:
                runtime.register_stage(
                    expr_key=source_cache_key,
                    column_name=current_stage_name,
                    stage_kind="ordered_helper",
                    producer_route="staged_source",
                    frame=sorted_df,
                    cache_key=source_cache_key,
                )

        prefix_keys: list[tuple] = []
        for step in staged_plan.steps:
            prefix_keys.append(self._planner.staged_step_key(step))
            cache_key = ("chain", source_key, tuple(prefix_keys))
            next_stage_name = stage_cache.get(cache_key)
            if next_stage_name is None:
                next_stage_name = self._temporary_helper_name("__stage_value", reserved=reserved_names)
                if runtime is not None:
                    runtime.consume_stage(
                        current_stage_name,
                        consumer_kind="staged_prefix",
                        frame=sorted_df,
                    )
                sorted_df = sorted_df.with_columns(
                    self._build_staged_cross_section_expr(
                        step,
                        stage_name=current_stage_name,
                    ).alias(next_stage_name)
                )
                reserved_names.add(next_stage_name)
                stage_cache[cache_key] = next_stage_name
                if runtime is not None:
                    runtime.register_stage(
                        expr_key=cache_key,
                        column_name=next_stage_name,
                        stage_kind="staged_prefix",
                        producer_route="staged",
                        frame=sorted_df,
                        cache_key=cache_key,
                    )
            current_stage_name = next_stage_name

        return sorted_df, current_stage_name, stage_cache

    def _get_prepared_frame(self) -> PreparedFrame:
        if self._prepared_frame is None:
            self._prepared_frame = build_prepared_frame(
                self.df,
                code_col=self.code_col,
                time_col=self.time_col,
            )

        return self._prepared_frame

    def _get_segmented_view(self, segment_spec_key: SegmentSpecKey) -> pl.DataFrame:
        prepared = self._get_prepared_frame()
        return get_segmented_view(
            prepared,
            segment_spec_key,
            prepare_segmented_sorted_df=(
                lambda sorted_df, key: self._prepare_segmented_sorted_df(
                    sorted_df,
                    segment_spec_key=key,
                )
            ),
        )

    def _evaluate_table(self, expr: Expr, validation: ValidationResult) -> pl.DataFrame:
        if validation.backend == "fft":
            return self._evaluate_fft(expr)

        raise ExecutionError(f"Unsupported table backend: {validation.backend}")

    def _infer_execution_profile(self, expr: Expr) -> ExecutionProfile:
        # Executor keeps a lightweight fallback so direct Executor.evaluate(...) calls
        # still choose the right execution path when no ValidationResult is provided.
        if isinstance(expr, (NumberNode, BooleanNode, VariableNode)):
            return ExecutionProfile.column()

        if isinstance(expr, ListNode):
            raise ExecutionError("List literals cannot be evaluated as standalone expressions")

        if isinstance(expr, UnaryOpNode):
            return self._infer_execution_profile(expr.operand)

        if isinstance(expr, BinaryOpNode):
            return ExecutionProfile.merge(
                self._infer_execution_profile(expr.left),
                self._infer_execution_profile(expr.right),
            )

        if isinstance(expr, CallNode):
            spec = get_function_spec(expr.name)
            child_profiles = [
                self._infer_execution_profile(arg)
                for index, arg in enumerate(expr.args)
                if not (spec is not None and spec.window_kind == "segmented" and index == 1)
            ]
            child_profiles.extend(self._infer_execution_profile(value) for value in expr.kwargs.values())
            if spec is None:
                return ExecutionProfile.merge(*child_profiles)
            return ExecutionProfile.merge(
                *child_profiles,
                result_kind=spec.result_kind,
                self_needs_code_group=spec.needs_code_group,
                self_needs_time_group=spec.needs_time_group,
                self_needs_time_order=spec.needs_time_order,
            )

        raise ExecutionError(f"Unsupported AST node for execution profiling: {type(expr).__name__}")

    def _evaluate_fft(self, expr: Expr) -> pl.DataFrame:
        # Validation guarantees the root shape, so execution can dispatch to the backend directly.
        if not isinstance(expr, CallNode) or len(expr.args) != 1:
            raise ExecutionError("Internal error: fft evaluation expects fft(column)")

        argument = expr.args[0]
        if not isinstance(argument, VariableNode):
            raise ExecutionError("Internal error: fft evaluation expects a direct column reference")

        try:
            return fourier_transform_frame(
                self.df,
                value_col=argument.name,
                time_col=self.time_col,
                code_col=self.code_col,
            )
        except ValueError as exc:
            raise ExecutionError(str(exc)) from exc

    def _compile_expr(self, expr: Expr) -> pl.Expr:
        if isinstance(expr, NumberNode):
            return pl.lit(expr.value)

        if isinstance(expr, BooleanNode):
            return pl.lit(expr.value)

        if isinstance(expr, ListNode):
            raise ExecutionError("List literals cannot be compiled as column expressions")

        if isinstance(expr, VariableNode):
            return pl.col(expr.name)

        if isinstance(expr, UnaryOpNode):
            operand = self._compile_expr(expr.operand)
            if expr.operator == "+":
                return operand
            if expr.operator == "-":
                return -operand
            if expr.operator == "not":
                return ~operand
            raise ExecutionError(f"Unsupported unary operator: {expr.operator}")

        if isinstance(expr, BinaryOpNode):
            return self._compile_binary(expr)

        if isinstance(expr, CallNode):
            return self._compile_call(expr)

        raise ExecutionError(f"Unsupported AST node: {type(expr).__name__}")

    def _compile_binary(self, expr: BinaryOpNode) -> pl.Expr:
        left = self._compile_expr(expr.left)
        right = self._compile_expr(expr.right)

        if expr.operator == "+":
            return left + right
        if expr.operator == "-":
            return left - right
        if expr.operator == "*":
            return left * right
        if expr.operator == "/":
            return left / right

        if expr.operator == ">":
            return left > right
        if expr.operator == "<":
            return left < right
        if expr.operator == ">=":
            return left >= right
        if expr.operator == "<=":
            return left <= right
        if expr.operator == "==":
            return left == right
        if expr.operator == "and":
            return left & right
        if expr.operator == "or":
            return left | right

        raise ExecutionError(f"Unsupported binary operator: {expr.operator}")

    def _compile_call(self, expr: CallNode) -> pl.Expr:
        function_name = canonical_function_name(expr.name)
        if function_name == "abs":
            return self._compile_abs(expr)
        if function_name == "argmax":
            return self._compile_argmax(expr)
        if function_name == "argmin":
            return self._compile_argmin(expr)
        if function_name == "clip":
            return self._compile_clip(expr)
        if function_name == "corr":
            return self._compile_corr(expr)
        if function_name == "cov":
            return self._compile_cov(expr)
        if function_name == "delta":
            return self._compile_delta(expr)
        if function_name == "where":
            return self._compile_where(expr)
        if function_name == "delay":
            return self._compile_delay(expr)
        if function_name == "skew":
            return self._compile_skew(expr)
        if function_name == "kurt":
            return self._compile_kurt(expr)
        if function_name == "pct_change":
            return self._compile_pct_change(expr)
        if function_name == "log":
            return self._compile_log(expr)
        if function_name == "ts_max":
            return self._compile_ts_max(expr)
        if function_name == "ts_median":
            return self._compile_ts_median(expr)
        if function_name == "ts_mean":
            return self._compile_ts_mean(expr)
        if function_name == "ts_min":
            return self._compile_ts_min(expr)
        if function_name == "ts_sum":
            return self._compile_ts_sum(expr)
        if function_name == "ts_std":
            return self._compile_ts_std(expr)
        if function_name == "demean":
            return self._compile_demean(expr)
        if function_name == "fill_null":
            return self._compile_fill_null(expr)
        if function_name == "group_demean":
            return self._compile_group_demean(expr)
        if function_name == "group_rank":
            return self._compile_group_rank(expr)
        if function_name == "group_zscore":
            return self._compile_group_zscore(expr)
        if function_name == "is_null":
            return self._compile_is_null(expr)
        if function_name == "zscore":
            return self._compile_zscore(expr)
        if function_name == "rank":
            return self._compile_rank(expr)
        if function_name == "scale":
            return self._compile_scale(expr)
        if function_name == "seg_all":
            return self._compile_seg_all(expr)
        if function_name == "seg_any":
            return self._compile_seg_any(expr)
        if function_name == "seg_count":
            return self._compile_seg_count(expr)
        if function_name == "seglen_all":
            return self._compile_seglen_all(expr)
        if function_name == "seglen_any":
            return self._compile_seglen_any(expr)
        if function_name == "seglen_count":
            return self._compile_seglen_count(expr)
        if function_name == "seglen_mean":
            return self._compile_seglen_mean(expr)
        if function_name == "seglen_sum":
            return self._compile_seglen_sum(expr)
        if function_name == "seg_mean":
            return self._compile_seg_mean(expr)
        if function_name == "seg_sum":
            return self._compile_seg_sum(expr)
        if function_name == "sign":
            return self._compile_sign(expr)
        if function_name == "signedpower":
            return self._compile_signedpower(expr)
        if function_name == "ts_all":
            return self._compile_ts_all(expr)
        if function_name == "ts_any":
            return self._compile_ts_any(expr)
        if function_name == "ts_count":
            return self._compile_ts_count(expr)
        if function_name == "ts_rank":
            return self._compile_ts_rank(expr)

        raise ExecutionError(f"Unsupported function in executor: {expr.name}")

    def _compile_abs(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 1 or expr.kwargs:
            raise ExecutionError("abs(x) expects exactly 1 positional argument")

        return self._compile_expr(expr.args[0]).abs()

    def _compile_log(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 1 or expr.kwargs:
            raise ExecutionError("log(x) expects exactly 1 positional argument")

        return self._compile_expr(expr.args[0]).log()

    def _compile_signedpower(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("signedpower(x, a) expects exactly 2 positional arguments")

        value_expr = self._compile_expr(expr.args[0])
        power = self._expect_scalar_number(expr.args[1], "signedpower")
        sign_expr = (
            pl.when(value_expr.is_null())
            .then(None)
            .when(value_expr < 0)
            .then(-1.0)
            .when(value_expr > 0)
            .then(1.0)
            .otherwise(0.0)
        )
        return sign_expr * value_expr.abs().pow(power)

    def _compile_argmax(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("argmax(x, n) expects exactly 2 positional arguments")

        value_expr = self._compile_time_series_input(expr.args[0])
        window = self._expect_numeric_literal(expr.args[1], "argmax")

        if window == 0:
            raise ExecutionError("Function 'argmax' requires window > 0")

        return self._build_positional_rolling_extremum_expr(
            value_expr,
            window=window,
            mode="argmax",
        )

    def _compile_argmin(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("argmin(x, n) expects exactly 2 positional arguments")

        value_expr = self._compile_time_series_input(expr.args[0])
        window = self._expect_numeric_literal(expr.args[1], "argmin")

        if window == 0:
            raise ExecutionError("Function 'argmin' requires window > 0")

        return self._build_positional_rolling_extremum_expr(
            value_expr,
            window=window,
            mode="argmin",
        )

    def _build_positional_rolling_extremum_expr(
        self,
        value_expr: pl.Expr,
        *,
        window: int,
        mode: Literal["argmax", "argmin"],
    ) -> pl.Expr:
        # Legacy expression fallback for cases that still need a pl.Expr inside
        # a larger compiled composition. Root positional calls use the grouped
        # deque kernel instead of this expression-expansion path.
        if window <= SHORT_WINDOW_THRESHOLD:
            return self._compile_positional_short_window(value_expr, window, mode=mode)

        return self._compile_positional_list_fallback(value_expr, window, mode=mode)

    def _compile_positional_short_window(
        self,
        value_expr: pl.Expr,
        window: int,
        *,
        mode: Literal["argmax", "argmin"],
    ) -> pl.Expr:
        # Build [x_t, x_{t-1}, ...] directly as columns. The smallest matching
        # offset is the nearest extremum, so min_horizontal over candidate
        # distances locks the current DSL tie-breaking rule.
        shifted = [
            value_expr if offset == 0 else value_expr.shift(offset).over(self.code_col)
            for offset in range(window)
        ]
        if mode == "argmax":
            extreme = pl.max_horizontal(*shifted)
        else:
            extreme = pl.min_horizontal(*shifted)

        missing_distance = window + 1
        candidates = [
            pl.when(item.eq(extreme))
            .then(pl.lit(offset))
            .otherwise(pl.lit(missing_distance))
            for offset, item in enumerate(shifted)
        ]
        nearest = pl.min_horizontal(*candidates)

        # max_horizontal/min_horizontal ignore nulls and return null for an
        # all-null effective window. Do not rely on when-then short-circuiting:
        # both branches are independently valid Polars expressions.
        return (
            pl.when(extreme.is_null())
            .then(pl.lit(None))
            .otherwise(nearest)
            .cast(pl.Int64)
        )

    def _compile_positional_list_fallback(
        self,
        value_expr: pl.Expr,
        window: int,
        *,
        mode: Literal["argmax", "argmin"],
    ) -> pl.Expr:
        # Large-window fallback preserves the phase-1 pure-Polars semantics.
        window_items = [value_expr]
        window_items.extend(
            value_expr.shift(offset).over(self.code_col)
            for offset in range(1, window)
        )
        window_list = pl.concat_list(window_items)
        if mode == "argmax":
            return window_list.list.arg_max().cast(pl.Int64)
        return window_list.list.arg_min().cast(pl.Int64)

    def _compile_fill_null(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("fill_null(x, v) expects exactly 2 positional arguments")

        value_expr = self._compile_expr(expr.args[0])
        fill_expr = self._compile_expr(expr.args[1])
        return value_expr.fill_null(fill_expr)

    def _compile_is_null(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 1 or expr.kwargs:
            raise ExecutionError("is_null(x) expects exactly 1 positional argument")

        return self._compile_expr(expr.args[0]).is_null()

    def _compile_clip(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 3 or expr.kwargs:
            raise ExecutionError("clip(x, lower, upper) expects exactly 3 positional arguments")

        value_expr = self._compile_expr(expr.args[0])
        lower_expr = self._compile_expr(expr.args[1])
        upper_expr = self._compile_expr(expr.args[2])

        return (
            pl.when(value_expr < lower_expr)
            .then(lower_expr)
            .when(value_expr > upper_expr)
            .then(upper_expr)
            .otherwise(value_expr)
        )

    def _compile_where(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 3 or expr.kwargs:
            raise ExecutionError("where(cond, a, b) expects exactly 3 positional arguments")

        condition = self._compile_expr(expr.args[0])
        true_value = self._compile_expr(expr.args[1])
        false_value = self._compile_expr(expr.args[2])

        return pl.when(condition).then(true_value).otherwise(false_value)

    def _expect_numeric_literal(self, expr: Expr, func_name: str) -> int:
        return expect_numeric_literal(expr, func_name)

    def _expect_scalar_number(self, expr: Expr, func_name: str) -> float:
        return expect_scalar_number(expr, func_name)

    def _expect_positive_numeric_literal(self, expr: Expr, func_name: str) -> int:
        return expect_positive_numeric_literal(expr, func_name)

    def _expect_positive_integer_list_literal(
        self,
        expr: Expr,
        func_name: str,
    ) -> tuple[int, ...]:
        return expect_positive_integer_list_literal(expr, func_name)

    def _expect_window_at_least(self, expr: Expr, func_name: str, minimum: int) -> int:
        return expect_window_at_least(expr, func_name, minimum)

    def _compile_time_series_input(self, expr: Expr) -> pl.Expr:
        return self._compile_expr(expr)

    def _compile_boolean_time_series_input(self, expr: Expr) -> pl.Expr:
        return self._compile_expr(expr)

    def _compile_boolean_window_as_int(self, expr: Expr) -> pl.Expr:
        # Boolean windows use fill_null(false) so ts_count/ts_any/ts_all share
        # one explicit and conservative null contract across the engine.
        condition_expr = self._compile_boolean_time_series_input(expr)
        return pl.when(condition_expr.fill_null(False)).then(1).otherwise(0)

    def _compile_boolean_segmented_as_int(self, expr: Expr) -> pl.Expr:
        # Segmented boolean reducers intentionally share the same null contract as
        # rolling boolean reducers so users do not have to remember two rule sets.
        return self._compile_boolean_window_as_int(expr)

    def _compile_corr(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 3 or expr.kwargs:
            raise ExecutionError("corr(x, y, n) expects exactly 3 positional arguments")

        left_expr = self._compile_time_series_input(expr.args[0])
        right_expr = self._compile_time_series_input(expr.args[1])
        window = self._expect_window_at_least(expr.args[2], "corr", 2)

        return pl.rolling_corr(
            left_expr,
            right_expr,
            window_size=window,
            min_samples=2,
        ).over(self.code_col)

    def _compile_cov(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 3 or expr.kwargs:
            raise ExecutionError("cov(x, y, n) expects exactly 3 positional arguments")

        left_expr = self._compile_time_series_input(expr.args[0])
        right_expr = self._compile_time_series_input(expr.args[1])
        window = self._expect_window_at_least(expr.args[2], "cov", 2)

        return pl.rolling_cov(
            left_expr,
            right_expr,
            window_size=window,
            min_samples=2,
        ).over(self.code_col)

    def _compile_seg_mean(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("seg_mean(x, n) expects exactly 2 positional arguments")

        value_expr = self._compile_time_series_input(expr.args[0])
        self._expect_positive_numeric_literal(expr.args[1], "seg_mean")
        return value_expr.mean().over([self.code_col, self._segment_id_name])

    def _compile_seglen_mean(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError(
                "seglen_mean(x, [l1, l2, ...]) expects exactly 2 positional arguments"
            )

        value_expr = self._compile_time_series_input(expr.args[0])
        self._expect_positive_integer_list_literal(expr.args[1], "seglen_mean")
        return value_expr.mean().over([self.code_col, self._segment_id_name])

    def _compile_seglen_sum(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError(
                "seglen_sum(x, [l1, l2, ...]) expects exactly 2 positional arguments"
            )

        value_expr = self._compile_time_series_input(expr.args[0])
        self._expect_positive_integer_list_literal(expr.args[1], "seglen_sum")
        return value_expr.sum().over([self.code_col, self._segment_id_name])

    def _compile_seglen_count(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError(
                "seglen_count(cond, [l1, l2, ...]) expects exactly 2 positional arguments"
            )

        condition_expr = self._compile_boolean_segmented_as_int(expr.args[0])
        self._expect_positive_integer_list_literal(expr.args[1], "seglen_count")
        return condition_expr.sum().over([self.code_col, self._segment_id_name])

    def _compile_seglen_any(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError(
                "seglen_any(cond, [l1, l2, ...]) expects exactly 2 positional arguments"
            )

        condition_expr = self._compile_boolean_segmented_as_int(expr.args[0])
        self._expect_positive_integer_list_literal(expr.args[1], "seglen_any")
        return condition_expr.max().over([self.code_col, self._segment_id_name]) > 0

    def _compile_seglen_all(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError(
                "seglen_all(cond, [l1, l2, ...]) expects exactly 2 positional arguments"
            )

        condition_expr = self._compile_boolean_segmented_as_int(expr.args[0])
        self._expect_positive_integer_list_literal(expr.args[1], "seglen_all")
        return condition_expr.min().over([self.code_col, self._segment_id_name]) == 1

    def _compile_seg_sum(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("seg_sum(x, n) expects exactly 2 positional arguments")

        value_expr = self._compile_time_series_input(expr.args[0])
        self._expect_positive_numeric_literal(expr.args[1], "seg_sum")
        return value_expr.sum().over([self.code_col, self._segment_id_name])

    def _compile_seg_count(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("seg_count(cond, n) expects exactly 2 positional arguments")

        condition_expr = self._compile_boolean_segmented_as_int(expr.args[0])
        self._expect_positive_numeric_literal(expr.args[1], "seg_count")
        return condition_expr.sum().over([self.code_col, self._segment_id_name])

    def _compile_seg_any(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("seg_any(cond, n) expects exactly 2 positional arguments")

        condition_expr = self._compile_boolean_segmented_as_int(expr.args[0])
        self._expect_positive_numeric_literal(expr.args[1], "seg_any")
        return condition_expr.max().over([self.code_col, self._segment_id_name]) > 0

    def _compile_seg_all(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("seg_all(cond, n) expects exactly 2 positional arguments")

        condition_expr = self._compile_boolean_segmented_as_int(expr.args[0])
        self._expect_positive_numeric_literal(expr.args[1], "seg_all")
        return condition_expr.min().over([self.code_col, self._segment_id_name]) == 1

    def _compile_delay(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("delay(x, n) expects exactly 2 positional arguments")

        value_expr = self._compile_time_series_input(expr.args[0])
        periods = self._expect_numeric_literal(expr.args[1], "delay")

        return self._compile_shifted_time_series(value_expr, periods)

    def _compile_delta(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("delta(x, n) expects exactly 2 positional arguments")

        value_expr = self._compile_time_series_input(expr.args[0])
        periods = self._expect_numeric_literal(expr.args[1], "delta")

        # Keep delta aligned with the documented engine semantics: x - delay(x, n).
        return value_expr - self._compile_shifted_time_series(value_expr, periods)

    def _compile_ts_mean(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("ts_mean(x, n) expects exactly 2 positional arguments")

        value_expr = self._compile_time_series_input(expr.args[0])
        window = self._expect_numeric_literal(expr.args[1], "ts_mean")

        if window == 0:
            raise ExecutionError("Function 'ts_mean' requires window > 0")

        return value_expr.rolling_mean(
            window_size=window,
            min_samples=1,
        ).over(self.code_col)

    def _compile_ts_min(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("ts_min(x, n) expects exactly 2 positional arguments")

        value_expr = self._compile_time_series_input(expr.args[0])
        window = self._expect_numeric_literal(expr.args[1], "ts_min")

        if window == 0:
            raise ExecutionError("Function 'ts_min' requires window > 0")

        return value_expr.rolling_min(
            window_size=window,
            min_samples=1,
        ).over(self.code_col)

    def _compile_ts_max(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("ts_max(x, n) expects exactly 2 positional arguments")

        value_expr = self._compile_time_series_input(expr.args[0])
        window = self._expect_numeric_literal(expr.args[1], "ts_max")

        if window == 0:
            raise ExecutionError("Function 'ts_max' requires window > 0")

        return value_expr.rolling_max(
            window_size=window,
            min_samples=1,
        ).over(self.code_col)

    def _compile_ts_median(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("ts_median(x, n) expects exactly 2 positional arguments")

        value_expr = self._compile_time_series_input(expr.args[0])
        window = self._expect_numeric_literal(expr.args[1], "ts_median")

        if window == 0:
            raise ExecutionError("Function 'ts_median' requires window > 0")

        return value_expr.rolling_median(
            window_size=window,
            min_samples=1,
        ).over(self.code_col)

    def _compile_ts_sum(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("ts_sum(x, n) expects exactly 2 positional arguments")

        value_expr = self._compile_time_series_input(expr.args[0])
        window = self._expect_numeric_literal(expr.args[1], "ts_sum")

        if window == 0:
            raise ExecutionError("Function 'ts_sum' requires window > 0")

        return value_expr.rolling_sum(
            window_size=window,
            min_samples=1,
        ).over(self.code_col)

    def _compile_ts_std(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("ts_std(x, n) expects exactly 2 positional arguments")

        value_expr = self._compile_time_series_input(expr.args[0])
        window = self._expect_numeric_literal(expr.args[1], "ts_std")

        if window == 0:
            raise ExecutionError("Function 'ts_std' requires window > 0")

        return value_expr.rolling_std(
            window_size=window,
            min_samples=2,
        ).over(self.code_col)

    def _compile_ts_count(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("ts_count(cond, n) expects exactly 2 positional arguments")

        condition_expr = self._compile_boolean_window_as_int(expr.args[0])
        window = self._expect_numeric_literal(expr.args[1], "ts_count")
        if window == 0:
            raise ExecutionError("Function 'ts_count' requires window > 0")

        return condition_expr.rolling_sum(
            window_size=window,
            min_samples=1,
        ).over(self.code_col)

    def _compile_ts_any(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("ts_any(cond, n) expects exactly 2 positional arguments")

        condition_expr = self._compile_boolean_window_as_int(expr.args[0])
        window = self._expect_numeric_literal(expr.args[1], "ts_any")
        if window == 0:
            raise ExecutionError("Function 'ts_any' requires window > 0")

        return condition_expr.rolling_max(
            window_size=window,
            min_samples=1,
        ).over(self.code_col) > 0

    def _compile_ts_all(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("ts_all(cond, n) expects exactly 2 positional arguments")

        condition_expr = self._compile_boolean_window_as_int(expr.args[0])
        window = self._expect_numeric_literal(expr.args[1], "ts_all")
        if window == 0:
            raise ExecutionError("Function 'ts_all' requires window > 0")

        return condition_expr.rolling_min(
            window_size=window,
            min_samples=1,
        ).over(self.code_col) == 1

    def _compile_ts_rank(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2:
            raise ExecutionError("ts_rank(x, n, ...) expects exactly 2 positional arguments")

        value_expr = self._compile_time_series_input(expr.args[0])
        window = self._expect_numeric_literal(expr.args[1], "ts_rank")
        if window == 0:
            raise ExecutionError("Function 'ts_rank' requires window > 0")

        ascending = False
        pct = False

        if "ascending" in expr.kwargs:
            ascending = self._expect_boolean_literal(expr.kwargs["ascending"], "ts_rank")

        if "pct" in expr.kwargs:
            pct = self._expect_boolean_literal(expr.kwargs["pct"], "ts_rank")

        ranked_input = value_expr if ascending else -value_expr
        rank_expr = ranked_input.rolling_rank(
            window_size=window,
            method="average",
            min_samples=1,
        ).over(self.code_col)

        if pct:
            sample_count_expr = value_expr.is_not_null().cast(pl.Int64).rolling_sum(
                window_size=window,
                min_samples=1,
            ).over(self.code_col)
            return rank_expr / sample_count_expr

        return rank_expr

    def _compile_skew(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("skew(x, n) expects exactly 2 positional arguments")

        value_expr = self._compile_time_series_input(expr.args[0])
        window = self._expect_window_at_least(expr.args[1], "skew", 3)

        return value_expr.rolling_skew(
            window_size=window,
            min_samples=3,
        ).over(self.code_col)

    def _compile_kurt(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("kurt(x, n) expects exactly 2 positional arguments")

        value_expr = self._compile_time_series_input(expr.args[0])
        window = self._expect_window_at_least(expr.args[1], "kurt", 4)

        return value_expr.rolling_kurtosis(
            window_size=window,
            fisher=True,
            bias=True,
            min_samples=4,
        ).over(self.code_col)

    def _compile_pct_change(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("pct_change(x, n) expects exactly 2 positional arguments")

        value_expr = self._compile_time_series_input(expr.args[0])
        periods = self._expect_numeric_literal(expr.args[1], "pct_change")

        # pct_change intentionally follows the engine-level arithmetic definition.
        delayed_expr = self._compile_shifted_time_series(value_expr, periods)
        return value_expr / delayed_expr - 1

    def _compile_demean(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 1 or expr.kwargs:
            raise ExecutionError("demean(x) expects exactly 1 positional argument")

        value_expr = self._compile_expr(expr.args[0])
        mean_expr = value_expr.mean().over(self.time_col)
        return value_expr - mean_expr

    def _compile_group_demean(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("group_demean(x, group) expects exactly 2 positional arguments")

        value_expr = self._compile_expr(expr.args[0])
        group_col = self._expect_group_column(expr, func_name="group_demean")
        mean_expr = value_expr.mean().over([self.time_col, group_col])
        return value_expr - mean_expr

    def _compile_zscore(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 1 or expr.kwargs:
            raise ExecutionError("zscore(x) expects exactly 1 positional argument")

        value_expr = self._compile_expr(expr.args[0])
        mean_expr = value_expr.mean().over(self.time_col)
        std_expr = value_expr.std().over(self.time_col)

        return (value_expr - mean_expr) / std_expr

    def _compile_group_zscore(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError("group_zscore(x, group) expects exactly 2 positional arguments")

        value_expr = self._compile_expr(expr.args[0])
        group_col = self._expect_group_column(expr, func_name="group_zscore")
        mean_expr = value_expr.mean().over([self.time_col, group_col])
        std_expr = value_expr.std().over([self.time_col, group_col])

        return (value_expr - mean_expr) / std_expr

    def _compile_scale(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) not in {1, 2} or expr.kwargs:
            raise ExecutionError("scale(x, a) expects 1 or 2 positional arguments")

        value_expr = self._compile_expr(expr.args[0])
        scale_to = self._expect_scalar_number(expr.args[1], "scale") if len(expr.args) == 2 else 1.0
        denominator = value_expr.abs().sum().over(self.time_col)
        return (
            pl.when(value_expr.is_null())
            .then(None)
            .when(denominator.is_null() | (denominator == 0))
            .then(None)
            .otherwise(value_expr * scale_to / denominator)
        )

    def _compile_rank(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 1:
            raise ExecutionError("rank(x, ...) expects exactly 1 positional argument")

        value_expr = self._compile_expr(expr.args[0])

        ascending = False
        pct = False

        if "ascending" in expr.kwargs:
            ascending = self._expect_boolean_literal(expr.kwargs["ascending"], "rank")

        if "pct" in expr.kwargs:
            pct = self._expect_boolean_literal(expr.kwargs["pct"], "rank")

        rank_expr = value_expr.rank(descending=not ascending).over(self.time_col)

        if pct:
            count_expr = pl.len().over(self.time_col)
            return rank_expr / count_expr

        return rank_expr

    def _compile_group_rank(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 2:
            raise ExecutionError("group_rank(x, group, ...) expects exactly 2 positional arguments")

        value_expr = self._compile_expr(expr.args[0])
        group_col = self._expect_group_column(expr, func_name="group_rank")

        ascending = False
        pct = False

        if "ascending" in expr.kwargs:
            ascending = self._expect_boolean_literal(expr.kwargs["ascending"], "group_rank")

        if "pct" in expr.kwargs:
            pct = self._expect_boolean_literal(expr.kwargs["pct"], "group_rank")

        partition = [self.time_col, group_col]
        rank_expr = value_expr.rank(descending=not ascending).over(partition)

        if pct:
            count_expr = pl.len().over(partition)
            return rank_expr / count_expr

        return rank_expr

    def _compile_sign(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 1 or expr.kwargs:
            raise ExecutionError("sign(x) expects exactly 1 positional argument")

        value_expr = self._compile_expr(expr.args[0])
        return (
            pl.when(value_expr.is_null())
            .then(None)
            .when(value_expr < 0)
            .then(-1.0)
            .when(value_expr > 0)
            .then(1.0)
            .otherwise(0.0)
        )

    def _expect_group_column(self, expr: CallNode, *, func_name: str) -> str:
        if len(expr.args) < 2 or not isinstance(expr.args[1], VariableNode):
            raise ExecutionError(
                f"Function '{func_name}' requires a direct group column reference as the second argument"
            )
        return expr.args[1].name

    def _expect_boolean_literal(self, expr: Expr, func_name: str) -> bool:
        if not isinstance(expr, BooleanNode):
            raise ExecutionError(
                f"Function '{func_name}' requires boolean literal keyword arguments"
            )
        return expr.value

    def _compile_shifted_time_series(self, value_expr: pl.Expr, periods: int) -> pl.Expr:
        return value_expr.shift(periods).over(self.code_col)

    def _expr_requires_staged_materialization(self, expr: Expr) -> bool:
        return self._planner.get_staged_chain_plan(expr) is not None

    def _build_staged_cross_section_expr(
        self,
        staged_spec: StagedCrossSectionStep,
        *,
        stage_name: str,
    ) -> pl.Expr:
        value_expr = pl.col(stage_name)
        if staged_spec.func_name == "demean":
            mean_expr = value_expr.mean().over(self.time_col)
            return value_expr - mean_expr

        if staged_spec.func_name == "zscore":
            mean_expr = value_expr.mean().over(self.time_col)
            std_expr = value_expr.std().over(self.time_col)
            return (value_expr - mean_expr) / std_expr

        if staged_spec.func_name == "scale":
            denominator = value_expr.abs().sum().over(self.time_col)
            return (
                pl.when(value_expr.is_null())
                .then(None)
                .when(denominator.is_null() | (denominator == 0))
                .then(None)
                .otherwise(value_expr * staged_spec.scale_to / denominator)
            )

        if staged_spec.func_name == "rank":
            rank_expr = value_expr.rank(descending=not staged_spec.ascending).over(self.time_col)
            if staged_spec.pct:
                count_expr = pl.len().over(self.time_col)
                return rank_expr / count_expr
            return rank_expr

        if staged_spec.group_col is None:
            raise ExecutionError("Internal error: grouped staged expression requires a group column")

        partition = [self.time_col, staged_spec.group_col]
        if staged_spec.func_name == "group_demean":
            mean_expr = value_expr.mean().over(partition)
            return value_expr - mean_expr

        if staged_spec.func_name == "group_zscore":
            mean_expr = value_expr.mean().over(partition)
            std_expr = value_expr.std().over(partition)
            return (value_expr - mean_expr) / std_expr

        if staged_spec.func_name == "group_rank":
            rank_expr = value_expr.rank(descending=not staged_spec.ascending).over(partition)
            if staged_spec.pct:
                count_expr = pl.len().over(partition)
                return rank_expr / count_expr
            return rank_expr

        raise ExecutionError(
            f"Internal error: unsupported staged cross-sectional function '{staged_spec.func_name}'"
        )

    def _expr_uses_segmented_window(self, expr: Expr) -> bool:
        return self._planner.expr_uses_segmented_window(expr)

    def _get_segment_spec_key(self, expr: Expr) -> SegmentSpecKey:
        segment_specs: set[SegmentSpecKey] = set()
        self._collect_segment_spec_keys(expr, specs=segment_specs)

        if not segment_specs:
            raise ExecutionError("Internal error: segmented execution requested without segmented calls")

        if len(segment_specs) != 1:
            raise ExecutionError(
                "Current segmented execution supports one segment spec per expression"
            )

        return next(iter(segment_specs))

    def _collect_segment_spec_keys(
        self,
        expr: Expr,
        *,
        specs: set[SegmentSpecKey],
    ) -> None:
        if isinstance(expr, CallNode):
            spec = get_function_spec(expr.name)
            if spec is not None and spec.window_kind == "segmented":
                if len(expr.args) < 2:
                    raise ExecutionError(f"Function '{expr.name}' requires a segment specification")
                specs.add(self._get_segment_spec_key_from_call(expr))

            for arg in expr.args:
                self._collect_segment_spec_keys(arg, specs=specs)
            for value in expr.kwargs.values():
                self._collect_segment_spec_keys(value, specs=specs)
            return

        if isinstance(expr, UnaryOpNode):
            self._collect_segment_spec_keys(expr.operand, specs=specs)
            return

        if isinstance(expr, BinaryOpNode):
            self._collect_segment_spec_keys(expr.left, specs=specs)
            self._collect_segment_spec_keys(expr.right, specs=specs)

    def _get_segment_spec_key_from_call(self, expr: CallNode) -> SegmentSpecKey:
        if len(expr.args) < 2:
            raise ExecutionError(f"Function '{expr.name}' requires a segment specification")

        if expr.name.startswith("seglen_"):
            return ("length", self._expect_positive_integer_list_literal(expr.args[1], expr.name))

        return ("equal", self._expect_positive_numeric_literal(expr.args[1], expr.name))

    def _prepare_segmented_sorted_df(
        self,
        sorted_df: pl.DataFrame,
        *,
        segment_spec_key: SegmentSpecKey,
    ) -> pl.DataFrame:
        return prepare_segmented_sorted_df(
            sorted_df,
            segment_spec_key=segment_spec_key,
            code_col=self.code_col,
            code_pos_name=self._code_pos_name,
            code_len_name=self._code_len_name,
            segment_id_name=self._segment_id_name,
        )

    def _build_equal_segment_id_expr(self, segment_count: int) -> pl.Expr:
        return build_equal_segment_id_expr(
            segment_count,
            code_pos_name=self._code_pos_name,
            code_len_name=self._code_len_name,
        )

    def _build_length_segment_id_expr(self, lengths: tuple[int, ...]) -> pl.Expr:
        return build_length_segment_id_expr(lengths, code_pos_name=self._code_pos_name)

    def _ensure_segment_lengths_cover_groups(
        self,
        prepared_df: pl.DataFrame,
        lengths: tuple[int, ...],
    ) -> None:
        ensure_segment_lengths_cover_groups(
            prepared_df,
            lengths,
            code_len_name=self._code_len_name,
        )
