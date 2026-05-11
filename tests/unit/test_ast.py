from factor_engine.ast_nodes import (
    BinaryOpNode,
    BooleanNode,
    CallNode,
    NumberNode,
    UnaryOpNode,
    VariableNode,
)


def test_number_node():
    node = NumberNode(1.5)
    assert node.value == 1.5


def test_boolean_node():
    node = BooleanNode(True)
    assert node.value is True


def test_variable_node():
    node = VariableNode("close")
    assert node.name == "close"


def test_unary_op_node():
    node = UnaryOpNode("-", VariableNode("close"))
    assert node.operator == "-"
    assert node.operand == VariableNode("close")


def test_binary_op_node():
    node = BinaryOpNode(
        left=VariableNode("close"),
        operator="/",
        right=NumberNode(2.0),
    )
    assert node.left == VariableNode("close")
    assert node.operator == "/"
    assert node.right == NumberNode(2.0)


def test_call_node_with_args_and_kwargs():
    node = CallNode(
        name="rank",
        args=[VariableNode("close")],
        kwargs={
            "ascending": BooleanNode(False),
            "pct": BooleanNode(True),
        },
    )


    assert node.name == "rank"
    assert len(node.args) == 1
    assert "ascending" in node.kwargs
    assert "pct" in node.kwargs
