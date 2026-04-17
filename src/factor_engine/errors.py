from __future__ import annotations

from dataclasses import dataclass


class FactorEngineError(Exception):
    """Base error for all factor engine exceptions."""


class LexerError(FactorEngineError):
    """Raised when tokenization fails."""


class ParserError(FactorEngineError):
    """Raised when parsing fails."""


class ValidationError(FactorEngineError):
    """Raised when semantic validation fails."""


class ExecutionError(FactorEngineError):
    """Raised when execution fails."""


class UnknownVariableError(ValidationError):
    """Raised when an expression references an unknown variable."""


class UnknownFunctionError(ValidationError):
    """Raised when an expression references an unsupported function."""


class ArgumentError(ValidationError):
    """Raised when function arguments are invalid."""


class UnsupportedOperatorError(ValidationError):
    """Raised when an unsupported operator is used."""


class WorkflowError(FactorEngineError):
    """Base error for workflow-layer IO/config/reporting failures."""


class WorkflowConfigError(WorkflowError):
    """Raised when workflow configuration or file schema is invalid."""


class WorkflowIOError(WorkflowError):
    """Raised when workflow helpers fail to read or write files."""


@dataclass(frozen=True)
class ExpressionFailure:
    """Structured failure payload for workflow batch reporting."""

    name: str | None
    expression: str | None
    stage: str
    error_type: str
    message: str
