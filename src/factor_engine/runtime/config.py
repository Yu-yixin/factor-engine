from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeConfig:
    code_column: str = "symbol"
    time_column: str = "time"
    window_size: int = 500
    strict: bool = True

    def __post_init__(self) -> None:
        if not self.code_column:
            raise ValueError("code_column must not be empty")
        if not self.time_column:
            raise ValueError("time_column must not be empty")
        if self.window_size <= 0:
            raise ValueError("window_size must be a positive integer")
