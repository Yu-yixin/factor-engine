import pytest

from factor_engine.errors import (
    ArgumentError,
    ExecutionError,
    FactorEngineError,
    LexerError,
    ParserError,
    UnknownFunctionError,
    UnknownVariableError,
    UnsupportedOperatorError,
    ValidationError,
    WorkflowConfigError,
    WorkflowError,
    WorkflowIOError,
)


def test_error_inheritance():
    assert issubclass(LexerError, FactorEngineError)
    assert issubclass(ParserError, FactorEngineError)
    assert issubclass(ValidationError, FactorEngineError)
    assert issubclass(ExecutionError, FactorEngineError)


def test_validation_subclasses():
    assert issubclass(UnknownVariableError, ValidationError)
    assert issubclass(UnknownFunctionError, ValidationError)
    assert issubclass(ArgumentError, ValidationError)
    assert issubclass(UnsupportedOperatorError, ValidationError)


def test_workflow_subclasses():
    assert issubclass(WorkflowError, FactorEngineError)
    assert issubclass(WorkflowConfigError, WorkflowError)
    assert issubclass(WorkflowIOError, WorkflowError)


def test_can_raise_custom_error():
    with pytest.raises(UnknownVariableError):
        raise UnknownVariableError("unknown variable: foo")
