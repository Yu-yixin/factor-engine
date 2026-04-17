from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping

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
from factor_engine.errors import (
    ArgumentError,
    UnknownFunctionError,
    UnknownVariableError,
)
from factor_engine.registry import ExecutionKind, FunctionSpec, ResultKind, get_function_spec


ValueType = Literal["numeric", "boolean", "other", "unknown", "table"]


@dataclass(frozen=True)
class ExecutionProfile:
    result_kind: ResultKind
    execution_kind: ExecutionKind
    needs_code_group: bool = False
    needs_time_group: bool = False
    needs_time_order: bool = False

    @classmethod
    def column(
        cls,
        *,
        needs_code_group: bool = False,
        needs_time_group: bool = False,
        needs_time_order: bool = False,
    ) -> "ExecutionProfile":
        return cls(
            result_kind="column",
            execution_kind=_derive_execution_kind(
                result_kind="column",
                needs_code_group=needs_code_group,
                needs_time_group=needs_time_group,
                needs_time_order=needs_time_order,
            ),
            needs_code_group=needs_code_group,
            needs_time_group=needs_time_group,
            needs_time_order=needs_time_order,
        )

    @classmethod
    def table(
        cls,
        *,
        needs_code_group: bool = False,
        needs_time_group: bool = False,
        needs_time_order: bool = False,
    ) -> "ExecutionProfile":
        return cls(
            result_kind="table",
            execution_kind="table",
            needs_code_group=needs_code_group,
            needs_time_group=needs_time_group,
            needs_time_order=needs_time_order,
        )

    @classmethod
    def merge(
        cls,
        *profiles: "ExecutionProfile",
        result_kind: ResultKind = "column",
        self_needs_code_group: bool = False,
        self_needs_time_group: bool = False,
        self_needs_time_order: bool = False,
    ) -> "ExecutionProfile":
        needs_code_group = self_needs_code_group or any(
            profile.needs_code_group for profile in profiles
        )
        needs_time_group = self_needs_time_group or any(
            profile.needs_time_group for profile in profiles
        )
        needs_time_order = self_needs_time_order or any(
            profile.needs_time_order for profile in profiles
        )

        if result_kind == "table":
            return cls.table(
                needs_code_group=needs_code_group,
                needs_time_group=needs_time_group,
                needs_time_order=needs_time_order,
            )

        return cls.column(
            needs_code_group=needs_code_group,
            needs_time_group=needs_time_group,
            needs_time_order=needs_time_order,
        )


@dataclass(frozen=True)
class ValidationResult:
    result_kind: ResultKind
    profile: ExecutionProfile
    backend: str | None = None


def _derive_execution_kind(
    *,
    result_kind: ResultKind,
    needs_code_group: bool,
    needs_time_group: bool,
    needs_time_order: bool,
) -> ExecutionKind:
    if result_kind == "table":
        return "table"
    if needs_time_order or needs_code_group:
        return "time_series"
    if needs_time_group:
        return "cross_sectional"
    return "pointwise"


