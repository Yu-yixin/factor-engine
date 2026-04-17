import pytest

from factor_engine.ast_nodes import (
    BinaryOpNode,
    BooleanNode,
    CallNode,
    ListNode,
    NumberNode,
    UnaryOpNode,
    VariableNode,
)
from factor_engine.errors import ParserError
from factor_engine.lexer import Lexer
from factor_engine.parser import Parser


def parse_expression(text: str):
    tokens = Lexer(text).tokenize()
    return Parser(tokens).parse()


def test_parse_number():
    expr = parse_expression("1.5")
    assert expr == NumberNode(1.5)


def test_parse_variable():
    expr = parse_expression("close")
    assert expr == VariableNode("close")


def test_parse_unary_expression():
    expr = parse_expression("-close")
    assert expr == UnaryOpNode("-", VariableNode("close"))


def test_parse_binary_expression_with_precedence():
    expr = parse_expression("1 + 2 * 3")

    assert expr == BinaryOpNode(
        left=NumberNode(1.0),
        operator="+",
        right=BinaryOpNode(
            left=NumberNode(2.0),
            operator="*",
            right=NumberNode(3.0),
        ),
    )


def test_parse_parenthesized_expression():
    expr = parse_expression("(1 + 2) * 3")

    assert expr == BinaryOpNode(
        left=BinaryOpNode(
            left=NumberNode(1.0),
            operator="+",
            right=NumberNode(2.0),
        ),
        operator="*",
        right=NumberNode(3.0),
    )


def test_parse_function_call():
    expr = parse_expression("ts_mean(close, 5)")

    assert expr == CallNode(
        name="ts_mean",
        args=[VariableNode("close"), NumberNode(5.0)],
        kwargs={},
    )


def test_parse_function_call_with_kwargs():
    expr = parse_expression("rank(close, ascending=false, pct=true)")

    assert expr == CallNode(
        name="rank",
        args=[VariableNode("close")],
        kwargs={
            "ascending": BooleanNode(False),
            "pct": BooleanNode(True),
        },
    )


def test_parse_list_literal():
    expr = parse_expression("[3, 5, 2]")

    assert expr == ListNode(items=[NumberNode(3.0), NumberNode(5.0), NumberNode(2.0)])


def test_parse_seglen_mean_call():
    expr = parse_expression("seglen_mean(close, [3, 5, 2])")

    assert expr == CallNode(
        name="seglen_mean",
        args=[
            VariableNode("close"),
            ListNode(items=[NumberNode(3.0), NumberNode(5.0), NumberNode(2.0)]),
        ],
        kwargs={},
    )


def test_parse_comparison_expression():
    expr = parse_expression("volume >= 10")

    assert expr == BinaryOpNode(
        left=VariableNode("volume"),
        operator=">=",
        right=NumberNode(10.0),
    )


def test_parse_not_expression():
    expr = parse_expression("not is_null(close)")

    assert expr == UnaryOpNode(
        operator="not",
        operand=CallNode(name="is_null", args=[VariableNode("close")], kwargs={}),
    )


def test_parse_logical_and_expression():
    expr = parse_expression("close > open and volume > 0")

    assert expr == BinaryOpNode(
        left=BinaryOpNode(
            left=VariableNode("close"),
            operator=">",
            right=VariableNode("open"),
        ),
        operator="and",
        right=BinaryOpNode(
            left=VariableNode("volume"),
            operator=">",
            right=NumberNode(0.0),
        ),
    )


def test_parse_logical_or_expression():
    expr = parse_expression("is_null(close) or is_null(open)")

    assert expr == BinaryOpNode(
        left=CallNode(name="is_null", args=[VariableNode("close")], kwargs={}),
        operator="or",
        right=CallNode(name="is_null", args=[VariableNode("open")], kwargs={}),
    )


def test_parse_logical_precedence_not_before_and_before_or():
    expr = parse_expression("not a and b or c")

    assert expr == BinaryOpNode(
        left=BinaryOpNode(
            left=UnaryOpNode(operator="not", operand=VariableNode("a")),
            operator="and",
            right=VariableNode("b"),
        ),
        operator="or",
        right=VariableNode("c"),
    )


def test_parse_missing_right_paren():
    with pytest.raises(ParserError, match="Expected '\\)'"):
        parse_expression("(close + 1")


def test_parse_unexpected_token():
    with pytest.raises(ParserError):
        parse_expression("close + * 2")
