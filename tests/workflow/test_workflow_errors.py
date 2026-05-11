from __future__ import annotations

import shutil
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import polars as pl
import pytest

from factor_engine.errors import (
    ExecutionError,
    ExpressionFailure,
    UnknownVariableError,
    ParserError,
    WorkflowConfigError,
    WorkflowError,
    WorkflowIOError,
)
from factor_engine.workflow import (
    BatchExpression,
    evaluate_expression_batch_report,
    evaluate_expression_file_report,
    load_expression_file,
)


def build_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [10.0, 15.0, 12.0],
            "open": [9.0, 11.0, 11.0],
            "industry": ["tech", "tech", None],
        }
    )


@contextmanager
def workspace_temp_dir():
    root = Path(__file__).resolve().parents[1] / ".tmp_test_workflow"
    root.mkdir(exist_ok=True)
    temp_dir = root / f"workflow-{uuid4().hex}"
    temp_dir.mkdir()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_workflow_error_inheritance():
    assert issubclass(WorkflowConfigError, WorkflowError)
    assert issubclass(WorkflowIOError, WorkflowError)


def test_expression_failure_payload_is_structured():
    failure = ExpressionFailure(
        name="spread",
        expression="close - open",
        stage="validation",
        error_type="ValidationError",
        message="bad expression",
    )

    assert failure.name == "spread"
    assert failure.expression == "close - open"
    assert failure.stage == "validation"


def test_syntax_error_classified_correctly():
    report = evaluate_expression_batch_report(
        [BatchExpression(name="bad_syntax", expression="close +")],
        build_df(),
    )

    assert report.has_failures is True
    assert report.successes == []
    assert len(report.failures) == 1
    failure = report.failures[0]
    assert failure.name == "bad_syntax"
    assert failure.expression == "close +"
    assert failure.stage == "parser"
    assert failure.error_type == ParserError.__name__


def test_validation_error_classified_correctly():
    report = evaluate_expression_batch_report(
        [BatchExpression(name="bad_validation", expression="unknown + 1")],
        build_df(),
    )

    assert len(report.failures) == 1
    failure = report.failures[0]
    assert failure.name == "bad_validation"
    assert failure.stage == "validation"
    assert failure.error_type == UnknownVariableError.__name__
    assert "unknown variable" in failure.message.lower()


def test_execution_error_classified_correctly():
    report = evaluate_expression_batch_report(
        [BatchExpression(name="bad_execution", expression="seglen_mean(close, [2])")],
        build_df(),
    )

    assert len(report.failures) == 1
    failure = report.failures[0]
    assert failure.name == "bad_execution"
    assert failure.stage == "execution"
    assert failure.error_type == ExecutionError.__name__
    assert "cover full group" in failure.message


def test_batch_report_keeps_successes_and_failures_together():
    report = evaluate_expression_batch_report(
        [
            BatchExpression(name="spread", expression="close - open"),
            BatchExpression(name="bad", expression="unknown + 1"),
            BatchExpression(name="lagged", expression="delay(close, 1)"),
        ],
        build_df(),
    )

    assert [item.name for item in report.successes] == ["spread", "lagged"]
    assert [failure.name for failure in report.failures] == ["bad"]
    assert report.result_df["spread"].to_list() == [1.0, 4.0, 1.0]
    assert report.result_df["lagged"].to_list() == [None, 10.0, 15.0]
    assert "bad" not in report.result_df.columns


def test_batch_report_keeps_successes_when_execution_fails_for_one_expression():
    report = evaluate_expression_batch_report(
        [
            BatchExpression(name="spread", expression="close - open"),
            BatchExpression(name="bad_execution", expression="seglen_mean(close, [2])"),
            BatchExpression(name="lagged", expression="delay(close, 1)"),
        ],
        build_df(),
    )

    assert [item.name for item in report.successes] == ["spread", "lagged"]
    assert [failure.name for failure in report.failures] == ["bad_execution"]
    assert report.failures[0].stage == "execution"
    assert report.result_df["spread"].to_list() == [1.0, 4.0, 1.0]
    assert report.result_df["lagged"].to_list() == [None, 10.0, 15.0]
    assert "bad_execution" not in report.result_df.columns


def test_file_report_returns_config_failure_for_malformed_file():
    with workspace_temp_dir() as temp_dir:
        path = temp_dir / "bad.yaml"
        path.write_text("expressions:\n  spread: close - open\n", encoding="utf-8")

        report = evaluate_expression_file_report(path, build_df())

    assert report.successes == []
    assert len(report.failures) == 1
    failure = report.failures[0]
    assert failure.name is None
    assert failure.expression is None
    assert failure.stage == "config"
    assert failure.error_type == WorkflowConfigError.__name__


def test_load_expression_file_missing_path_raises_workflow_io_error():
    with pytest.raises(WorkflowIOError, match="Failed to read expression file"):
        load_expression_file("does-not-exist.yaml")
