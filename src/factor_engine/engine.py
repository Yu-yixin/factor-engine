from __future__ import annotations

from collections import OrderedDict
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

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
from factor_engine.executor import Executor
from factor_engine.dag import ExpressionDag
from factor_engine.errors import ArgumentError
from factor_engine.lifecycle import (
    normalize_helper_lifecycle_mode,
    normalize_lifecycle_mode,
    normalize_frame_projection_mode,
    normalize_fusion_mode,
    normalize_materialization_threshold_mode,
    normalize_output_attach_mode,
    normalize_planner_cse_mode,
)
from factor_engine.lexer import Lexer
from factor_engine.parser import Parser
from factor_engine.planner import BatchPlanningItem, ExecutionPlan, ExecutionPlanner
from factor_engine.profiling import ProfileArtifacts, StageLifecycleProfiler
from factor_engine.validator import ValidationResult, Validator


@dataclass(frozen=True)
class _CompiledCacheKey:
    expression: str
    schema_fingerprint: tuple[tuple[str, str], ...]
    time_col: str
    code_col: str


@dataclass(frozen=True)
class _CompiledArtifacts:
    expr: Expr
    validation: ValidationResult
    plan: ExecutionPlan
    compiled: pl.Expr | None = None


class _LruCache:
    def __init__(self, max_size: int):
        self.max_size = max_size
        self._entries: OrderedDict[object, object] = OrderedDict()

    def get(self, key: object) -> object | None:
        value = self._entries.get(key)
        if value is None:
            return None

        self._entries.move_to_end(key)
        return value

    def set(self, key: object, value: object) -> None:
        self._entries[key] = value
        self._entries.move_to_end(key)

        while len(self._entries) > self.max_size:
            self._entries.popitem(last=False)


def _schema_fingerprint(df: pl.DataFrame) -> tuple[tuple[str, str], ...]:
    return tuple((name, repr(dtype)) for name, dtype in df.schema.items())


def _clone_expr(expr: Expr) -> Expr:
    # The engine keeps cached AST nodes internally; cloning protects the cache
    # from accidental mutations when callers use the public parse() API.
    if isinstance(expr, NumberNode):
        return NumberNode(expr.value)
    if isinstance(expr, BooleanNode):
        return BooleanNode(expr.value)
    if isinstance(expr, ListNode):
        return ListNode(items=[_clone_expr(item) for item in expr.items])
    if isinstance(expr, VariableNode):
        return VariableNode(expr.name)
    if isinstance(expr, UnaryOpNode):
        return UnaryOpNode(operator=expr.operator, operand=_clone_expr(expr.operand))
    if isinstance(expr, BinaryOpNode):
        return BinaryOpNode(
            left=_clone_expr(expr.left),
            operator=expr.operator,
            right=_clone_expr(expr.right),
        )
    if isinstance(expr, CallNode):
        return CallNode(
            name=expr.name,
            args=[_clone_expr(arg) for arg in expr.args],
            kwargs={key: _clone_expr(value) for key, value in expr.kwargs.items()},
        )

    raise TypeError(f"Unsupported AST node for cloning: {type(expr).__name__}")


