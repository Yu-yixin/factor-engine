from __future__ import annotations

from collections import deque
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
from factor_engine.errors import ExecutionError
from factor_engine.fourier import fourier_transform_frame
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
    PositionalPhaseDetail,
    StageLifecycleProfiler,
    current_rss_mb,
)
from factor_engine.native_positional import evaluate_native_positional_kernel
from factor_engine.registry import get_function_spec
from factor_engine.stage_registry import StageRegistry
from factor_engine.validator import ExecutionProfile, ValidationResult


SegmentSpecKey = tuple[str, int | tuple[int, ...]]
# Root argmax/argmin calls use the dedicated grouped kernel. This threshold only
# applies to the legacy expression fallback used inside compiled compositions.
SHORT_WINDOW_THRESHOLD = 8


@dataclass
class PreparedFrame:
    # PreparedFrame is an internal optimization helper for ordered time-series work.
    original_df: pl.DataFrame
    sorted_df: pl.DataFrame
    row_index_name: str
    segmented_views: dict[SegmentSpecKey, pl.DataFrame]

    def restore_output_columns(self, output_names: list[str]) -> pl.DataFrame:
        return (
            self.sorted_df.select([self.row_index_name, *output_names])
            .sort(self.row_index_name)
            .drop(self.row_index_name)
        )


