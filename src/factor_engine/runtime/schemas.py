from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import polars as pl


@dataclass(frozen=True)
class FactorResult:
    frame: pl.DataFrame
    latest: dict[str, Any] | None
    expressions: tuple[tuple[str, str], ...]

    @classmethod
    def from_frame(
        cls,
        frame: pl.DataFrame,
        expressions: tuple[tuple[str, str], ...],
        *,
        latest_only: bool = True,
    ) -> "FactorResult":
        latest = frame.tail(1).to_dicts()[0] if latest_only and frame.height > 0 else None
        return cls(frame=frame, latest=latest, expressions=expressions)