class Validator:
    def __init__(
        self,
        variables: set[str] | None = None,
        *,
        schema: Mapping[str, pl.DataType] | None = None,
        time_col: str = "time",
        code_col: str = "code",
    ):
        self.schema = dict(schema or {})
        self.variables = set(variables or self.schema.keys())
        self.time_col = time_col
        self.code_col = code_col

    def validate(self, expr: Expr) -> ValidationResult:
        # Validation establishes legality plus the AST-level execution profile.
        profile = self._validate_expr(expr, is_root=True)
        backend = None

        if isinstance(expr, CallNode):
            spec = get_function_spec(expr.name)
            if spec is not None:
                backend = spec.backend

        return ValidationResult(
            result_kind=profile.result_kind,
            profile=profile,
            backend=backend,
        )

    def _validate_expr(self, expr: Expr, *, is_root: bool) -> ExecutionProfile:
        if isinstance(expr, NumberNode):
            return ExecutionProfile.column()

        if isinstance(expr, BooleanNode):
            return ExecutionProfile.column()

        if isinstance(expr, ListNode):
            raise ArgumentError(
                "List literals can only be used as segmented length specifications"
            )

        if isinstance(expr, VariableNode):
            self._validate_variable(expr)
            return ExecutionProfile.column()

        if isinstance(expr, UnaryOpNode):
            operand_profile = self._validate_expr(expr.operand, is_root=False)
            self._ensure_column_result(
                operand_profile.result_kind,
                context=f"unary operator '{expr.operator}'",
            )
            if expr.operator == "not":
                self._ensure_boolean_expr(expr.operand, context="unary operator 'not'")
            return ExecutionProfile.merge(operand_profile)

        if isinstance(expr, BinaryOpNode):
            left_profile = self._validate_expr(expr.left, is_root=False)
            right_profile = self._validate_expr(expr.right, is_root=False)
            self._ensure_column_result(
                left_profile.result_kind,
                context=f"operator '{expr.operator}'",
            )
            self._ensure_column_result(
                right_profile.result_kind,
                context=f"operator '{expr.operator}'",
            )
            if expr.operator in {"and", "or"}:
                self._ensure_boolean_expr(expr.left, context=f"operator '{expr.operator}'")
                self._ensure_boolean_expr(expr.right, context=f"operator '{expr.operator}'")
            return ExecutionProfile.merge(left_profile, right_profile)

        if isinstance(expr, CallNode):
            return self._validate_call(expr, is_root=is_root)

        raise TypeError(f"Unsupported AST node: {type(expr).__name__}")

    def _validate_variable(self, expr: VariableNode) -> None:
        if expr.name not in self.variables:
            raise UnknownVariableError(f"Unknown variable: {expr.name}")

    def _validate_call(self, expr: CallNode, *, is_root: bool) -> ExecutionProfile:
        spec = get_function_spec(expr.name)
        if spec is None:
            raise UnknownFunctionError(f"Unknown function: {expr.name}")

        self._validate_argument_counts(spec, expr)
        self._validate_keyword_arguments(spec, expr)

        if spec.root_only and not is_root:
            raise ArgumentError(f"Function '{expr.name}' can only be used as the root expression")

        self._validate_required_columns(spec)
        self._validate_window_arguments(spec, expr)

        if spec.arg_rule == "variable_only":
            self._validate_variable_only_arguments(spec, expr)
        else:
            self._validate_column_arguments(spec, expr)

        self._validate_numeric_arguments(spec, expr)
        self._validate_boolean_arguments(spec, expr)
        self._validate_special_arguments(spec, expr)

        child_profiles = []
        for index, arg in enumerate(expr.args):
            if spec.window_kind == "segmented" and index == 1:
                continue
            if spec.arg_rule == "variable_only" and isinstance(arg, VariableNode):
                continue
            child_profiles.append(self._validate_expr(arg, is_root=False))
        child_profiles.extend(
            self._validate_expr(value, is_root=False) for value in expr.kwargs.values()
        )

        return ExecutionProfile.merge(
            *child_profiles,
            result_kind=spec.result_kind,
            self_needs_code_group=spec.needs_code_group,
            self_needs_time_group=spec.needs_time_group,
            self_needs_time_order=spec.needs_time_order,
        )

    def _validate_window_arguments(self, spec: FunctionSpec, expr: CallNode) -> None:
        if spec.window_kind != "segmented":
            return

        if len(expr.args) < 2:
            return

        if expr.name.startswith("seglen_"):
            self._expect_positive_integer_list_literal(expr.args[1], expr.name)
            return

        self._expect_positive_integer_literal(expr.args[1], expr.name)

    def _expect_positive_integer_literal(self, expr: Expr, func_name: str) -> int:
        if not isinstance(expr, NumberNode):
            raise ArgumentError(
                f"Function '{func_name}' requires a positive integer literal segment count"
            )

        value = expr.value
        if int(value) != value or value <= 0:
            raise ArgumentError(
                f"Function '{func_name}' requires a positive integer literal segment count"
            )

        return int(value)

    def _expect_positive_integer_list_literal(
        self,
        expr: Expr,
        func_name: str,
    ) -> tuple[int, ...]:
        if not isinstance(expr, ListNode) or not expr.items:
            raise ArgumentError(
                f"Function '{func_name}' requires a positive integer literal length list"
            )

        values: list[int] = []
        for item in expr.items:
            if not isinstance(item, NumberNode):
                raise ArgumentError(
                    f"Function '{func_name}' requires a positive integer literal length list"
                )
            value = item.value
            if int(value) != value or value <= 0:
                raise ArgumentError(
                    f"Function '{func_name}' requires a positive integer literal length list"
                )
            values.append(int(value))

        return tuple(values)

    def _validate_argument_counts(self, spec: FunctionSpec, expr: CallNode) -> None:
        arg_count = len(expr.args)
        if arg_count < spec.min_args or arg_count > spec.max_args:
            raise ArgumentError(
                f"Function '{expr.name}' expects between "
                f"{spec.min_args} and {spec.max_args} positional arguments, "
                f"got {arg_count}"
            )

    def _validate_keyword_arguments(self, spec: FunctionSpec, expr: CallNode) -> None:
        for key in expr.kwargs:
            if key not in spec.allowed_kwargs:
                raise ArgumentError(
                    f"Function '{expr.name}' does not support keyword argument: {key}"
                )

    def _validate_required_columns(self, spec: FunctionSpec) -> None:
        if spec.requires_time_col and self.time_col not in self.variables:
            raise ArgumentError(f"Function '{spec.name}' requires time column: {self.time_col}")

        if spec.requires_code_col and self.code_col not in self.variables:
            raise ArgumentError(f"Function '{spec.name}' requires code column: {self.code_col}")

    def _validate_variable_only_arguments(self, spec: FunctionSpec, expr: CallNode) -> None:
        for arg in expr.args:
            if not isinstance(arg, VariableNode):
                raise ArgumentError(
                    f"Function '{expr.name}' requires direct column reference arguments"
                )
            self._validate_variable(arg)

        for value in expr.kwargs.values():
            value_kind = self._validate_expr(value, is_root=False)
            self._ensure_column_result(
                value_kind.result_kind,
                context=f"keyword argument to function '{expr.name}'",
            )

    def _validate_column_arguments(self, spec: FunctionSpec, expr: CallNode) -> None:
        for index, arg in enumerate(expr.args):
            if spec.window_kind == "segmented" and index == 1:
                continue
            arg_kind = self._validate_expr(arg, is_root=False)
            self._ensure_column_result(
                arg_kind.result_kind,
                context=f"argument to function '{expr.name}'",
            )

        for value in expr.kwargs.values():
            value_kind = self._validate_expr(value, is_root=False)
            self._ensure_column_result(
                value_kind.result_kind,
                context=f"keyword argument to function '{expr.name}'",
            )

    def _validate_numeric_arguments(self, spec: FunctionSpec, expr: CallNode) -> None:
        for position in spec.numeric_arg_positions:
            if position >= len(expr.args):
                continue

            arg = expr.args[position]
            value_type = self._infer_value_type(arg)
            if value_type in {"boolean", "other"}:
                argument_label = (
                    f"column: {arg.name}" if isinstance(arg, VariableNode) else f"expression at position {position + 1}"
                )
                raise ArgumentError(
                    f"Function '{expr.name}' requires a numeric input {argument_label}"
                )

    def _validate_boolean_arguments(self, spec: FunctionSpec, expr: CallNode) -> None:
        for position in spec.boolean_arg_positions:
            if position >= len(expr.args):
                continue

            arg = expr.args[position]
            value_type = self._infer_value_type(arg)
            if value_type in {"numeric", "other", "table"}:
                argument_label = (
                    f"column: {arg.name}"
                    if isinstance(arg, VariableNode)
                    else f"expression at position {position + 1}"
                )
                raise ArgumentError(
                    f"Function '{expr.name}' requires a boolean input {argument_label}"
                )

    def _validate_special_arguments(self, spec: FunctionSpec, expr: CallNode) -> None:
        if spec.name == "fill_null":
            left_type = self._infer_value_type(expr.args[0])
            right_type = self._infer_value_type(expr.args[1])
            supported_types = {"numeric", "boolean", "unknown"}

            if left_type not in supported_types:
                raise ArgumentError("Function 'fill_null' requires a numeric or boolean input")
            if right_type not in supported_types:
                raise ArgumentError("Function 'fill_null' requires a numeric or boolean fill value")
            if (
                left_type != "unknown"
                and right_type != "unknown"
                and left_type != right_type
            ):
                raise ArgumentError(
                    "Function 'fill_null' requires the value and fill value to share the same type"
                )
            return

        if spec.name in {"group_demean", "group_zscore", "group_rank"}:
            if not isinstance(expr.args[1], VariableNode):
                raise ArgumentError(
                    f"Function '{expr.name}' requires a direct group column reference as the second argument"
                )
            self._validate_variable(expr.args[1])

    def _ensure_column_result(self, result_kind: ResultKind, *, context: str) -> None:
        if result_kind != "column":
            raise ArgumentError(f"Table-valued expressions cannot be used inside {context}")

    def _ensure_boolean_expr(self, expr: Expr, *, context: str) -> None:
        value_type = self._infer_value_type(expr)
        if value_type in {"numeric", "other", "table"}:
            argument_label = f"column: {expr.name}" if isinstance(expr, VariableNode) else "expression"
            raise ArgumentError(f"{context} requires a boolean input {argument_label}")

    def _infer_value_type(self, expr: Expr) -> ValueType:
        # The validator uses lightweight type inference so numeric-only functions can
        # accept derived numeric expressions while still rejecting obvious boolean/text inputs.
        if isinstance(expr, NumberNode):
            return "numeric"

        if isinstance(expr, BooleanNode):
            return "boolean"

        if isinstance(expr, ListNode):
            return "other"

        if isinstance(expr, VariableNode):
            dtype = self.schema.get(expr.name)
            if dtype is None:
                return "unknown"
            if dtype.is_numeric():
                return "numeric"
            if dtype == pl.Boolean:
                return "boolean"
            return "other"

        if isinstance(expr, UnaryOpNode):
            operand_type = self._infer_value_type(expr.operand)
            if expr.operator == "not":
                if operand_type == "boolean":
                    return "boolean"
                if operand_type == "table":
                    return "table"
                return "unknown"
            if operand_type == "numeric":
                return "numeric"
            if operand_type == "table":
                return "table"
            return "unknown"

        if isinstance(expr, BinaryOpNode):
            if expr.operator in {"+", "-", "*", "/"}:
                left_type = self._infer_value_type(expr.left)
                right_type = self._infer_value_type(expr.right)
                if left_type == "numeric" and right_type == "numeric":
                    return "numeric"
                if "table" in {left_type, right_type}:
                    return "table"
                if "other" in {left_type, right_type} or "boolean" in {left_type, right_type}:
                    return "other"
                return "unknown"

            if expr.operator in {">", "<", ">=", "<=", "=="}:
                return "boolean"
            if expr.operator in {"and", "or"}:
                return "boolean"

        if isinstance(expr, CallNode):
            if expr.name == "where" and len(expr.args) == 3:
                true_type = self._infer_value_type(expr.args[1])
                false_type = self._infer_value_type(expr.args[2])
                if true_type == false_type:
                    return true_type
                if "table" in {true_type, false_type}:
                    return "table"
                return "unknown"

            if expr.name == "fft":
                return "table"

            if expr.name == "fill_null" and len(expr.args) == 2:
                left_type = self._infer_value_type(expr.args[0])
                right_type = self._infer_value_type(expr.args[1])
                if left_type == right_type:
                    return left_type
                if left_type == "unknown":
                    return right_type
                if right_type == "unknown":
                    return left_type
                return "unknown"

            if expr.name == "is_null":
                return "boolean"

            if expr.name in {
                "abs",
                "argmax",
                "argmin",
                "clip",
                "corr",
                "cov",
                "delta",
                "demean",
                "group_demean",
                "group_rank",
                "group_zscore",
                "kurt",
                "pct_change",
                "rank",
                "seg_count",
                "seglen_count",
                "seglen_mean",
                "seglen_sum",
                "seg_mean",
                "seg_sum",
                "sign",
                "skew",
                "ts_count",
                "ts_max",
                "ts_median",
                "ts_mean",
                "ts_min",
                "ts_rank",
                "ts_std",
                "ts_sum",
                "zscore",
            }:
                return "numeric"

            if expr.name in {"seg_all", "seg_any", "seglen_all", "seglen_any", "ts_all", "ts_any"}:
                return "boolean"

            if expr.name == "delay" and expr.args:
                return self._infer_value_type(expr.args[0])

        return "unknown"
