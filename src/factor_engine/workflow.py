from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import polars as pl

from factor_engine.engine import FactorEngine
from factor_engine.errors import (
    ArgumentError,
    ExecutionError,
    ExpressionFailure,
    LexerError,
    ParserError,
    ValidationError,
    WorkflowConfigError,
    WorkflowIOError,
)
from factor_engine.run_summary import RunSummary, build_run_summary


@dataclass(frozen=True)
class BatchExpression:
    name: str
    expression: str


@dataclass(frozen=True)
class BatchEvaluationReport:
    result_df: pl.DataFrame
    successes: list[BatchExpression]
    failures: list[ExpressionFailure]

    @property
    def has_failures(self) -> bool:
        return bool(self.failures)


@dataclass(frozen=True)
class WorkflowRun:
    result_df: pl.DataFrame
    summary: RunSummary


@dataclass(frozen=True)
class WorkflowReportRun:
    report: BatchEvaluationReport
    summary: RunSummary


@dataclass(frozen=True)
class _BatchExecutionTiming:
    validate_time_seconds: float
    execute_time_seconds: float


def _strip_yaml_scalar(value: str) -> str:
    stripped = value.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in {'"', "'"}:
        return stripped[1:-1]
    return stripped


def _normalize_expression_items(payload: Any, *, source: Path) -> list[BatchExpression]:
    if not isinstance(payload, dict):
        raise ValueError(f"Expression file '{source}' must contain a top-level mapping")

    expressions = payload.get("expressions")
    if not isinstance(expressions, list):
        raise ValueError(f"Expression file '{source}' must contain 'expressions' as a list")

    items: list[BatchExpression] = []
    seen_names: set[str] = set()

    for index, item in enumerate(expressions, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Expression entry #{index} in '{source}' must be a mapping")

        name = item.get("name")
        expression = item.get("expression")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Expression entry #{index} in '{source}' requires a non-empty string 'name'")
        if not isinstance(expression, str) or not expression.strip():
            raise ValueError(
                f"Expression entry #{index} in '{source}' requires a non-empty string 'expression'"
            )
        if name in seen_names:
            raise ValueError(f"Duplicate expression name in '{source}': {name}")

        seen_names.add(name)
        items.append(BatchExpression(name=name, expression=expression))

    return items


def _load_yaml_expression_payload(text: str, *, source: Path) -> dict[str, Any]:
    items: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped == "expressions:":
            continue

        if stripped.startswith("- "):
            current = {}
            items.append(current)
            stripped = stripped[2:].strip()
            if not stripped:
                continue
        elif current is None:
            raise ValueError(
                f"YAML expression file '{source}' must start with 'expressions:' and list items"
            )

        if ":" not in stripped:
            raise ValueError(f"Invalid YAML entry in '{source}': {stripped}")

        key, value = stripped.split(":", 1)
        key = key.strip()
        if key not in {"name", "expression"}:
            raise ValueError(f"Unsupported YAML key in '{source}': {key}")
        current[key] = _strip_yaml_scalar(value)

    return {"expressions": items}


def load_expression_file(path: str | Path) -> list[BatchExpression]:
    source = Path(path)
    try:
        text = source.read_text(encoding="utf-8")
    except OSError as exc:
        raise WorkflowIOError(f"Failed to read expression file '{source}': {exc}") from exc

    try:
        if source.suffix.lower() == ".json":
            payload = json.loads(text)
        elif source.suffix.lower() in {".yaml", ".yml"}:
            payload = _load_yaml_expression_payload(text, source=source)
        else:
            raise WorkflowConfigError(f"Unsupported expression file format for '{source}'")
    except json.JSONDecodeError as exc:
        raise WorkflowConfigError(f"Invalid JSON in '{source}': {exc.msg}") from exc
    except WorkflowConfigError:
        raise
    except ValueError as exc:
        raise WorkflowConfigError(str(exc)) from exc

    try:
        return _normalize_expression_items(payload, source=source)
    except ValueError as exc:
        raise WorkflowConfigError(str(exc)) from exc


def evaluate_expression_file(
    path: str | Path,
    df: pl.DataFrame,
    *,
    engine: FactorEngine | None = None,
) -> pl.DataFrame:
    batch_items = load_expression_file(path)
    active_engine = engine or FactorEngine()
    return active_engine.evaluate_many(
        [(item.name, item.expression) for item in batch_items],
        df,
    )


def _classify_exception_stage(exc: Exception) -> str:
    if isinstance(exc, WorkflowIOError):
        return "io"
    if isinstance(exc, WorkflowConfigError):
        return "config"
    if isinstance(exc, LexerError):
        return "lexer"
    if isinstance(exc, ParserError):
        return "parser"
    if isinstance(exc, ValidationError):
        return "validation"
    if isinstance(exc, ExecutionError):
        return "execution"
    return "unknown"


def _build_expression_failure(
    *,
    name: str | None,
    expression: str | None,
    exc: Exception,
) -> ExpressionFailure:
    return ExpressionFailure(
        name=name,
        expression=expression,
        stage=_classify_exception_stage(exc),
        error_type=type(exc).__name__,
        message=str(exc),
    )


def _count_codes(df: pl.DataFrame, *, code_col: str) -> int | None:
    if code_col not in df.columns:
        return None
    return int(df.get_column(code_col).n_unique())


def _normalize_data_path(data_path: str | Path | None) -> str:
    if data_path is None:
        return "in-memory://dataframe"
    return str(data_path)


def _evaluate_expression_batch_report_internal(
    expressions: list[BatchExpression],
    df: pl.DataFrame,
    *,
    engine: FactorEngine | None = None,
) -> tuple[BatchEvaluationReport, _BatchExecutionTiming]:
    active_engine = engine or FactorEngine()
    result_df = df
    successes: list[BatchExpression] = []
    failures: list[ExpressionFailure] = []
    validated_items: list[BatchExpression] = []
    seen_names: set[str] = set()
    has_duplicate_names = False
    validate_time_seconds = 0.0
    execute_time_seconds = 0.0

    for item in expressions:
        if item.name in seen_names:
            has_duplicate_names = True
        seen_names.add(item.name)

        try:
            validate_start = time.perf_counter()
            validation = active_engine.validate(item.expression, df)
            validate_time_seconds += time.perf_counter() - validate_start
        except Exception as exc:
            failures.append(
                _build_expression_failure(
                    name=item.name,
                    expression=item.expression,
                    exc=exc,
                )
            )
            continue

        if validation.result_kind != "column":
            failures.append(
                _build_expression_failure(
                    name=item.name,
                    expression=item.expression,
                    exc=ArgumentError(
                        "evaluate_many() only supports column expressions in the current version"
                    ),
                )
            )
            continue

        validated_items.append(item)

    if validated_items and not has_duplicate_names:
        try:
            execute_start = time.perf_counter()
            result_df = active_engine.evaluate_many(
                [(item.name, item.expression) for item in validated_items],
                df,
            )
            execute_time_seconds += time.perf_counter() - execute_start
            successes.extend(validated_items)
            return (
                BatchEvaluationReport(
                    result_df=result_df,
                    successes=successes,
                    failures=failures,
                ),
                _BatchExecutionTiming(
                    validate_time_seconds=validate_time_seconds,
                    execute_time_seconds=execute_time_seconds,
                ),
            )
        except Exception:
            # Fall back to per-expression execution so mixed-good/bad batches keep
            # their current identity-preserving failure summary.
            pass

    for item in validated_items:
        try:
            execute_start = time.perf_counter()
            evaluated = active_engine.evaluate(item.expression, df, output_name=item.name)
            execute_time_seconds += time.perf_counter() - execute_start
        except Exception as exc:
            failures.append(
                _build_expression_failure(
                    name=item.name,
                    expression=item.expression,
                    exc=exc,
                )
            )
            continue

        result_df = result_df.with_columns(evaluated[item.name])
        successes.append(item)

    return (
        BatchEvaluationReport(
            result_df=result_df,
            successes=successes,
            failures=failures,
        ),
        _BatchExecutionTiming(
            validate_time_seconds=validate_time_seconds,
            execute_time_seconds=execute_time_seconds,
        ),
    )


def evaluate_expression_batch_report(
    expressions: list[BatchExpression],
    df: pl.DataFrame,
    *,
    engine: FactorEngine | None = None,
) -> BatchEvaluationReport:
    report, _timing = _evaluate_expression_batch_report_internal(expressions, df, engine=engine)
    return report


def evaluate_expression_file_report(
    path: str | Path,
    df: pl.DataFrame,
    *,
    engine: FactorEngine | None = None,
) -> BatchEvaluationReport:
    try:
        expressions = load_expression_file(path)
    except Exception as exc:
        return BatchEvaluationReport(
            result_df=df,
            successes=[],
            failures=[
                _build_expression_failure(
                    name=None,
                    expression=None,
                    exc=exc,
                )
            ],
        )

    return evaluate_expression_batch_report(expressions, df, engine=engine)


def evaluate_expression_file_with_summary(
    path: str | Path,
    df: pl.DataFrame,
    *,
    engine: FactorEngine | None = None,
    data_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> WorkflowRun:
    total_start = time.perf_counter()
    active_engine = engine or FactorEngine()

    load_start = time.perf_counter()
    batch_items = load_expression_file(path)
    load_time_seconds = time.perf_counter() - load_start

    execute_start = time.perf_counter()
    result_df = active_engine.evaluate_many(
        [(item.name, item.expression) for item in batch_items],
        df,
    )
    execute_time_seconds = time.perf_counter() - execute_start
    total_time_seconds = time.perf_counter() - total_start

    summary = build_run_summary(
        mode="workflow_strict",
        data_path=_normalize_data_path(data_path),
        expression_source=str(path),
        rows=int(df.height),
        codes=_count_codes(df, code_col=active_engine.code_col),
        expressions=len(batch_items),
        success_count=len(batch_items),
        failed_count=0,
        total_time_seconds=total_time_seconds,
        load_time_seconds=load_time_seconds,
        validate_time_seconds=None,
        execute_time_seconds=execute_time_seconds,
        write_time_seconds=None,
        output_path=None if output_path is None else str(output_path),
        notes=None,
    )
    return WorkflowRun(result_df=result_df, summary=summary)


def evaluate_expression_file_report_with_summary(
    path: str | Path,
    df: pl.DataFrame,
    *,
    engine: FactorEngine | None = None,
    data_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> WorkflowReportRun:
    total_start = time.perf_counter()
    active_engine = engine or FactorEngine()

    try:
        load_start = time.perf_counter()
        expressions = load_expression_file(path)
        load_time_seconds = time.perf_counter() - load_start
    except Exception as exc:
        report = BatchEvaluationReport(
            result_df=df,
            successes=[],
            failures=[
                _build_expression_failure(
                    name=None,
                    expression=None,
                    exc=exc,
                )
            ],
        )
        summary = build_run_summary(
            mode="workflow_report",
            data_path=_normalize_data_path(data_path),
            expression_source=str(path),
            rows=int(df.height),
            codes=_count_codes(df, code_col=active_engine.code_col),
            expressions=0,
            success_count=0,
            failed_count=len(report.failures),
            total_time_seconds=time.perf_counter() - total_start,
            load_time_seconds=None,
            validate_time_seconds=None,
            execute_time_seconds=None,
            write_time_seconds=None,
            output_path=None if output_path is None else str(output_path),
            notes="expression file load failed",
            exception_summary=str(exc),
        )
        return WorkflowReportRun(report=report, summary=summary)

    report, timing = _evaluate_expression_batch_report_internal(
        expressions,
        df,
        engine=active_engine,
    )
    total_time_seconds = time.perf_counter() - total_start
    summary = build_run_summary(
        mode="workflow_report",
        data_path=_normalize_data_path(data_path),
        expression_source=str(path),
        rows=int(df.height),
        codes=_count_codes(df, code_col=active_engine.code_col),
        expressions=len(expressions),
        success_count=len(report.successes),
        failed_count=len(report.failures),
        total_time_seconds=total_time_seconds,
        load_time_seconds=load_time_seconds,
        validate_time_seconds=timing.validate_time_seconds,
        execute_time_seconds=timing.execute_time_seconds,
        write_time_seconds=None,
        output_path=None if output_path is None else str(output_path),
        notes=None if not report.failures else "completed with partial failures",
        exception_summary=None if not report.failures else report.failures[0].message,
    )
    return WorkflowReportRun(report=report, summary=summary)


def write_result(df: pl.DataFrame, path: str | Path) -> None:
    target = Path(path)
    suffix = target.suffix.lower()

    try:
        if suffix == ".parquet":
            df.write_parquet(target)
            return
        if suffix == ".csv":
            df.write_csv(target)
            return
    except Exception as exc:  # pragma: no cover - exercised in tests
        raise WorkflowIOError(f"Failed to write result to '{target}': {exc}") from exc

    raise WorkflowConfigError(f"Unsupported output format for '{target}'")
