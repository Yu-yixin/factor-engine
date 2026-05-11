from __future__ import annotations

from factor_engine.ast_nodes import Expr, ListNode, NumberNode
from factor_engine.errors import ExecutionError


def temporary_helper_name(
    base_name: str,
    existing_names: set[str],
    *,
    reserved: set[str] | None = None,
) -> str:
    used_names = set(existing_names)
    if reserved is not None:
        used_names.update(reserved)

    candidate = base_name
    while candidate in used_names:
        candidate = f"_{candidate}"
    return candidate


def expect_numeric_literal(expr: Expr, func_name: str) -> int:
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


def expect_scalar_number(expr: Expr, func_name: str) -> float:
    if not isinstance(expr, NumberNode):
        raise ExecutionError(f"Function '{func_name}' requires a scalar numeric literal")
    return float(expr.value)


def expect_positive_numeric_literal(expr: Expr, func_name: str) -> int:
    value = expect_numeric_literal(expr, func_name)
    if value <= 0:
        raise ExecutionError(f"Function '{func_name}' requires a positive integer argument")
    return value


def expect_positive_integer_list_literal(
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


def expect_window_at_least(expr: Expr, func_name: str, minimum: int) -> int:
    window = expect_numeric_literal(expr, func_name)
    if window < minimum:
        raise ExecutionError(f"Function '{func_name}' requires window >= {minimum}")
    return window
