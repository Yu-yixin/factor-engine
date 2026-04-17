from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Expr:
    """AST base class for all expression nodes."""


@dataclass(frozen=True)
class NumberNode(Expr):
    value: float


@dataclass(frozen=True)
class BooleanNode(Expr):
    value: bool


@dataclass(frozen=True)
class ListNode(Expr):
    items: list[Expr] = field(default_factory=list)


@dataclass(frozen=True)
class VariableNode(Expr):
    name: str


@dataclass(frozen=True)
class UnaryOpNode(Expr):
    operator: str
    operand: Expr


@dataclass(frozen=True)
class BinaryOpNode(Expr):
    left: Expr
    operator: str
    right: Expr


@dataclass(frozen=True)
class CallNode(Expr):
    name: str
    args: list[Expr] = field(default_factory=list)
    kwargs: dict[str, Expr] = field(default_factory=dict)
