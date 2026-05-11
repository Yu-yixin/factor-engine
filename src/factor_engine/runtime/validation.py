from __future__ import annotations

from collections.abc import Sequence

import polars as pl

from factor_engine.runtime.config import RuntimeConfig
from factor_engine.runtime.errors import RuntimeValidationError


REQUIRED_MARKET_COLUMNS: tuple[str, ...] = (
    "symbol",
    "time",
    "open",
    "high",
    "low",
    "close",
    "volume",
)


def validate_expressions(expressions: Sequence[tuple[str, str]]) -> tuple[tuple[str, str], ...]:
    normalized = tuple(expressions)
    if not normalized:
        raise RuntimeValidationError("expressions must not be empty")
    for output_name, expression in normalized:
        if not output_name:
            raise RuntimeValidationError("expression output name must not be empty")
        if not expression:
            raise RuntimeValidationError("expression text must not be empty")
    return normalized


def validate_market_frame(df: pl.DataFrame, config: RuntimeConfig) -> None:
    missing = [column for column in REQUIRED_MARKET_COLUMNS if column not in df.columns]
    if missing:
        raise RuntimeValidationError(f"market frame missing required columns: {missing}")
    if config.code_column not in df.columns:
        raise RuntimeValidationError(f"market frame missing code column: {config.code_column}")
    if config.time_column not in df.columns:
        raise RuntimeValidationError(f"market frame missing time column: {config.time_column}")
    if config.strict and df.height == 0:
        raise RuntimeValidationError("market frame must not be empty")
