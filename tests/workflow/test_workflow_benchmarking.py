from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import polars as pl

from factor_engine.engine import FactorEngine
from factor_engine.run_summary import persist_run_summary
from factor_engine.workflow import BatchExpression, evaluate_expression_batch_report


class CountingEngine(FactorEngine):
    def __init__(self) -> None:
        super().__init__()
        self.evaluate_calls: list[str] = []
        self.evaluate_many_calls: int = 0

    def evaluate(self, expression: str, df: pl.DataFrame, output_name: str = "result") -> pl.DataFrame:
        self.evaluate_calls.append(expression)
        return super().evaluate(expression, df, output_name=output_name)

    def evaluate_many(
        self,
        expressions: list[tuple[str, str]],
        df: pl.DataFrame,
    ) -> pl.DataFrame:
        self.evaluate_many_calls += 1
        return super().evaluate_many(expressions, df)


def build_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "time": [1, 2, 3],
            "code": ["A", "A", "A"],
            "close": [10.0, 15.0, 12.0],
            "open": [9.0, 11.0, 11.0],
            "industry": ["tech", "tech", "tech"],
        }
    )


@contextmanager
def workspace_temp_dir():
    root = Path(__file__).resolve().parents[1] / ".tmp_test_workflow_benchmarking"
    root.mkdir(exist_ok=True)
    temp_dir = root / f"workflow-benchmarking-{uuid4().hex}"
    temp_dir.mkdir()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_batch_report_uses_evaluate_many_fast_path_for_all_valid_expressions():
    engine = CountingEngine()

    report = evaluate_expression_batch_report(
        [
            BatchExpression(name="spread", expression="close - open"),
            BatchExpression(name="lagged", expression="delay(close, 1)"),
        ],
        build_df(),
        engine=engine,
    )

    assert [item.name for item in report.successes] == ["spread", "lagged"]
    assert report.failures == []
    assert engine.evaluate_many_calls == 1
    assert engine.evaluate_calls == []


def test_benchmark_summary_can_write_latest_json():
    with workspace_temp_dir() as temp_dir:
        repo_root = Path(__file__).resolve().parents[2]
        module_path = repo_root / "benchmarks" / "scripts" / "benchmark_real_workload.py"
        spec = importlib.util.spec_from_file_location("benchmark_real_workload", module_path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        summary = module.build_benchmark_run_summary(
            df=build_df(),
            expressions=module.EXPRESSIONS[:2],
            total_time_seconds=1.5,
            load_time_seconds=0.2,
            execute_time_seconds=1.1,
            write_time_seconds=0.1,
            notes="test run",
        )
        artifacts = persist_run_summary(summary, benchmarks_dir=temp_dir)

        payload = json.loads(artifacts.latest_json_path.read_text(encoding="utf-8"))
        assert payload["mode"] == "benchmark_real_workload"
        assert payload["benchmark_name"] == "benchmark_real_workload"
        assert payload["rows"] == 3
        assert payload["expressions"] == 2
