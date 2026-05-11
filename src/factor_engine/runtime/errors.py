from __future__ import annotations


class RuntimeErrorBase(Exception):
    """Base class for Factor Engine runtime errors."""


class RuntimeValidationError(RuntimeErrorBase):
    """Raised when runtime inputs violate the runtime contract."""


class RuntimeDataError(RuntimeErrorBase):
    """Raised when runtime data is missing or insufficient."""


class RuntimeDependencyError(RuntimeErrorBase):
    """Raised when an optional runtime dependency is unavailable."""
