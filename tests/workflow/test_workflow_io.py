from __future__ import annotations

import json
import shutil
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import polars as pl
import pytest

from factor_engine.engine import FactorEngine
from factor_engine.errors import WorkflowConfigError, WorkflowIOError
from factor_engine.workflow import (
    evaluate_expression_file,
    evaluate_expression_file_report_with_summary,
    evaluate_expression_file_with_summary,
    load_expression_file,
    write_result,
)


def build_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [10.0, 15.0, 12.0],
            "open": [9.0, 11.0, 11.0],
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


def test_load_valid_yaml_expression_file():
    with workspace_temp_dir() as temp_dir:
        path = temp_dir / "batch.yaml"
        path.write_text(
            "\n".join(
                [
                    "expressions:",
                    "  - name: spread",
                    "    expression: close - open",
                    "  - name: ts_rank_20",
                    "    expression: ts_rank(close, 2, pct=true)",
                ]
            ),
            encoding="utf-8",
        )

        result = load_expression_file(path)

    assert [(item.name, item.expression) for item in result] == [
        ("spread", "close - open"),
        ("ts_rank_20", "ts_rank(close, 2, pct=true)"),
    ]


def test_load_valid_json_expression_file():
    with workspace_temp_dir() as temp_dir:
        path = temp_dir / "batch.json"
        path.write_text(
            json.dumps(
                {
                    "expressions": [
                        {"name": "spread", "expression": "close - open"},
                        {"name": "lagged", "expression": "delay(close, 1)"},
                    ]
                }
            ),
            encoding="utf-8",
        )

        result = load_expression_file(path)

    assert [(item.name, item.expression) for item in result] == [
        ("spread", "close - open"),
        ("lagged", "delay(close, 1)"),
    ]


def test_duplicate_output_names_rejected():
    with workspace_temp_dir() as temp_dir:
        path = temp_dir / "dup.json"
        path.write_text(
            json.dumps(
                {
                    "expressions": [
                        {"name": "spread", "expression": "close - open"},
                        {"name": "spread", "expression": "delay(close, 1)"},
                    ]
                }
            ),
            encoding="utf-8",
        )

        with pytest.raises(WorkflowConfigError, match="Duplicate expression name"):
            load_expression_file(path)


def test_malformed_file_schema_rejected():
    with workspace_temp_dir() as temp_dir:
        path = temp_dir / "bad.yaml"
        path.write_text("expressions:\n  spread: close - open\n", encoding="utf-8")

        with pytest.raises(
            WorkflowConfigError, match="must start with 'expressions:' and list items|Invalid YAML entry"
        ):
            load_expression_file(path)


def test_loaded_expressions_pass_through_evaluate_many():
    with workspace_temp_dir() as temp_dir:
        path = temp_dir / "batch.json"
        path.write_text(
            json.dumps(
                {
                    "expressions": [
                        {"name": "spread", "expression": "close - open"},
                        {"name": "lagged", "expression": "delay(close, 1)"},
                    ]
                }
            ),
            encoding="utf-8",
        )

        result = evaluate_expression_file(path, build_df(), engine=FactorEngine())

    assert result["spread"].to_list() == [1.0, 4.0, 1.0]
    assert result["lagged"].to_list() == [None, 10.0, 15.0]


def test_workflow_run_with_summary_returns_counts_and_timings():
    with workspace_temp_dir() as temp_dir:
        path = temp_dir / "batch.json"
        path.write_text(
            json.dumps(
                {
                    "expressions": [
                        {"name": "spread", "expression": "close - open"},
                        {"name": "lagged", "expression": "delay(close, 1)"},
                    ]
                }
            ),
            encoding="utf-8",
        )

        run = evaluate_expression_file_with_summary(
            path,
            build_df(),
            engine=FactorEngine(),
            data_path="data/example.parquet",
            output_path="result.parquet",
        )

    assert run.result_df["spread"].to_list() == [1.0, 4.0, 1.0]
    assert run.summary.mode == "workflow_strict"
    assert run.summary.expression_source.endswith("batch.json")
    assert run.summary.rows == 3
    assert run.summary.codes == 1
    assert run.summary.expressions == 2
    assert run.summary.success_count == 2
    assert run.summary.failed_count == 0
    assert run.summary.load_time_seconds is not None
    assert run.summary.validate_time_seconds is None
    assert run.summary.execute_time_seconds is not None
    assert run.summary.write_time_seconds is None


def test_failed_workflow_report_with_summary_records_failed_count():
    with workspace_temp_dir() as temp_dir:
        path = temp_dir / "batch.json"
        path.write_text(
            json.dumps(
                {
                    "expressions": [
                        {"name": "spread", "expression": "close - open"},
                        {"name": "bad", "expression": "unknown + 1"},
                    ]
                }
            ),
            encoding="utf-8",
        )

        run = evaluate_expression_file_report_with_summary(
            path,
            build_df(),
            engine=FactorEngine(),
            data_path="data/example.parquet",
            output_path="result.parquet",
        )

    assert [item.name for item in run.report.successes] == ["spread"]
    assert [failure.name for failure in run.report.failures] == ["bad"]
    assert run.summary.mode == "workflow_report"
    assert run.summary.expressions == 2
    assert run.summary.success_count == 1
    assert run.summary.failed_count == 1
    assert run.summary.validate_time_seconds is not None
    assert run.summary.execute_time_seconds is not None


def test_write_parquet_succeeds():
    with workspace_temp_dir() as temp_dir:
        target = temp_dir / "result.parquet"
        df = build_df()

        write_result(df, target)
        loaded = pl.read_parquet(target)

    assert loaded.columns == df.columns
    assert loaded.shape == df.shape


def test_write_csv_succeeds():
    with workspace_temp_dir() as temp_dir:
        target = temp_dir / "result.csv"
        df = build_df()

        write_result(df, target)
        loaded = pl.read_csv(target)

    assert loaded.columns == df.columns
    assert loaded.shape == df.shape


def test_temp_path_error_produces_clear_message():
    with workspace_temp_dir() as temp_dir:
        target = temp_dir / "missing" / "result.csv"

        with pytest.raises(WorkflowIOError, match="Failed to write result"):
            write_result(build_df(), target)