class FactorEngine:
    def __init__(
        self,
        time_col: str = "time",
        code_col: str = "code",
        cache_size: int = 256,
    ):
        if cache_size <= 0:
            raise ValueError("cache_size must be a positive integer")

        self.time_col = time_col
        self.code_col = code_col
        # Caches are instance-scoped on purpose: entries can be reused across
        # repeated evaluations, but they do not leak across engine lifecycles
        # or implicitly claim correctness for unrelated data versions.
        self._ast_cache = _LruCache(cache_size)
        self._validation_cache = _LruCache(cache_size)
        self._plan_cache = _LruCache(cache_size)
        self._compiled_expr_cache = _LruCache(cache_size)
        self._planner = ExecutionPlanner(
            time_col=self.time_col,
            code_col=self.code_col,
        )
        self.last_profile_summary = None
        self.last_profile_artifacts: ProfileArtifacts | None = None
        self.last_expression_dag: ExpressionDag | None = None

    def parse(self, expression: str):
        return _clone_expr(self._get_or_parse_ast(expression))

    def validate(self, expression: str, df: pl.DataFrame) -> ValidationResult:
        return self._get_or_validate(expression, df)

    def inspect_plan(self, expression: str, df: pl.DataFrame) -> dict[str, object]:
        expr = self._get_or_parse_ast(expression)
        validation = self._get_or_validate(expression, df)
        return self._planner.inspect_route(expr, validation)

    def inspect_dag(self, expressions: Sequence[tuple[str, str]], df: pl.DataFrame) -> dict[str, object]:
        dag_items = [
            (output_name, self._get_or_parse_ast(expression))
            for output_name, expression in expressions
        ]
        return self._planner.inspect_expression_dag(dag_items)

    def evaluate(
        self,
        expression: str,
        df: pl.DataFrame,
        output_name: str = "result",
    ) -> pl.DataFrame:
        artifacts = self._get_or_compile(expression, df)
        executor = Executor(
            df=df,
            time_col=self.time_col,
            code_col=self.code_col,
        )
        # Cache hits must preserve the exact execution contract; they only skip
        # redundant planning work and never change validation or runtime semantics.
        if artifacts.compiled is not None:
            return executor.evaluate_compiled(
                artifacts.compiled,
                output_name=output_name,
                validation=artifacts.validation,
            )
        return executor.evaluate(
            artifacts.expr,
            output_name=output_name,
            validation=artifacts.validation,
            plan=artifacts.plan,
        )

    def evaluate_many(
        self,
        expressions: Sequence[tuple[str, str]],
        df: pl.DataFrame,
        *,
        profiling: bool = False,
        profile_output_dir: str | Path | None = None,
        benchmark_name: str = "evaluate_many_stage_lifecycle",
        dataset_name: str = "dataframe",
        lifecycle: bool = False,
        lifecycle_mode: str | None = None,
        helper_lifecycle_mode: str | None = None,
        output_attach_mode: str | None = None,
        frame_projection_mode: str | None = None,
        materialization_threshold_mode: str | None = None,
        recomputation_guardrail_max_expansion: int = 0,
        planner_cse_mode: str | None = None,
        fusion_mode: str | None = None,
        dag_cse: bool = True,
    ) -> pl.DataFrame:
        try:
            resolved_lifecycle_mode = normalize_lifecycle_mode(
                lifecycle=lifecycle,
                lifecycle_mode=lifecycle_mode,
            )
            resolved_helper_lifecycle_mode = normalize_helper_lifecycle_mode(
                helper_lifecycle_mode=helper_lifecycle_mode,
            )
            resolved_output_attach_mode = normalize_output_attach_mode(
                output_attach_mode=output_attach_mode,
            )
            resolved_frame_projection_mode = normalize_frame_projection_mode(
                frame_projection_mode=frame_projection_mode,
            )
            resolved_materialization_threshold_mode = normalize_materialization_threshold_mode(
                materialization_threshold_mode=materialization_threshold_mode,
            )
            resolved_planner_cse_mode = normalize_planner_cse_mode(
                planner_cse_mode=planner_cse_mode,
            )
            resolved_fusion_mode = normalize_fusion_mode(
                fusion_mode=fusion_mode,
            )
        except ValueError as exc:
            raise ArgumentError(str(exc)) from exc

        profiler = (
            StageLifecycleProfiler(
                benchmark_name=benchmark_name,
                dataset_name=dataset_name,
                mode="evaluate_many",
                row_count=df.height,
                group_count=df.get_column(self.code_col).n_unique() if self.code_col in df.columns else 0,
                input_column_count=len(df.columns),
                expression_count=len(expressions),
            )
            if profiling
            else None
        )
        compiled_no_time_items: list[tuple[str, ValidationResult, pl.Expr]] = []
        compiled_time_items: list[tuple[str, Expr, ValidationResult, pl.Expr]] = []
        seen_names: set[str] = set()
        planning_items: list[BatchPlanningItem] = []

        for output_name, expression in expressions:
            if output_name in seen_names:
                raise ArgumentError(f"Duplicate output column name in evaluate_many(): {output_name}")
            seen_names.add(output_name)

            artifacts = self._get_or_compile(expression, df)
            if artifacts.validation.result_kind != "column":
                raise ArgumentError(
                    "evaluate_many() only supports column expressions in the current version"
                )
            planning_items.append(
                BatchPlanningItem(
                    output_name=output_name,
                    expr=artifacts.expr,
                    validation=artifacts.validation,
                    plan=artifacts.plan,
                )
            )
            if artifacts.compiled is not None:
                if artifacts.validation.profile.needs_time_order:
                    compiled_time_items.append(
                        (output_name, artifacts.expr, artifacts.validation, artifacts.compiled)
                    )
                else:
                    compiled_no_time_items.append((output_name, artifacts.validation, artifacts.compiled))

        self.last_expression_dag = self._planner.build_expression_dag(
            [(item.output_name, item.expr) for item in planning_items],
            materialization_threshold_mode=resolved_materialization_threshold_mode,
            recomputation_guardrail_max_expansion=recomputation_guardrail_max_expansion,
            planner_cse_mode=resolved_planner_cse_mode,
            fusion_mode=resolved_fusion_mode,
        )
        deferred_planning_items = [
            item
            for item in planning_items
            if item.plan.route != "compiled" or item.validation.profile.needs_time_order
        ]
        batch_plan = self._planner.with_materialization_policy(
            materialization_threshold_mode=resolved_materialization_threshold_mode,
            recomputation_guardrail_max_expansion=recomputation_guardrail_max_expansion,
            planner_cse_mode=resolved_planner_cse_mode,
            fusion_mode=resolved_fusion_mode,
        ).build_batch_plan(deferred_planning_items)

        result_df = df
        if compiled_no_time_items:
            executor = Executor(
                df=result_df,
                time_col=self.time_col,
                code_col=self.code_col,
                profile_recorder=profiler,
                lifecycle_mode=resolved_lifecycle_mode,
                helper_lifecycle_mode=resolved_helper_lifecycle_mode,
                output_attach_mode=resolved_output_attach_mode,
                frame_projection_mode=resolved_frame_projection_mode,
                materialization_threshold_mode=resolved_materialization_threshold_mode,
                recomputation_guardrail_max_expansion=(
                    recomputation_guardrail_max_expansion
                ),
                planner_cse_mode=resolved_planner_cse_mode,
                fusion_mode=resolved_fusion_mode,
                dag_cse_enabled=dag_cse,
            )
            result_df = executor.evaluate_many_compiled(compiled_no_time_items)

        if (
            compiled_time_items
            or batch_plan.segmented_items
            or batch_plan.staged_items
            or batch_plan.materialized_ordered_items
            or batch_plan.positional_items
        ):
            result_df = Executor(
                df=result_df,
                time_col=self.time_col,
                code_col=self.code_col,
                profile_recorder=profiler,
                lifecycle_mode=resolved_lifecycle_mode,
                helper_lifecycle_mode=resolved_helper_lifecycle_mode,
                output_attach_mode=resolved_output_attach_mode,
                frame_projection_mode=resolved_frame_projection_mode,
                materialization_threshold_mode=resolved_materialization_threshold_mode,
                recomputation_guardrail_max_expansion=(
                    recomputation_guardrail_max_expansion
                ),
                planner_cse_mode=resolved_planner_cse_mode,
                fusion_mode=resolved_fusion_mode,
                dag_cse_enabled=dag_cse,
            ).evaluate_many_planned(
                batch_plan,
                compiled_time_items=compiled_time_items,
            )

        appended_columns = [output_name for output_name, _ in expressions if output_name not in df.columns]
        result = result_df.select([*df.columns, *appended_columns])

        if profiler is not None:
            self.last_profile_summary = profiler.finish(result_column_count=len(appended_columns))
            target_dir = profile_output_dir or Path(__file__).resolve().parents[2] / "benchmarks"
            self.last_profile_artifacts = profiler.persist(target_dir)

        return result

    def _validate_expr(self, expr: Expr, df: pl.DataFrame) -> ValidationResult:
        return Validator(
            schema=df.schema,
            time_col=self.time_col,
            code_col=self.code_col,
        ).validate(expr)

    def _build_compiled_cache_key(self, expression: str, df: pl.DataFrame) -> _CompiledCacheKey:
        return _CompiledCacheKey(
            expression=expression,
            schema_fingerprint=_schema_fingerprint(df),
            time_col=self.time_col,
            code_col=self.code_col,
        )

    def _get_or_parse_ast(self, expression: str) -> Expr:
        cached = self._ast_cache.get(expression)
        if cached is not None:
            return cached

        tokens = Lexer(expression).tokenize()
        expr = Parser(tokens).parse()
        self._ast_cache.set(expression, expr)
        return expr

    def _get_or_validate(self, expression: str, df: pl.DataFrame) -> ValidationResult:
        cache_key = self._build_compiled_cache_key(expression, df)
        cached = self._validation_cache.get(cache_key)
        if cached is not None:
            return cached

        expr = self._get_or_parse_ast(expression)
        validation = self._validate_expr(expr, df)
        self._validation_cache.set(cache_key, validation)
        return validation

    def _get_or_plan(self, expression: str, df: pl.DataFrame) -> ExecutionPlan:
        cache_key = self._build_compiled_cache_key(expression, df)
        cached = self._plan_cache.get(cache_key)
        if cached is not None:
            return cached

        expr = self._get_or_parse_ast(expression)
        validation = self._get_or_validate(expression, df)
        plan = self._planner.build_plan(expr, validation)
        self._plan_cache.set(cache_key, plan)
        return plan

    def _get_or_compile(self, expression: str, df: pl.DataFrame) -> _CompiledArtifacts:
        cache_key = self._build_compiled_cache_key(expression, df)
        expr = self._get_or_parse_ast(expression)
        validation = self._get_or_validate(expression, df)
        plan = self._get_or_plan(expression, df)

        if validation.result_kind != "column":
            return _CompiledArtifacts(expr=expr, validation=validation, plan=plan)

        if plan.route != "compiled":
            # Segmented and staged routes depend on executor-scoped helper columns or
            # explicit materialization barriers, so v1 keeps them on the AST path.
            return _CompiledArtifacts(expr=expr, validation=validation, plan=plan)

        compiled = self._compiled_expr_cache.get(cache_key)
        if compiled is None:
            compiled = Executor(
                df=df,
                time_col=self.time_col,
                code_col=self.code_col,
            ).compile(expr)
            self._compiled_expr_cache.set(cache_key, compiled)

        return _CompiledArtifacts(expr=expr, validation=validation, plan=plan, compiled=compiled)
