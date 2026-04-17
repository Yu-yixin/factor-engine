from __future__ import annotations

from collections import OrderedDict
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

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
from factor_engine.physical_properties import (
    MATERIALIZATION_EFFECT,
    OperatorContract,
    PhysicalProperties,
    satisfies,
)
from factor_engine.errors import ArgumentError
from factor_engine.registry import build_operator_contract, get_function_spec
from factor_engine.validator import ExecutionProfile, ValidationResult


ExecutionRoute = Literal[
    "compiled",
    "segmented",
    "staged",
    "materialized_ordered",
    "positional_ordered",
    "table",
]


@dataclass(frozen=True)
class StagedCrossSectionStep:
    func_name: str
    group_col: str | None = None
    ascending: bool = False
    pct: bool = False


@dataclass(frozen=True)
class StagedChainPlan:
    source_expr: Expr
    steps: tuple[StagedCrossSectionStep, ...]


@dataclass(frozen=True)
class MaterializedOrderedPlan:
    func_name: str
    input_exprs: tuple[Expr, ...]
    window: int


@dataclass(frozen=True)
class ExecutionPlan:
    result_kind: str
    profile: ExecutionProfile
    route: ExecutionRoute
    staged: StagedChainPlan | None = None
    materialized_ordered: MaterializedOrderedPlan | None = None


@dataclass(frozen=True)
class BatchPlanningItem:
    output_name: str
    expr: Expr
    validation: ValidationResult
    plan: ExecutionPlan


@dataclass(frozen=True)
class BatchStagedSourceNode:
    cache_key: tuple
    expr_key: tuple
    expr: Expr
    consumer_outputs: tuple[str, ...]


@dataclass(frozen=True)
class BatchStagedPrefixNode:
    cache_key: tuple
    source_cache_key: tuple
    steps: tuple[StagedCrossSectionStep, ...]
    depends_on_cache_key: tuple
    consumer_outputs: tuple[str, ...]


@dataclass(frozen=True)
class BatchStagedNode:
    cache_key: tuple
    kind: Literal["source", "prefix"]
    depends_on_cache_key: tuple | None
    expr: Expr | None = None
    step: StagedCrossSectionStep | None = None
    steps: tuple[StagedCrossSectionStep, ...] = ()
    consumer_outputs: tuple[str, ...] = ()


@dataclass(frozen=True)
class BatchStagedOutputBinding:
    output_name: str
    cache_key: tuple


@dataclass(frozen=True)
class BatchExecutionPlan:
    compiled_items: tuple[BatchPlanningItem, ...]
    segmented_items: tuple[BatchPlanningItem, ...]
    staged_items: tuple[BatchPlanningItem, ...]
    materialized_ordered_items: tuple[BatchPlanningItem, ...]
    positional_items: tuple[BatchPlanningItem, ...]
    staged_sources: tuple[BatchStagedSourceNode, ...]
    staged_prefix_nodes: tuple[BatchStagedPrefixNode, ...]
    staged_nodes: tuple[BatchStagedNode, ...]
    staged_output_bindings: tuple[BatchStagedOutputBinding, ...]


