from __future__ import annotations

import csv
import json
import shutil
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from factor_engine.run_summary import (
    CSV_COLUMNS,
    build_run_summary,
    persist_run_summary,
    render_run_summary,
)


def build_sample_summary():
    return build_run_summary(
        mode="workflow_report",
        data_path="data/example.parquet",
        expression_source="expressions.yaml",
        rows=120000,
        codes=500,
        expressions=42,
        success_count=40,
        failed_count=2,
        total_time_seconds=3.214,
        load_time_seconds=0.412,
        validate_time_seconds=None,
        execute_time_seconds=2.101,
        write_time_seconds=None,
        output_path="result.parquet",
        notes=None,
    )


@contextmanager
def workspace_temp_dir():
    root = Path(__file__).resolve().parents[1] / ".tmp_test_run_summary"
    root.mkdir(exist_ok=True)
    temp_dir = root / f"run-summary-{uuid4().hex}"
    temp_dir.mkdir()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_persist_run_summary_writes_latest_json_and_history_csv():
    with workspace_temp_dir() as temp_dir:
        summary = build_sample_summary()

        artifacts = persist_run_summary(summary, benchmarks_dir=temp_dir)

        latest_payload = json.loads(artifacts.latest_json_path.read_text(encoding="utf-8"))
        assert latest_payload["mode"] == "workflow_report"
        assert latest_payload["validate_time_seconds"] is None
        assert artifacts.history_csv_path.exists()

        rows = list(csv.DictReader(artifacts.history_csv_path.open(encoding="utf-8")))
        assert len(rows) == 1
        assert rows[0]["mode"] == "workflow_report"
        assert rows[0]["validate_time_seconds"] == ""


def test_history_csv_header_is_created_once():
    with workspace_temp_dir() as temp_dir:
        first = build_sample_summary()
        second = build_run_summary(
            mode="benchmark_real_workload",
            data_path="generated://benchmark_real_workload",
            expression_source="inline:benchmark_real_workload",
            rows=1000,
            codes=10,
            expressions=5,
            success_count=5,
            failed_count=0,
            total_time_seconds=1.5,
            load_time_seconds=None,
            validate_time_seconds=None,
            execute_time_seconds=1.2,
            write_time_seconds=0.1,
            output_path=None,
            notes="ok",
        )

        persist_run_summary(first, benchmarks_dir=temp_dir)
        persist_run_summary(second, benchmarks_dir=temp_dir)

        lines = (temp_dir / "history.csv").read_text(encoding="utf-8").splitlines()
        assert lines[0].split(",") == CSV_COLUMNS
        assert len(lines) == 3


def test_render_run_summary_is_human_readable():
    rendered = render_run_summary(build_sample_summary())

    assert rendered.startswith("[run-summary]")
    assert "mode=workflow_report" in rendered
    assert "rows=120000" in rendered