@dataclass
class OrderedBatchRuntime:
    batch_id: str
    profiler: StageLifecycleProfiler | None
    registry: StageRegistry
    lifecycle_enabled: bool
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

    def observe_frame(self, frame: pl.DataFrame) -> None:
        self.peak_frame_col_count = max(self.peak_frame_col_count, len(frame.columns))
        rss = current_rss_mb()
        self.peak_rss_mb = max(self.peak_rss_mb, rss)
        if self.profiler is not None:
            self.profiler.peak_rss_mb = max(self.profiler.peak_rss_mb, rss)

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
            enabled=self.lifecycle_enabled,
        )
        self.observe_frame(swept)
        return swept

    def finish(self, *, frame: pl.DataFrame, output_names: set[str]) -> None:
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
        late_alive = sum(
            1
            for item in details
            if item.alive_at_batch_end and item.planned_consumer_count_total > 0
        )
        self.profiler.add_batch(
            BatchDetail(
                batch_id=self.batch_id,
                route="ordered_batch",
                expression_count=self.expression_count,
                rows=self.rows,
                groups=self.groups,
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
    ):
        self.df = df
        self.time_col = time_col
        self.code_col = code_col
        self.profile_recorder = profile_recorder
        self.lifecycle_enabled = lifecycle_enabled
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

    def _temporary_helper_name(
        self,
        base_name: str,
        *,
        reserved: set[str] | None = None,
    ) -> str:
        used_names = set(self.df.columns)
        if reserved is not None:
            used_names.update(reserved)

        candidate = base_name
        while candidate in used_names:
            candidate = f"_{candidate}"
        return candidate

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
        compiled_time_items: list[tuple[str, ValidationResult, pl.Expr]] = []
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
                target_bucket = (
                    compiled_time_items if validation.profile.needs_time_order else compiled_no_time_items
                )
                target_bucket.append((output_name, validation, self.compile(expr)))

        deferred_planning_items = [item for item in planning_items if item.plan.route != "compiled"]
        batch_plan = self._planner.build_batch_plan(deferred_planning_items)
        result_df = self.df
        if compiled_no_time_items:
            result_df = Executor(
                result_df,
                time_col=self.time_col,
                code_col=self.code_col,
                profile_recorder=self.profile_recorder,
                lifecycle_enabled=self.lifecycle_enabled,
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
                lifecycle_enabled=self.lifecycle_enabled,
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
        compiled_time_items: list[tuple[str, ValidationResult, pl.Expr]] | None = None,
    ) -> pl.DataFrame:
        result_df = self.df
        ordered_compiled_items = compiled_time_items or []

        if batch_plan.segmented_items:
            result_df = Executor(
                result_df,
                time_col=self.time_col,
                code_col=self.code_col,
                profile_recorder=self.profile_recorder,
                lifecycle_enabled=self.lifecycle_enabled,
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
                lifecycle_enabled=self.lifecycle_enabled,
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
                for output_name, _validation, _compiled in ordered_compiled_items
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
        # Pointwise and cross-sectional expressions can stay on the original row order.
        return self.df.with_columns(compiled.alias(output_name))

    def _evaluate_row_aligned_time_ordered(
        self,
        compiled: pl.Expr,
        *,
        output_name: str,
    ) -> pl.DataFrame:
        prepared = self._get_prepared_frame()
        sorted_df = prepared.sorted_df.with_columns(compiled.alias(output_name))
        return (
            sorted_df.sort(prepared.row_index_name)
            .drop(prepared.row_index_name)
        )

    def _evaluate_many_row_aligned_no_time_order(
        self,
        base_df: pl.DataFrame,
        items: list[tuple[str, pl.Expr]],
    ) -> pl.DataFrame:
        compiled = [expr.alias(output_name) for output_name, expr in items]
        return base_df.with_columns(compiled)

    def _evaluate_many_row_aligned_time_ordered(
        self,
        items: list[tuple[str, pl.Expr]],
    ) -> pl.DataFrame:
        prepared = self._get_prepared_frame()
        compiled = [expr.alias(output_name) for output_name, expr in items]

        prepared.sorted_df = prepared.sorted_df.with_columns(compiled)
        return prepared.restore_output_columns([output_name for output_name, _ in items])

    def _evaluate_segmented_column(
        self,
        expr: Expr,
        *,
        output_name: str,
    ) -> pl.DataFrame:
        prepared = self._get_prepared_frame()
        segment_spec_key = self._get_segment_spec_key(expr)
        segmented_df = self._get_segmented_view(segment_spec_key)
        compiled = self._compile_expr(expr)
        result_df = segmented_df.with_columns(compiled.alias(output_name))

        return (
            result_df.select([prepared.row_index_name, *self.df.columns, output_name])
            .sort(prepared.row_index_name)
            .drop(prepared.row_index_name)
        )

    def _evaluate_many_segmented_columns(
        self,
        items: list[tuple[str, Expr, ValidationResult]],
    ) -> pl.DataFrame:
        if not items:
            return self.df

        prepared = self._get_prepared_frame()
        outputs_by_name: dict[str, pl.Series] = {}
        items_by_segment_spec: dict[SegmentSpecKey, list[tuple[str, Expr]]] = {}

        for output_name, expr, _validation in items:
            segment_spec_key = self._get_segment_spec_key(expr)
            items_by_segment_spec.setdefault(segment_spec_key, []).append((output_name, expr))

        for segment_spec_key, grouped_items in items_by_segment_spec.items():
            segmented_df = self._get_segmented_view(segment_spec_key)
            compiled = [
                self._compile_expr(expr).alias(output_name)
                for output_name, expr in grouped_items
            ]
            grouped_result = (
                segmented_df.select([prepared.row_index_name, *compiled])
                .sort(prepared.row_index_name)
                .drop(prepared.row_index_name)
            )
            for output_name, _expr in grouped_items:
                outputs_by_name[output_name] = grouped_result.get_column(output_name)

        return self.df.with_columns([outputs_by_name[output_name] for output_name, _expr, _validation in items])

    def _evaluate_staged_column(
        self,
        staged_plan: StagedChainPlan,
        *,
        output_name: str,
    ) -> pl.DataFrame:
        prepared = self._get_prepared_frame()
        sorted_df = prepared.sorted_df
        reserved_names = set(sorted_df.columns)
        sorted_df, final_stage_name, _stage_cache = self._materialize_staged_chain_on_sorted_df(
            sorted_df,
            staged_plan=staged_plan,
            reserved_names=reserved_names,
            stage_cache={},
        )
        if final_stage_name != output_name:
            sorted_df = sorted_df.with_columns(pl.col(final_stage_name).alias(output_name))

        return (
            sorted_df.select([prepared.row_index_name, *self.df.columns, output_name])
            .sort(prepared.row_index_name)
            .drop(prepared.row_index_name)
        )

    def _evaluate_many_staged_columns(
        self,
        items: list[tuple[str, StagedChainPlan]],
    ) -> pl.DataFrame:
        if not items:
            return self.df

        prepared = self._get_prepared_frame()
        sorted_df = prepared.sorted_df
        reserved_names = set(sorted_df.columns)
        output_names: list[str] = []
        stage_cache: dict[tuple, str] = {}
        output_stage_names: dict[str, str] = {}

        for output_name, staged_plan in items:
            sorted_df, final_stage_name, stage_cache = self._materialize_staged_chain_on_sorted_df(
                sorted_df,
                staged_plan=staged_plan,
                reserved_names=reserved_names,
                stage_cache=stage_cache,
            )
            output_stage_names[output_name] = final_stage_name
            output_names.append(output_name)

        sorted_df = sorted_df.with_columns(
            [pl.col(output_stage_names[output_name]).alias(output_name) for output_name in output_names]
        )
        prepared.sorted_df = sorted_df
        ordered_outputs = prepared.restore_output_columns(output_names)
        return self.df.with_columns([ordered_outputs.get_column(output_name) for output_name in output_names])

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
        if cache_key is not None:
            planned[cache_key] = planned.get(cache_key, 0) + 1

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

    def _evaluate_many_ordered_batch_plan(
        self,
        batch_plan: BatchExecutionPlan,
        *,
        compiled_time_items: list[tuple[str, ValidationResult, pl.Expr]],
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
        planned_stage_consumers = self._plan_ordered_batch_stage_consumers(batch_plan)
        runtime: OrderedBatchRuntime | None = None
        if self.profile_recorder is not None or self.lifecycle_enabled:
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
                lifecycle_enabled=self.lifecycle_enabled,
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

        if compiled_time_items:
            sorted_df = sorted_df.with_columns(
                [compiled.alias(output_name) for output_name, _validation, compiled in compiled_time_items]
            )
            output_names.extend([output_name for output_name, _validation, _compiled in compiled_time_items])
            if runtime is not None:
                runtime.observe_frame(sorted_df)

        stage_started_at = time.perf_counter()
        for item in batch_plan.positional_items:
            sorted_df, final_stage_name, stage_cache = self._materialize_positional_call_on_sorted_df(
                sorted_df,
                expr=item.expr,
                reserved_names=reserved_names,
                stage_cache=stage_cache,
                runtime=runtime,
                output_name=item.output_name,
            )
            if final_stage_name != item.output_name:
                if runtime is not None:
                    runtime.consume_stage(final_stage_name, consumer_kind="output_alias", frame=sorted_df)
                sorted_df = sorted_df.with_columns(pl.col(final_stage_name).alias(item.output_name))
            output_names.append(item.output_name)
            if runtime is not None:
                runtime.observe_frame(sorted_df)
                sorted_df = runtime.sweep(
                    sorted_df,
                    stage_cache=stage_cache,
                    output_names=set(output_names),
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
            if final_stage_name != item.output_name:
                if runtime is not None:
                    runtime.consume_stage(final_stage_name, consumer_kind="output_alias", frame=sorted_df)
                sorted_df = sorted_df.with_columns(pl.col(final_stage_name).alias(item.output_name))
            output_names.append(item.output_name)
            if runtime is not None:
                runtime.observe_frame(sorted_df)
                sorted_df = runtime.sweep(
                    sorted_df,
                    stage_cache=stage_cache,
                    output_names=set(output_names),
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
            if runtime is not None:
                runtime.consume_stage(
                    stage_cache[binding.cache_key],
                    consumer_kind="output_binding",
                    frame=sorted_df,
                )
            sorted_df = sorted_df.with_columns(
                pl.col(stage_cache[binding.cache_key]).alias(binding.output_name)
            )
            output_names.append(binding.output_name)
            if runtime is not None:
                runtime.observe_frame(sorted_df)

        if runtime is not None:
            runtime.stage_materialize_time_ms = (time.perf_counter() - stage_started_at) * 1000
            sorted_df = runtime.sweep(
                sorted_df,
                stage_cache=stage_cache,
                output_names=set(output_names),
            )

        prepared.sorted_df = sorted_df
        restore_started_at = time.perf_counter()
        ordered_outputs = prepared.restore_output_columns(output_names)
        if runtime is not None:
            runtime.restore_time_ms = (time.perf_counter() - restore_started_at) * 1000
        append_started_at = time.perf_counter()
        result = self.df.with_columns([ordered_outputs.get_column(output_name) for output_name in output_names])
        if runtime is not None:
            runtime.append_time_ms = (time.perf_counter() - append_started_at) * 1000
            runtime.finish(frame=sorted_df, output_names=set(output_names))
        return result

    def _evaluate_materialized_ordered_column(
        self,
        materialized_plan: MaterializedOrderedPlan,
        *,
        output_name: str,
    ) -> pl.DataFrame:
        prepared = self._get_prepared_frame()
        reserved_names = set(prepared.sorted_df.columns)
        sorted_df, final_stage_name, _stage_cache = self._materialize_ordered_plan_on_sorted_df(
            prepared.sorted_df,
            materialized_plan=materialized_plan,
            reserved_names=reserved_names,
            stage_cache={},
        )
        if final_stage_name != output_name:
            sorted_df = sorted_df.with_columns(pl.col(final_stage_name).alias(output_name))

        return (
            sorted_df.select([prepared.row_index_name, *self.df.columns, output_name])
            .sort(prepared.row_index_name)
            .drop(prepared.row_index_name)
        )

    def _evaluate_positional_ordered_column(
        self,
        expr: Expr,
        *,
        output_name: str,
    ) -> pl.DataFrame:
        prepared = self._get_prepared_frame()
        reserved_names = set(prepared.sorted_df.columns)
        sorted_df, final_stage_name, _stage_cache = self._materialize_positional_call_on_sorted_df(
            prepared.sorted_df,
            expr=expr,
            reserved_names=reserved_names,
            stage_cache={},
        )
        if final_stage_name != output_name:
            sorted_df = sorted_df.with_columns(pl.col(final_stage_name).alias(output_name))

        return (
            sorted_df.select([prepared.row_index_name, *self.df.columns, output_name])
            .sort(prepared.row_index_name)
            .drop(prepared.row_index_name)
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
        if not isinstance(expr, CallNode) or expr.name not in {"argmax", "argmin"}:
            raise ExecutionError("Internal error: positional ordered route expects argmax/argmin")
        if len(expr.args) != 2 or expr.kwargs:
            raise ExecutionError(f"{expr.name}(x, n) expects exactly 2 positional arguments")

        window = self._expect_positive_numeric_literal(expr.args[1], expr.name)
        result_cache_key = (
            "positional_kernel",
            expr.name,
            self._planner.expr_key(expr.args[0]),
            window,
        )
        result_stage_name = stage_cache.get(result_cache_key)
        if result_stage_name is not None:
            return sorted_df, result_stage_name, stage_cache

        child_started_at = time.perf_counter()
        sorted_df, value_stage_name, stage_cache = self._materialize_expr_on_sorted_df(
            sorted_df,
            expr=expr.args[0],
            reserved_names=reserved_names,
            stage_cache=stage_cache,
            runtime=runtime,
        )
        child_expr_time_ms = (time.perf_counter() - child_started_at) * 1000
        result_stage_name = self._temporary_helper_name("__stage_value", reserved=reserved_names)
        sorted_df = self._attach_positional_kernel_from_stage(
            sorted_df,
            value_stage_name=value_stage_name,
            result_stage_name=result_stage_name,
            window=window,
            mode=expr.name,
            runtime=runtime,
            expression=repr(self._planner.expr_key(expr)),
            output_name=output_name or result_stage_name,
            child_expr_time_ms=child_expr_time_ms,
        )
        if runtime is not None:
            runtime.register_stage(
                expr_key=result_cache_key,
                column_name=result_stage_name,
                stage_kind="positional_result",
                producer_route="positional_ordered",
                frame=sorted_df,
                cache_key=result_cache_key,
            )
        reserved_names.add(result_stage_name)
        stage_cache[result_cache_key] = result_stage_name
        return sorted_df, result_stage_name, stage_cache

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
        if runtime is not None:
            runtime.consume_stage(
                value_stage_name,
                consumer_kind="positional_kernel",
                frame=sorted_df,
            )
        rss_before = current_rss_mb()
        positional_started_at = time.perf_counter()
        result, kernel_profile = self._evaluate_positional_kernel(
            sorted_df.get_column(value_stage_name),
            sorted_df.get_column(self.code_col),
            window,
            mode=mode,
        )
        positional_total_time_ms = (time.perf_counter() - positional_started_at) * 1000
        attach_started_at = time.perf_counter()
        attached = sorted_df.with_columns(result.alias(result_stage_name))
        result_attach_time_ms = (
            kernel_profile["series_construct_time_ms"]
            + (time.perf_counter() - attach_started_at) * 1000
        )
        rss_after = current_rss_mb()
        if runtime is not None:
            runtime.add_positional_phase(
                PositionalPhaseDetail(
                    run_id=runtime.profiler.run_id if runtime.profiler is not None else "",
                    batch_id=runtime.batch_id,
                    expression=expression,
                    output_name=output_name or result_stage_name,
                    function_name=mode,
                    rows=sorted_df.height,
                    groups=kernel_profile["group_count"],
                    window=window,
                    child_stage_kind=runtime.stage_kind_for_column(value_stage_name),
                    prepare_sort_time_ms=runtime.prepare_sort_time_ms,
                    child_expr_time_ms=child_expr_time_ms,
                    positional_total_time_ms=positional_total_time_ms,
                    positional_to_list_time_ms=kernel_profile["to_list_time_ms"],
                    positional_group_scan_time_ms=kernel_profile["group_scan_time_ms"],
                    result_attach_time_ms=result_attach_time_ms,
                    restore_time_ms=runtime.restore_time_ms,
                    python_kernel_used=not bool(kernel_profile["native_kernel_used"]),
                    native_kernel_used=bool(kernel_profile["native_kernel_used"]),
                    native_low_copy_bridge_used=bool(kernel_profile["native_low_copy_bridge_used"]),
                    python_object_bridge_used=bool(kernel_profile["python_object_bridge_used"]),
                    native_parallel_used=bool(kernel_profile["native_parallel_used"]),
                    group_parallelism_level=int(kernel_profile["group_parallelism_level"]),
                    group_count=kernel_profile["group_count"],
                    avg_group_size=kernel_profile["avg_group_size"],
                    max_group_size=kernel_profile["max_group_size"],
                    output_non_null_count=kernel_profile["output_non_null_count"],
                    rss_before_mb=rss_before,
                    rss_after_mb=rss_after,
                    peak_rss_mb=max(rss_before, rss_after),
                )
            )
        return attached

    def _evaluate_positional_kernel(
        self,
        value_series: pl.Series,
        group_codes: pl.Series,
        window: int,
        *,
        mode: Literal["argmax", "argmin"],
    ) -> tuple[pl.Series, dict[str, float | int | bool]]:
        native_result = evaluate_native_positional_kernel(
            value_series,
            group_codes,
            window,
            mode=mode,
        )
        if native_result is not None:
            group_lengths = (
                group_codes.to_frame("__code")
                .group_by("__code", maintain_order=True)
                .agg(pl.len().alias("__len"))
                .get_column("__len")
                .to_list()
            )
            output_non_null_count = native_result.series.is_not_null().sum()
            group_count = len(group_lengths)
            return native_result.series, {
                "to_list_time_ms": native_result.to_list_time_ms,
                "group_scan_time_ms": native_result.group_scan_time_ms,
                "series_construct_time_ms": native_result.series_construct_time_ms,
                "native_kernel_used": native_result.native_kernel_used,
                "native_low_copy_bridge_used": native_result.low_copy_bridge_used,
                "python_object_bridge_used": native_result.python_object_bridge_used,
                "native_parallel_used": native_result.native_parallel_used,
                "group_parallelism_level": native_result.group_parallelism_level,
                "group_count": group_count,
                "avg_group_size": value_series.len() / group_count if group_count else 0.0,
                "max_group_size": max(group_lengths, default=0),
                "output_non_null_count": int(output_non_null_count),
            }

        to_list_started_at = time.perf_counter()
        values = value_series.to_list()
        to_list_time_ms = (time.perf_counter() - to_list_started_at) * 1000
        scan_started_at = time.perf_counter()
        group_lengths = (
            group_codes.to_frame("__code")
            .group_by("__code", maintain_order=True)
            .agg(pl.len().alias("__len"))
            .get_column("__len")
            .to_list()
        )
        output: list[int | None] = [None] * len(values)

        group_start = 0
        for group_length in group_lengths:
            group_end = group_start + group_length
            self._scan_group_positional_extreme(
                values,
                group_start,
                group_end,
                window,
                mode=mode,
                output=output,
            )
            group_start = group_end

        group_scan_time_ms = (time.perf_counter() - scan_started_at) * 1000
        series_started_at = time.perf_counter()
        result = pl.Series(value_series.name, output, dtype=pl.Int64)
        series_construct_time_ms = (time.perf_counter() - series_started_at) * 1000
        group_count = len(group_lengths)
        return result, {
            "to_list_time_ms": to_list_time_ms,
            "group_scan_time_ms": group_scan_time_ms,
            "series_construct_time_ms": series_construct_time_ms,
            "native_kernel_used": False,
            "native_low_copy_bridge_used": False,
            "python_object_bridge_used": True,
            "native_parallel_used": False,
            "group_parallelism_level": 1,
            "group_count": group_count,
            "avg_group_size": len(values) / group_count if group_count else 0.0,
            "max_group_size": max(group_lengths, default=0),
            "output_non_null_count": sum(item is not None for item in output),
        }

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
        candidates: deque[int] = deque()
        choose_max = mode == "argmax"

        for index in range(start, end):
            first_valid_index = index - window + 1
            while candidates and candidates[0] < first_valid_index:
                candidates.popleft()

            current_value = values[index]
            if current_value is not None:
                # Invariant: the deque front is the best still-in-window index.
                # Equal values are popped so the newer equal candidate survives,
                # which implements the DSL's nearest-extremum tie rule.
                while candidates:
                    tail_value = values[candidates[-1]]
                    if tail_value is None:
                        candidates.pop()
                        continue
                    if choose_max:
                        should_drop_tail = current_value >= tail_value
                    else:
                        should_drop_tail = current_value <= tail_value
                    if not should_drop_tail:
                        break
                    candidates.pop()
                candidates.append(index)

            output[index] = None if not candidates else index - candidates[0]

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
        if self.time_col not in self.df.columns or self.code_col not in self.df.columns:
            raise ExecutionError(
                f"Ordered time-series execution requires columns: {self.code_col}, {self.time_col}"
            )

        if self._prepared_frame is None:
            row_index_name = "__row_idx"
            while row_index_name in self.df.columns:
                row_index_name = f"_{row_index_name}"

            sorted_df = (
                self.df.with_row_index(row_index_name)
                .sort([self.code_col, self.time_col])
            )
            self._prepared_frame = PreparedFrame(
                original_df=self.df,
                sorted_df=sorted_df,
                row_index_name=row_index_name,
                segmented_views={},
            )

        return self._prepared_frame

    def _get_segmented_view(self, segment_spec_key: SegmentSpecKey) -> pl.DataFrame:
        prepared = self._get_prepared_frame()
        segmented_view = prepared.segmented_views.get(segment_spec_key)
        if segmented_view is not None:
            return segmented_view

        # Segment views are cached per immutable spec key so evaluate_many() can
        # reuse the same ordered split across multiple segmented expressions.
        segmented_view = self._prepare_segmented_sorted_df(
            prepared.sorted_df,
            segment_spec_key=segment_spec_key,
        )
        prepared.segmented_views[segment_spec_key] = segmented_view
        return segmented_view

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
        if expr.name == "abs":
            return self._compile_abs(expr)
        if expr.name == "argmax":
            return self._compile_argmax(expr)
        if expr.name == "argmin":
            return self._compile_argmin(expr)
        if expr.name == "clip":
            return self._compile_clip(expr)
        if expr.name == "corr":
            return self._compile_corr(expr)
        if expr.name == "cov":
            return self._compile_cov(expr)
        if expr.name == "delta":
            return self._compile_delta(expr)
        if expr.name == "where":
            return self._compile_where(expr)
        if expr.name == "delay":
            return self._compile_delay(expr)
        if expr.name == "skew":
            return self._compile_skew(expr)
        if expr.name == "kurt":
            return self._compile_kurt(expr)
        if expr.name == "pct_change":
            return self._compile_pct_change(expr)
        if expr.name == "ts_max":
            return self._compile_ts_max(expr)
        if expr.name == "ts_median":
            return self._compile_ts_median(expr)
        if expr.name == "ts_mean":
            return self._compile_ts_mean(expr)
        if expr.name == "ts_min":
            return self._compile_ts_min(expr)
        if expr.name == "ts_sum":
            return self._compile_ts_sum(expr)
        if expr.name == "ts_std":
            return self._compile_ts_std(expr)
        if expr.name == "demean":
            return self._compile_demean(expr)
        if expr.name == "fill_null":
            return self._compile_fill_null(expr)
        if expr.name == "group_demean":
            return self._compile_group_demean(expr)
        if expr.name == "group_rank":
            return self._compile_group_rank(expr)
        if expr.name == "group_zscore":
            return self._compile_group_zscore(expr)
        if expr.name == "is_null":
            return self._compile_is_null(expr)
        if expr.name == "zscore":
            return self._compile_zscore(expr)
        if expr.name == "rank":
            return self._compile_rank(expr)
        if expr.name == "seg_all":
            return self._compile_seg_all(expr)
        if expr.name == "seg_any":
            return self._compile_seg_any(expr)
        if expr.name == "seg_count":
            return self._compile_seg_count(expr)
        if expr.name == "seglen_all":
            return self._compile_seglen_all(expr)
        if expr.name == "seglen_any":
            return self._compile_seglen_any(expr)
        if expr.name == "seglen_count":
            return self._compile_seglen_count(expr)
        if expr.name == "seglen_mean":
            return self._compile_seglen_mean(expr)
        if expr.name == "seglen_sum":
            return self._compile_seglen_sum(expr)
        if expr.name == "seg_mean":
            return self._compile_seg_mean(expr)
        if expr.name == "seg_sum":
            return self._compile_seg_sum(expr)
        if expr.name == "sign":
            return self._compile_sign(expr)
        if expr.name == "ts_all":
            return self._compile_ts_all(expr)
        if expr.name == "ts_any":
            return self._compile_ts_any(expr)
        if expr.name == "ts_count":
            return self._compile_ts_count(expr)
        if expr.name == "ts_rank":
            return self._compile_ts_rank(expr)

        raise ExecutionError(f"Unsupported function in executor: {expr.name}")

    def _compile_abs(self, expr: CallNode) -> pl.Expr:
        if len(expr.args) != 1 or expr.kwargs:
            raise ExecutionError("abs(x) expects exactly 1 positional argument")

        return self._compile_expr(expr.args[0]).abs()

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
        if not isinstance(expr, NumberNode):
            raise ExecutionError(
                f"Function '{func_name}' requires an integer literal window argument"
            )

        value = expr.value
        if int(value) != value or value < 0:
            raise ExecutionError(
                f"Function '{func_name}' requires a non-negative integer argument"
            )

        return int(value)

    def _expect_positive_numeric_literal(self, expr: Expr, func_name: str) -> int:
        value = self._expect_numeric_literal(expr, func_name)
        if value <= 0:
            raise ExecutionError(
                f"Function '{func_name}' requires a positive integer argument"
            )
        return value

    def _expect_positive_integer_list_literal(
        self,
        expr: Expr,
        func_name: str,
    ) -> tuple[int, ...]:
        if not isinstance(expr, ListNode) or not expr.items:
            raise ExecutionError(
                f"Function '{func_name}' requires a positive integer literal length list"
            )

        values: list[int] = []
        for item in expr.items:
            if not isinstance(item, NumberNode):
                raise ExecutionError(
                    f"Function '{func_name}' requires a positive integer literal length list"
                )

            value = item.value
            if int(value) != value or value <= 0:
                raise ExecutionError(
                    f"Function '{func_name}' requires a positive integer literal length list"
                )
            values.append(int(value))

        return tuple(values)

    def _expect_window_at_least(self, expr: Expr, func_name: str, minimum: int) -> int:
        window = self._expect_numeric_literal(expr, func_name)
        if window < minimum:
            raise ExecutionError(f"Function '{func_name}' requires window >= {minimum}")
        return window

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
        with_group_position = sorted_df.with_columns(
            [
                (pl.col(self.code_col).cum_count().over(self.code_col) - 1).alias(
                    self._code_pos_name
                ),
                pl.len().over(self.code_col).alias(self._code_len_name),
            ]
        )

        kind, spec_value = segment_spec_key
        if kind == "equal":
            if not isinstance(spec_value, int):
                raise ExecutionError("Internal error: invalid equal segment specification")
            segment_id_expr = self._build_equal_segment_id_expr(spec_value)
        elif kind == "length":
            if not isinstance(spec_value, tuple):
                raise ExecutionError("Internal error: invalid length segment specification")
            self._ensure_segment_lengths_cover_groups(with_group_position, spec_value)
            segment_id_expr = self._build_length_segment_id_expr(spec_value)
        else:
            raise ExecutionError(f"Internal error: unsupported segment specification kind '{kind}'")

        return with_group_position.with_columns(segment_id_expr.alias(self._segment_id_name))

    def _build_equal_segment_id_expr(self, segment_count: int) -> pl.Expr:
        code_pos = pl.col(self._code_pos_name)
        code_len = pl.col(self._code_len_name)
        segment_count_lit = pl.lit(segment_count)
        base_size = code_len // segment_count_lit
        larger_segment_count = code_len % segment_count_lit
        larger_segment_rows = (base_size + 1) * larger_segment_count

        # Segment remainders are assigned to the earliest buckets so the split
        # stays deterministic and the n > m case naturally collapses to 1-row segments.
        segment_id_expr = (
            pl.when(code_pos < larger_segment_rows)
            .then(code_pos // (base_size + 1))
            .otherwise(
                pl.when(base_size > 0)
                .then(
                    larger_segment_count
                    + ((code_pos - larger_segment_rows) // base_size)
                )
                .otherwise(code_pos)
            )
            .cast(pl.Int64)
        )

        return segment_id_expr

    def _build_length_segment_id_expr(self, lengths: tuple[int, ...]) -> pl.Expr:
        code_pos = pl.col(self._code_pos_name)
        cumulative = 0
        segment_id_expr: pl.Expr | None = None

        for index, length in enumerate(lengths):
            cumulative += length
            if segment_id_expr is None:
                segment_id_expr = pl.when(code_pos < cumulative).then(index)
            else:
                segment_id_expr = segment_id_expr.when(code_pos < cumulative).then(index)

        if segment_id_expr is None:
            raise ExecutionError("Internal error: empty length segment specification")

        return segment_id_expr.otherwise(len(lengths) - 1).cast(pl.Int64)

    def _ensure_segment_lengths_cover_groups(
        self,
        prepared_df: pl.DataFrame,
        lengths: tuple[int, ...],
    ) -> None:
        total_length = sum(lengths)
        uncovered = prepared_df.filter(pl.col(self._code_len_name) > total_length).head(1)
        if uncovered.height > 0:
            raise ExecutionError("segment lengths do not cover full group")