class ExecutionPlanner:
    def __init__(self, *, time_col: str = "time", code_col: str = "code"):
        self.time_col = time_col
        self.code_col = code_col

    def build_plan(self, expr: Expr, validation: ValidationResult) -> ExecutionPlan:
        if validation.result_kind == "table":
            return ExecutionPlan(
                result_kind=validation.result_kind,
                profile=validation.profile,
                route="table",
            )

        if self.expr_uses_segmented_window(expr):
            return ExecutionPlan(
                result_kind=validation.result_kind,
                profile=validation.profile,
                route="segmented",
            )

        materialized_ordered = self.get_materialized_ordered_plan(expr)
        if materialized_ordered is not None:
            return ExecutionPlan(
                result_kind=validation.result_kind,
                profile=validation.profile,
                route="materialized_ordered",
                materialized_ordered=materialized_ordered,
            )

        if self.is_positional_ordered_root(expr):
            return ExecutionPlan(
                result_kind=validation.result_kind,
                profile=validation.profile,
                route="positional_ordered",
            )

        staged = self.get_staged_chain_plan(expr)
        if staged is not None:
            return ExecutionPlan(
                result_kind=validation.result_kind,
                profile=validation.profile,
                route="staged",
                staged=staged,
            )

        self._ensure_supported_property_compositions(expr)

        return ExecutionPlan(
            result_kind=validation.result_kind,
            profile=validation.profile,
            route="compiled",
        )

    def inspect_route(self, expr: Expr, validation: ValidationResult) -> dict[str, object]:
        plan = self.build_plan(expr, validation)
        details: dict[str, object] = {
            "route": plan.route,
            "result_kind": plan.result_kind,
            "needs_time_order": validation.profile.needs_time_order,
            "needs_time_group": validation.profile.needs_time_group,
            "needs_code_group": validation.profile.needs_code_group,
        }
        if isinstance(expr, CallNode):
            spec = get_function_spec(expr.name)
            if spec is not None:
                details["root_window_kind"] = spec.window_kind
        if plan.materialized_ordered is not None:
            details["materialized_func"] = plan.materialized_ordered.func_name
            details["materialized_input_count"] = len(plan.materialized_ordered.input_exprs)
            details["materialized_window"] = plan.materialized_ordered.window
        if plan.staged is not None:
            details["staged_steps"] = tuple(step.func_name for step in plan.staged.steps)
        return details

    def expr_uses_segmented_window(self, expr: Expr) -> bool:
        if isinstance(expr, CallNode):
            spec = get_function_spec(expr.name)
            if spec is not None and spec.window_kind == "segmented":
                return True
            return any(self.expr_uses_segmented_window(arg) for arg in expr.args) or any(
                self.expr_uses_segmented_window(value) for value in expr.kwargs.values()
            )

        if isinstance(expr, UnaryOpNode):
            return self.expr_uses_segmented_window(expr.operand)

        if isinstance(expr, BinaryOpNode):
            return self.expr_uses_segmented_window(expr.left) or self.expr_uses_segmented_window(
                expr.right
            )

        return False

    def expr_key(self, expr: Expr) -> tuple:
        if isinstance(expr, NumberNode):
            return ("number", expr.value)
        if isinstance(expr, BooleanNode):
            return ("boolean", expr.value)
        if isinstance(expr, ListNode):
            return ("list", tuple(self.expr_key(item) for item in expr.items))
        if isinstance(expr, VariableNode):
            return ("var", expr.name)
        if isinstance(expr, UnaryOpNode):
            return ("unary", expr.operator, self.expr_key(expr.operand))
        if isinstance(expr, BinaryOpNode):
            return (
                "binary",
                expr.operator,
                self.expr_key(expr.left),
                self.expr_key(expr.right),
            )
        if isinstance(expr, CallNode):
            return (
                "call",
                expr.name,
                tuple(self.expr_key(arg) for arg in expr.args),
                tuple(sorted((key, self.expr_key(value)) for key, value in expr.kwargs.items())),
            )

        raise TypeError(f"Unsupported AST node for execution-plan keying: {type(expr).__name__}")

    def staged_step_key(self, step: StagedCrossSectionStep) -> tuple:
        return (
            step.func_name,
            step.group_col,
            step.ascending,
            step.pct,
        )

    def staged_chain_key(self, plan: StagedChainPlan) -> tuple:
        return (
            self.expr_key(plan.source_expr),
            tuple(self.staged_step_key(step) for step in plan.steps),
        )

    def source_cache_key(self, expr: Expr) -> tuple:
        return ("source", self.expr_key(expr))

    def staged_prefix_cache_key(
        self,
        source_expr: Expr,
        steps: Sequence[StagedCrossSectionStep],
    ) -> tuple:
        return (
            "chain",
            self.expr_key(source_expr),
            tuple(self.staged_step_key(step) for step in steps),
        )

    def build_batch_plan(self, items: Sequence[BatchPlanningItem]) -> BatchExecutionPlan:
        compiled_items: list[BatchPlanningItem] = []
        segmented_items: list[BatchPlanningItem] = []
        staged_items: list[BatchPlanningItem] = []
        materialized_ordered_items: list[BatchPlanningItem] = []
        positional_items: list[BatchPlanningItem] = []
        staged_sources: OrderedDict[tuple, dict[str, object]] = OrderedDict()
        staged_prefix_nodes: OrderedDict[tuple, dict[str, object]] = OrderedDict()
        staged_output_bindings: list[BatchStagedOutputBinding] = []

        for item in items:
            if item.plan.route == "staged":
                staged_items.append(item)
                if item.plan.staged is None:
                    raise TypeError("Internal error: staged batch item is missing a staged chain plan")

                source_expr = item.plan.staged.source_expr
                source_expr_key = self.expr_key(source_expr)
                source_cache_key = ("source", source_expr_key)
                source_entry = staged_sources.setdefault(
                    source_cache_key,
                    {
                        "expr_key": source_expr_key,
                        "expr": source_expr,
                        "consumer_outputs": [],
                    },
                )
                source_entry["consumer_outputs"].append(item.output_name)

                prefix_steps: list[StagedCrossSectionStep] = []
                depends_on_cache_key = source_cache_key
                for step in item.plan.staged.steps:
                    prefix_steps.append(step)
                    prefix_cache_key = self.staged_prefix_cache_key(source_expr, prefix_steps)
                    prefix_entry = staged_prefix_nodes.setdefault(
                        prefix_cache_key,
                        {
                            "source_cache_key": source_cache_key,
                            "steps": tuple(prefix_steps),
                            "depends_on_cache_key": depends_on_cache_key,
                            "consumer_outputs": [],
                        },
                    )
                    prefix_entry["consumer_outputs"].append(item.output_name)
                    depends_on_cache_key = prefix_cache_key

                staged_output_bindings.append(
                    BatchStagedOutputBinding(
                        output_name=item.output_name,
                        cache_key=depends_on_cache_key,
                    )
                )
                continue

            if item.plan.route == "segmented":
                segmented_items.append(item)
                continue

            if item.plan.route == "materialized_ordered":
                materialized_ordered_items.append(item)
                continue

            if item.plan.route == "positional_ordered":
                positional_items.append(item)
                continue

            compiled_items.append(item)

        staged_source_nodes = tuple(
            BatchStagedSourceNode(
                cache_key=cache_key,
                expr_key=entry["expr_key"],
                expr=entry["expr"],
                consumer_outputs=tuple(entry["consumer_outputs"]),
            )
            for cache_key, entry in staged_sources.items()
        )
        staged_prefix_node_items = tuple(
            BatchStagedPrefixNode(
                cache_key=cache_key,
                source_cache_key=entry["source_cache_key"],
                steps=entry["steps"],
                depends_on_cache_key=entry["depends_on_cache_key"],
                consumer_outputs=tuple(entry["consumer_outputs"]),
            )
            for cache_key, entry in staged_prefix_nodes.items()
        )
        staged_nodes = tuple(
            [
                *(
                    BatchStagedNode(
                        cache_key=node.cache_key,
                        kind="source",
                        depends_on_cache_key=None,
                        expr=node.expr,
                        consumer_outputs=node.consumer_outputs,
                    )
                    for node in staged_source_nodes
                ),
                *(
                    BatchStagedNode(
                        cache_key=node.cache_key,
                        kind="prefix",
                        depends_on_cache_key=node.depends_on_cache_key,
                        step=node.steps[-1],
                        steps=node.steps,
                        consumer_outputs=node.consumer_outputs,
                    )
                    for node in staged_prefix_node_items
                ),
            ]
        )

        return BatchExecutionPlan(
            compiled_items=tuple(compiled_items),
            segmented_items=tuple(segmented_items),
            staged_items=tuple(staged_items),
            materialized_ordered_items=tuple(materialized_ordered_items),
            positional_items=tuple(positional_items),
            staged_sources=staged_source_nodes,
            staged_prefix_nodes=staged_prefix_node_items,
            staged_nodes=staged_nodes,
            staged_output_bindings=tuple(staged_output_bindings),
        )

    def is_positional_ordered_root(self, expr: Expr) -> bool:
        if not isinstance(expr, CallNode):
            return False

        spec = get_function_spec(expr.name)
        if spec is None or spec.window_kind != "positional":
            return False
        if len(expr.args) != 2 or expr.kwargs:
            return False
        if self.expr_uses_segmented_window(expr.args[0]):
            return False

        return self._read_positive_integer_literal(expr.args[1]) is not None

    def get_materialized_ordered_plan(self, expr: Expr) -> MaterializedOrderedPlan | None:
        if not isinstance(expr, CallNode):
            return None

        parent_contract = self._build_operator_contract(expr)
        if parent_contract is None or not parent_contract.accepts_materialized_input:
            return None
        single_input_plan = self._get_single_input_materialized_ordered_plan(
            expr,
            parent_contract=parent_contract,
        )
        if single_input_plan is not None:
            return single_input_plan

        return self._get_binary_materialized_ordered_plan(
            expr,
            parent_contract=parent_contract,
        )

    def _get_single_input_materialized_ordered_plan(
        self,
        expr: CallNode,
        *,
        parent_contract: OperatorContract,
    ) -> MaterializedOrderedPlan | None:
        if not parent_contract.is_single_input_ordered_root:
            return None
        if len(expr.args) != 2 or expr.kwargs:
            return None
        if self.expr_uses_segmented_window(expr.args[0]):
            return None

        child_properties = self._infer_physical_properties(expr.args[0])
        if not (
            self._requires_materialization(child_properties, parent_contract)
            and self._is_cross_or_grouped(child_properties)
        ):
            return None

        window = self._read_positive_integer_literal(expr.args[1])
        minimum_window = self._minimum_window_for_single_input_ordered_root(expr.name)
        if window is None or window < minimum_window:
            return None

        return MaterializedOrderedPlan(
            func_name=expr.name,
            input_exprs=(expr.args[0],),
            window=window,
        )

    def _get_binary_materialized_ordered_plan(
        self,
        expr: CallNode,
        *,
        parent_contract: OperatorContract,
    ) -> MaterializedOrderedPlan | None:
        if expr.name not in {"corr", "cov"}:
            return None
        if len(expr.args) != 3 or expr.kwargs:
            return None
        if self.expr_uses_segmented_window(expr.args[0]) or self.expr_uses_segmented_window(expr.args[1]):
            return None

        left_properties = self._infer_physical_properties(expr.args[0])
        right_properties = self._infer_physical_properties(expr.args[1])
        if not (
            self._requires_materialization(left_properties, parent_contract)
            or self._requires_materialization(right_properties, parent_contract)
        ):
            return None

        window = self._read_positive_integer_literal(expr.args[2])
        if window is None or window < 2:
            return None

        return MaterializedOrderedPlan(
            func_name=expr.name,
            input_exprs=(expr.args[0], expr.args[1]),
            window=window,
        )

    def get_staged_chain_plan(self, expr: Expr) -> StagedChainPlan | None:
        staged_root = self._match_staged_root(expr)
        if staged_root is None:
            return None

        parent_contract = self._build_operator_contract(expr)
        if parent_contract is None:
            return None

        inner_chain = self.get_staged_chain_plan(staged_root.source_expr)
        child_properties = (
            MATERIALIZATION_EFFECT
            if inner_chain is not None
            else self._infer_physical_properties(staged_root.source_expr)
        )
        if self._requires_materialization(child_properties, parent_contract):
            if not parent_contract.accepts_materialized_input:
                return None
            return StagedChainPlan(
                source_expr=staged_root.source_expr,
                steps=(staged_root.step,),
            )

        if inner_chain is not None:
            return StagedChainPlan(
                source_expr=inner_chain.source_expr,
                steps=(*inner_chain.steps, staged_root.step),
            )

        return None

    def _match_staged_root(self, expr: Expr) -> _MatchedStagedRoot | None:
        if not isinstance(expr, CallNode):
            return None

        if expr.name in {"demean", "zscore"}:
            if len(expr.args) != 1 or expr.kwargs:
                return None
            return _MatchedStagedRoot(
                source_expr=expr.args[0],
                step=StagedCrossSectionStep(expr.name),
            )

        if expr.name == "rank":
            if len(expr.args) != 1:
                return None
            return _MatchedStagedRoot(
                source_expr=expr.args[0],
                step=StagedCrossSectionStep(
                    expr.name,
                    ascending=self._read_boolean_kwarg(
                        expr,
                        kwarg_name="ascending",
                        default=False,
                    ),
                    pct=self._read_boolean_kwarg(
                        expr,
                        kwarg_name="pct",
                        default=False,
                    ),
                ),
            )

        if expr.name in {"group_demean", "group_zscore"}:
            if len(expr.args) != 2 or expr.kwargs:
                return None
            group_expr = expr.args[1]
            if not isinstance(group_expr, VariableNode):
                return None
            return _MatchedStagedRoot(
                source_expr=expr.args[0],
                step=StagedCrossSectionStep(
                    expr.name,
                    group_col=group_expr.name,
                ),
            )

        if expr.name == "group_rank":
            if len(expr.args) != 2:
                return None
            group_expr = expr.args[1]
            if not isinstance(group_expr, VariableNode):
                return None
            return _MatchedStagedRoot(
                source_expr=expr.args[0],
                step=StagedCrossSectionStep(
                    expr.name,
                    group_col=group_expr.name,
                    ascending=self._read_boolean_kwarg(
                        expr,
                        kwarg_name="ascending",
                        default=False,
                    ),
                    pct=self._read_boolean_kwarg(
                        expr,
                        kwarg_name="pct",
                        default=False,
                    ),
                ),
            )

        return None

    def _read_boolean_kwarg(
        self,
        expr: CallNode,
        *,
        kwarg_name: str,
        default: bool,
    ) -> bool:
        value = expr.kwargs.get(kwarg_name)
        if value is None:
            return default
        if not isinstance(value, BooleanNode):
            return default
        return value.value

    def _read_positive_integer_literal(self, expr: Expr) -> int | None:
        if not isinstance(expr, NumberNode):
            return None
        value = expr.value
        if int(value) != value or value <= 0:
            return None
        return int(value)

    def _build_operator_contract(self, expr: Expr) -> OperatorContract | None:
        if not isinstance(expr, CallNode):
            return None

        spec = get_function_spec(expr.name)
        if spec is None:
            return None

        group_col = None
        if expr.name in {"group_demean", "group_zscore", "group_rank"}:
            if len(expr.args) >= 2 and isinstance(expr.args[1], VariableNode):
                group_col = expr.args[1].name

        return build_operator_contract(
            spec,
            time_col=self.time_col,
            code_col=self.code_col,
            group_col=group_col,
        )

    def _infer_physical_properties(self, expr: Expr) -> PhysicalProperties:
        if isinstance(expr, (NumberNode, BooleanNode, VariableNode, ListNode)):
            return PhysicalProperties()

        if isinstance(expr, UnaryOpNode):
            return self._infer_physical_properties(expr.operand)

        if isinstance(expr, BinaryOpNode):
            return self._merge_preserved_properties(
                self._infer_physical_properties(expr.left),
                self._infer_physical_properties(expr.right),
            )

        if isinstance(expr, CallNode):
            contract = self._build_operator_contract(expr)
            if contract is not None:
                return contract.produced_properties()

            return self._properties_from_profile(self._infer_execution_profile(expr))

        raise TypeError(f"Unsupported AST node for physical-property inference: {type(expr).__name__}")

    def _properties_from_profile(self, profile: ExecutionProfile) -> PhysicalProperties:
        if profile.needs_code_group or profile.needs_time_order:
            return PhysicalProperties(
                partition_by=(self.code_col,),
                order_by=(self.time_col,),
            )
        if profile.needs_time_group:
            return PhysicalProperties(partition_by=(self.time_col,))
        return PhysicalProperties()

    def _merge_preserved_properties(
        self,
        left: PhysicalProperties,
        right: PhysicalProperties,
    ) -> PhysicalProperties:
        if left.is_plain():
            return right
        if right.is_plain():
            return left
        if left == right:
            return left
        return PhysicalProperties()

    def _requires_materialization(
        self,
        child_properties: PhysicalProperties,
        parent_contract: OperatorContract,
    ) -> bool:
        return not satisfies(child_properties, parent_contract.requires)

    def _is_cross_or_grouped(self, properties: PhysicalProperties) -> bool:
        return (
            self.time_col in properties.partition_by
            and not properties.order_by
            and properties.segment is None
        )

    def _minimum_window_for_single_input_ordered_root(self, func_name: str) -> int:
        if func_name == "skew":
            return 3
        if func_name == "kurt":
            return 4
        return 1

    def _ensure_supported_property_compositions(self, expr: Expr) -> None:
        if isinstance(expr, (NumberNode, BooleanNode, VariableNode, ListNode)):
            return

        if isinstance(expr, UnaryOpNode):
            self._ensure_supported_property_compositions(expr.operand)
            return

        if isinstance(expr, BinaryOpNode):
            self._ensure_supported_property_compositions(expr.left)
            self._ensure_supported_property_compositions(expr.right)
            return

        if not isinstance(expr, CallNode):
            raise TypeError(f"Unsupported AST node for composition validation: {type(expr).__name__}")

        contract = self._build_operator_contract(expr)
        if contract is None:
            return

        spec = get_function_spec(expr.name)
        if spec is None:
            return

        for index, child in enumerate(expr.args):
            if spec.window_kind == "segmented" and index == 1:
                continue
            self._ensure_supported_property_compositions(child)
            child_properties = self._infer_physical_properties(child)
            if not self._requires_materialization(child_properties, contract):
                continue
            if contract.accepts_materialized_input:
                raise ArgumentError(
                    f"Unsupported property mismatch for '{expr.name}': materialization route is not implemented for this operator family"
                )
            raise ArgumentError(
                f"Unsupported property mismatch for '{expr.name}': child properties do not satisfy parent requirements"
            )

        for child in expr.kwargs.values():
            self._ensure_supported_property_compositions(child)

    def _infer_execution_profile(self, expr: Expr) -> ExecutionProfile:
        if isinstance(expr, (NumberNode, BooleanNode, VariableNode)):
            return ExecutionProfile.column()

        if isinstance(expr, ListNode):
            raise TypeError("List literals are not valid standalone execution-profile inputs")

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

        raise TypeError(f"Unsupported AST node for execution planning: {type(expr).__name__}")


@dataclass(frozen=True)
class _MatchedStagedRoot:
    source_expr: Expr
    step: StagedCrossSectionStep
