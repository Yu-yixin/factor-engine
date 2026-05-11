from __future__ import annotations

from collections.abc import Sequence

import polars as pl

from factor_engine import FactorEngine
from factor_engine.runtime.config import RuntimeConfig
from factor_engine.runtime.schemas import FactorResult
from factor_engine.runtime.validation import validate_expressions, validate_market_frame


class BatchFactorRuntime:
    def __init__(
        self,
        config: RuntimeConfig | None = None,
        *,
        engine: FactorEngine | None = None,
    ) -> None:
        self.config = config or RuntimeConfig()
        self.engine = engine or FactorEngine(
            time_col=self.config.time_column,
            code_col=self.config.code_column,
        )

    def compute(
        self,
        frame: pl.DataFrame,
        expressions: Sequence[tuple[str, str]],
        *,
        latest_only: bool = False,
    ) -> FactorResult:
        validate_market_frame(frame, self.config)
        normalized_expressions = validate_expressions(expressions)
        result_frame = self.engine.evaluate_many(normalized_expressions, frame)
        return FactorResult.from_frame(
            result_frame,
            normalized_expressions,
            latest_only=latest_only,
        )
