import pytest

from factor_engine.ast_nodes import ListNode, NumberNode, VariableNode
from factor_engine.errors import ExecutionError
from factor_engine.executor_utils import (
    expect_numeric_literal,
    expect_positive_integer_list_literal,
    expect_positive_numeric_literal,
    expect_scalar_number,
    expect_window_at_least,
    temporary_helper_name,
)


def test_temporary_helper_name_uses_base_when_available():
    assert temporary_helper_name("__stage", {"close", "open"}) == "__stage"


def test_temporary_helper_name_prefixes_until_unique():
    assert temporary_helper_name("__stage", {"__stage", "___stage"}) == "____stage"


def test_temporary_helper_name_honors_reserved_names():
    assert temporary_helper_name("__stage", set(), reserved={"__stage"}) == "___stage"


def test_expect_numeric_literal_accepts_non_negative_integer_literal():
    assert expect_numeric_literal(NumberNode(3.0), "ts_mean") == 3
    assert expect_numeric_literal(NumberNode(0.0), "delay") == 0


@pytest.mark.parametrize("expr", [VariableNode("window"), NumberNode(-1.0), NumberNode(1.5)])
def test_expect_numeric_literal_rejects_invalid_values(expr):
    with pytest.raises(ExecutionError):
        expect_numeric_literal(expr, "ts_mean")


def test_expect_scalar_number_accepts_number_node():
    assert expect_scalar_number(NumberNode(1.25), "scale") == 1.25


def test_expect_positive_numeric_literal_requires_positive_integer():
    assert expect_positive_numeric_literal(NumberNode(2.0), "seg_mean") == 2
    with pytest.raises(ExecutionError, match="positive integer"):
        expect_positive_numeric_literal(NumberNode(0.0), "seg_mean")


def test_expect_positive_integer_list_literal_accepts_positive_integer_list():
    expr = ListNode([NumberNode(2.0), NumberNode(3.0)])
    assert expect_positive_integer_list_literal(expr, "seglen_mean") == (2, 3)


@pytest.mark.parametrize(
    "expr",
    [
        ListNode([]),
        ListNode([NumberNode(2.0), VariableNode("n")]),
        ListNode([NumberNode(2.5)]),
        ListNode([NumberNode(0.0)]),
    ],
)
def test_expect_positive_integer_list_literal_rejects_invalid_values(expr):
    with pytest.raises(ExecutionError, match="positive integer literal length list"):
        expect_positive_integer_list_literal(expr, "seglen_mean")


def test_expect_window_at_least_enforces_minimum():
    assert expect_window_at_least(NumberNode(4.0), "kurt", 4) == 4
    with pytest.raises(ExecutionError, match="window >= 4"):
        expect_window_at_least(NumberNode(3.0), "kurt", 4)
