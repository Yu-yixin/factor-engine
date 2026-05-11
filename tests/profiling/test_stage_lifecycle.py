from __future__ import annotations

import json
import shutil
from pathlib import Path
from uuid import uuid4

import polars as pl
import pytest

from factor_engine.engine import FactorEngine
import factor_engine.executor as executor_module
from factor_engine.native_positional import NativePositionalResult
from factor_engine.native_positional import native_available
from factor_engine.stage_registry import StageRegistry
from benchmarks.scripts.benchmark_stage_lifecycle import WORKLOADS, build_workload, load_summary


def assert_frames_equal_with_nan(left: pl.DataFrame, right: pl.DataFrame) -> None:
    assert left.columns == right.columns
    for column in left.columns:
        left_values = left[column].to_list()
        right_values = right[column].to_list()
        assert len(left_values) == len(right_values)
        for observed, expected in zip(left_values, right_values, strict=True):
            if observed is None or expected is None:
                assert observed is None and expected is None
            elif isinstance(observed, float) and isinstance(expected, float):
                if observed != observed or expected != expected:
                    assert observed != observed and expected != expected
                else:
                    assert observed == expected
            else:
                assert observed == expected


def build_ordered_stage_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "time": [1, 1, 2, 2, 3, 3],
            "code": ["A", "B", "A", "B", "A", "B"],
            "close": [10.0, 20.0, 11.0, 19.0, 12.0, 18.0],
            "open": [9.0, 19.0, 10.0, 18.0, 11.0, 17.0],
        }
    )


def workspace_temp_dir() -> Path:
    root = Path(__file__).resolve().parents[1] / ".tmp_test_stage_lifecycle"
    root.mkdir(exist_ok=True)
    target = root / f"profile-{uuid4().hex}"
    target.mkdir()
    return target


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def build_profiled_engine_result(
    *,
    expressions: list[tuple[str, str]],
    lifecycle: bool,
    profile_dir: Path,
) -> pl.DataFrame:
    return FactorEngine().evaluate_many(
        expressions,
        build_ordered_stage_df(),
        profiling=True,
        profile_output_dir=profile_dir,
        lifecycle=lifecycle,
    )


def stage_lifecycle_expressions() -> list[tuple[str, str]]:
    return [
        ("argmaxed", "argmax(fill_null(close, open), 2)"),
        ("ranked", "rank(demean(ts_mean(close, 2)), pct=true)"),
        ("corr_ranked", "corr(rank(close), rank(open), 2)"),
    ]


def test_stage_registry_register_consume_and_drop_sweep():
    frame = pl.DataFrame({"base": [1], "__stage": [2], "out": [2]})
    registry = StageRegistry(batch_id="batch-1")
    registry.register_stage(
        expr_key=("expr", "x"),
        column_name="__stage",
        stage_kind="materialized_child",
        producer_route="compiled_child",
        frame_col_count=frame.width,
        cache_key=("expr", "x"),
    )
    registry.record_consume("__stage", consumer_kind="unit", frame_col_count=frame.width)

    stage = next(iter(registry.records.values()))
    assert stage.consumer_count_total == 1
    assert stage.last_use_order_index is not None

    stage_cache = {("expr", "x"): "__stage"}
    swept = registry.sweep_drop_candidates(
        frame,
        stage_cache=stage_cache,
        output_names={"out"},
        enabled=True,
    )

    assert "__stage" not in swept.columns
    assert stage.is_dropped is True
    assert stage_cache == {}


@pytest.mark.parametrize("stage_kind", ["staged_prefix", "materialized_child", "positional_child"])
@pytest.mark.parametrize("consumer_count", [0, 1, 2])
@pytest.mark.parametrize("is_output", [False, True])
def test_stage_registry_state_machine_matrix(
    stage_kind: str,
    consumer_count: int,
    is_output: bool,
):
    frame = pl.DataFrame({"base": [1], "__stage": [2], "out": [2]})
    registry = StageRegistry(batch_id="batch-matrix")
    registry.register_stage(
        expr_key=("expr", stage_kind, consumer_count, is_output),
        column_name="__stage",
        stage_kind=stage_kind,
        producer_route="unit",
        frame_col_count=frame.width,
        cache_key=("expr", stage_kind),
    )
    registry.set_expected_consumers("__stage", consumer_count)
    if is_output:
        registry.mark_output_backed("__stage")

    stage = next(iter(registry.records.values()))
    assert stage.consumer_count_total == consumer_count
    assert stage.consumer_count_remaining == consumer_count

    for index in range(consumer_count):
        registry.record_consume("__stage", consumer_kind=f"consumer_{index}", frame_col_count=frame.width)
        assert stage.consumer_count_remaining == consumer_count - index - 1
        assert stage.last_use_order_index is not None

    can_drop = registry.can_drop(stage, output_names={"out"})
    assert can_drop is (consumer_count == 0 and not is_output or consumer_count > 0 and not is_output)

    swept = registry.sweep_drop_candidates(
        frame,
        stage_cache={("expr", stage_kind): "__stage"},
        output_names={"out"},
        enabled=True,
    )
    if is_output:
        assert "__stage" in swept.columns
        assert stage.is_dropped is False
    else:
        assert "__stage" not in swept.columns
        assert stage.is_dropped is True


def test_stage_registry_does_not_drop_before_last_consumer():
    frame = pl.DataFrame({"base": [1], "__stage": [2], "out": [2]})
    registry = StageRegistry(batch_id="batch-consumers")
    registry.register_stage(
        expr_key=("expr", "multi"),
        column_name="__stage",
        stage_kind="materialized_child",
        producer_route="unit",
        frame_col_count=frame.width,
        cache_key=("expr", "multi"),
    )
    registry.set_expected_consumers("__stage", 2)
    stage = next(iter(registry.records.values()))

    registry.record_consume("__stage", consumer_kind="first", frame_col_count=frame.width)
    assert stage.consumer_count_remaining == 1
    assert registry.can_drop(stage, output_names={"out"}) is False

    frame_after_first = registry.sweep_drop_candidates(
        frame,
        stage_cache={("expr", "multi"): "__stage"},
        output_names={"out"},
        enabled=True,
    )
    assert "__stage" in frame_after_first.columns

    registry.record_consume("__stage", consumer_kind="second", frame_col_count=frame.width)
    assert stage.consumer_count_remaining == 0
    assert registry.can_drop(stage, output_names={"out"}) is True


def test_evaluate_many_profiling_writes_stage_lifecycle_files():
    temp_dir = workspace_temp_dir()
    try:
        df = build_ordered_stage_df()
        engine = FactorEngine()

        result = engine.evaluate_many(
            stage_lifecycle_expressions(),
            df,
            profiling=True,
            profile_output_dir=temp_dir,
            lifecycle=False,
        )

        assert result.columns == [
            "time",
            "code",
            "close",
            "open",
            "argmaxed",
            "ranked",
            "corr_ranked",
        ]
        for filename in [
            "latest_run.json",
            "history.csv",
            "latest_batch_details.jsonl",
            "latest_stage_details.jsonl",
            "latest_stage_events.jsonl",
            "latest_positional_phase_details.jsonl",
            "latest_output_details.jsonl",
            "latest_native_buffer_details.jsonl",
            "latest_memory_events.jsonl",
            "benchmark_report.md",
        ]:
            assert (temp_dir / filename).exists()

        run = json.loads((temp_dir / "latest_run.json").read_text(encoding="utf-8"))
        assert run["total_stage_count"] > 0
        assert run["alive_stage_at_batch_end_count"] > 0
        assert "peak_output_col_count" in run
        assert "peak_stage_col_count" in run
        assert "peak_native_buffer_bytes_estimate" in run
        assert "native_buffer_release_lag" in run

        events = (temp_dir / "latest_stage_events.jsonl").read_text(encoding="utf-8")
        assert "stage_created" in events
        assert "stage_consumed" in events
        assert "batch_end_stage_snapshot" in events

        positional_phases = read_jsonl(temp_dir / "latest_positional_phase_details.jsonl")
        assert positional_phases
        assert positional_phases[0]["python_kernel_used"] is True
        assert positional_phases[0]["native_kernel_used"] is False
        assert positional_phases[0]["positional_group_scan_time_ms"] >= 0
        assert positional_phases[0]["positional_to_list_time_ms"] >= 0

        outputs = read_jsonl(temp_dir / "latest_output_details.jsonl")
        memory_events = read_jsonl(temp_dir / "latest_memory_events.jsonl")
        assert {item["output_name"] for item in outputs} == {
            "argmaxed",
            "ranked",
            "corr_ranked",
        }
        assert all(item["attached_to_working_frame"] is False for item in outputs)
        assert any(event["event_type"] == "output_created" for event in memory_events)
        assert any(event["event_type"] == "output_attached" for event in memory_events)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_deferred_output_attach_keeps_outputs_out_of_ordered_working_frame():
    temp_dir = workspace_temp_dir()
    try:
        FactorEngine().evaluate_many(
            stage_lifecycle_expressions(),
            build_ordered_stage_df(),
            profiling=True,
            profile_output_dir=temp_dir,
            lifecycle=True,
        )

        run = json.loads((temp_dir / "latest_run.json").read_text(encoding="utf-8"))
        batches = read_jsonl(temp_dir / "latest_batch_details.jsonl")
        outputs = read_jsonl(temp_dir / "latest_output_details.jsonl")

        assert run["peak_output_col_count"] == 0
        assert batches[0]["peak_output_col_count"] == 0
        assert all(item["attached_to_working_frame"] is False for item in outputs)
        assert all(item["attached_order_index"] is not None for item in outputs)
        assert all(item["is_late_alive_output"] is False for item in outputs)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_m3_finalize_select_output_attach_preserves_results_and_narrows_frame():
    materialize_dir = workspace_temp_dir()
    finalize_dir = workspace_temp_dir()
    try:
        df = build_ordered_stage_df()
        expressions = [
            ("a", "ts_rank(close, 2) + ts_rank(close, 2)"),
            ("b", "ts_rank(open, 2) + ts_rank(open, 2)"),
            ("c", "ts_rank(close, 2) + ts_rank(open, 2)"),
        ]
        materialized = FactorEngine().evaluate_many(
            expressions,
            df,
            profiling=True,
            profile_output_dir=materialize_dir,
            output_attach_mode="materialize",
        )
        finalize_selected = FactorEngine().evaluate_many(
            expressions,
            df,
            profiling=True,
            profile_output_dir=finalize_dir,
            lifecycle_mode="first_wave",
            helper_lifecycle_mode="second_wave_nested",
            output_attach_mode="finalize_select",
        )

        assert_frames_equal_with_nan(finalize_selected, materialized)

        materialized_run = json.loads(
            (materialize_dir / "latest_run.json").read_text(encoding="utf-8")
        )
        finalize_run = json.loads(
            (finalize_dir / "latest_run.json").read_text(encoding="utf-8")
        )

        assert finalize_run["peak_frame_col_count"] <= materialized_run[
            "peak_frame_col_count"
        ]
        assert finalize_run["input_column_count"] == materialized_run["input_column_count"]
    finally:
        shutil.rmtree(materialize_dir, ignore_errors=True)
        shutil.rmtree(finalize_dir, ignore_errors=True)


def test_m3_last_use_select_output_attach_is_executable_and_safe():
    materialize_dir = workspace_temp_dir()
    last_use_dir = workspace_temp_dir()
    try:
        df = build_ordered_stage_df()
        expressions = [
            ("a", "ts_rank(close, 2) + ts_rank(close, 2)"),
            ("b", "ts_rank(open, 2) + ts_rank(open, 2)"),
        ]
        materialized = FactorEngine().evaluate_many(
            expressions,
            df,
            profiling=True,
            profile_output_dir=materialize_dir,
            output_attach_mode="materialize",
        )
        last_use_selected = FactorEngine().evaluate_many(
            expressions,
            df,
            profiling=True,
            profile_output_dir=last_use_dir,
            lifecycle_mode="first_wave",
            helper_lifecycle_mode="second_wave_nested",
            output_attach_mode="last_use_select",
        )

        assert_frames_equal_with_nan(last_use_selected, materialized)

        materialized_run = json.loads(
            (materialize_dir / "latest_run.json").read_text(encoding="utf-8")
        )
        last_use_run = json.loads(
            (last_use_dir / "latest_run.json").read_text(encoding="utf-8")
        )

        assert last_use_run["peak_frame_col_count"] <= materialized_run[
            "peak_frame_col_count"
        ]
        outputs = [
            json.loads(line)
            for line in (last_use_dir / "latest_output_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]
        assert all(item["attached_to_working_frame"] is False for item in outputs)
    finally:
        shutil.rmtree(materialize_dir, ignore_errors=True)
        shutil.rmtree(last_use_dir, ignore_errors=True)


def test_m3_dependency_driven_projection_preserves_results():
    baseline_dir = workspace_temp_dir()
    projected_dir = workspace_temp_dir()
    try:
        df = build_ordered_stage_df()
        expressions = [
            ("a", "ts_rank(close, 2) + ts_rank(close, 2)"),
            ("b", "ts_rank(open, 2) + ts_rank(open, 2)"),
        ]
        baseline = FactorEngine().evaluate_many(
            expressions,
            df,
            profiling=True,
            profile_output_dir=baseline_dir,
            frame_projection_mode="off",
        )
        projected = FactorEngine().evaluate_many(
            expressions,
            df,
            profiling=True,
            profile_output_dir=projected_dir,
            frame_projection_mode="dependency_driven",
        )

        assert_frames_equal_with_nan(projected, baseline)
    finally:
        shutil.rmtree(baseline_dir, ignore_errors=True)
        shutil.rmtree(projected_dir, ignore_errors=True)


def test_native_buffer_profile_events_record_immediate_release(monkeypatch):
    temp_dir = workspace_temp_dir()

    def fake_native_kernel(
        value_series: pl.Series,
        group_codes: pl.Series,
        window: int,
        *,
        mode: str,
    ) -> NativePositionalResult:
        return NativePositionalResult(
            series=pl.Series(value_series.name, [None] * value_series.len(), dtype=pl.Int64),
            to_list_time_ms=0.1,
            group_scan_time_ms=0.2,
            series_construct_time_ms=0.3,
            native_kernel_used=True,
            low_copy_bridge_used=True,
            python_object_bridge_used=False,
            native_parallel_used=True,
            group_parallelism_level=4,
            output_buffer_bytes_estimate=value_series.len() * 8 + 1,
        )

    monkeypatch.setattr(executor_module, "evaluate_native_positional_kernel", fake_native_kernel)
    try:
        FactorEngine().evaluate_many(
            [("argmaxed", "argmax(close, 2)")],
            build_ordered_stage_df(),
            profiling=True,
            profile_output_dir=temp_dir,
            lifecycle=True,
        )

        run = json.loads((temp_dir / "latest_run.json").read_text(encoding="utf-8"))
        buffers = read_jsonl(temp_dir / "latest_native_buffer_details.jsonl")
        memory_events = read_jsonl(temp_dir / "latest_memory_events.jsonl")

        assert run["native_output_buffer_count"] == 1
        assert run["peak_native_buffer_bytes_estimate"] > 0
        assert run["native_buffer_release_lag"] == 0
        assert run["parallel_enabled"] is True
        assert buffers[0]["alive_before_attach"] is True
        assert buffers[0]["alive_after_attach"] is False
        assert buffers[0]["release_lag_steps"] == 0
        assert {event["event_type"] for event in memory_events} >= {
            "native_buffer_created",
            "native_buffer_attached",
            "native_buffer_released",
        }
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_profiling_and_lifecycle_do_not_change_results_or_routes():
    base_dir = workspace_temp_dir()
    lifecycle_dir = workspace_temp_dir()
    try:
        df = build_ordered_stage_df()
        expressions = stage_lifecycle_expressions()
        engine = FactorEngine()
        route_map = {
            output_name: engine.inspect_plan(expression, df)["route"]
            for output_name, expression in expressions
        }

        baseline = FactorEngine().evaluate_many(expressions, df)
        profiled = FactorEngine().evaluate_many(
            expressions,
            df,
            profiling=True,
            profile_output_dir=base_dir,
            lifecycle=False,
        )
        lifecycle = FactorEngine().evaluate_many(
            expressions,
            df,
            profiling=True,
            profile_output_dir=lifecycle_dir,
            lifecycle=True,
        )

        assert_frames_equal_with_nan(profiled, baseline)
        assert_frames_equal_with_nan(lifecycle, baseline)
        assert route_map == {
            output_name: engine.inspect_plan(expression, df)["route"]
            for output_name, expression in expressions
        }
    finally:
        shutil.rmtree(base_dir, ignore_errors=True)
        shutil.rmtree(lifecycle_dir, ignore_errors=True)


def test_stage_event_stream_matches_summary_and_stage_details():
    profile_dir = workspace_temp_dir()
    try:
        build_profiled_engine_result(
            expressions=stage_lifecycle_expressions(),
            lifecycle=True,
            profile_dir=profile_dir,
        )

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        batches = read_jsonl(profile_dir / "latest_batch_details.jsonl")
        stages = read_jsonl(profile_dir / "latest_stage_details.jsonl")
        events = read_jsonl(profile_dir / "latest_stage_events.jsonl")

        created = [event for event in events if event["event_type"] == "stage_created"]
        consumed = [event for event in events if event["event_type"] == "stage_consumed"]
        dropped = [event for event in events if event["event_type"] == "stage_dropped"]
        snapshots = [event for event in events if event["event_type"] == "batch_end_stage_snapshot"]

        assert created
        assert consumed
        assert dropped
        assert snapshots
        assert len(created) == len(stages) == run["total_stage_count"]
        assert len(dropped) == run["dropped_stage_count"]
        assert sum(1 for stage in stages if stage["dropped"]) == run["dropped_stage_count"]
        assert sum(1 for stage in stages if stage["alive_at_batch_end"]) == run[
            "alive_stage_at_batch_end_count"
        ]
        assert sum(batch["alive_stage_at_batch_end_count"] for batch in batches) == run[
            "alive_stage_at_batch_end_count"
        ]

        events_by_stage: dict[str, list[dict[str, object]]] = {}
        for event in events:
            events_by_stage.setdefault(str(event["stage_id"]), []).append(event)

        for stage in stages:
            stage_id = str(stage["stage_id"])
            stage_events = events_by_stage[stage_id]
            created_order = min(
                int(event["order_index"])
                for event in stage_events
                if event["event_type"] == "stage_created"
            )
            snapshot_order = max(
                int(event["order_index"])
                for event in stage_events
                if event["event_type"] == "batch_end_stage_snapshot"
            )
            assert created_order < snapshot_order
            consume_orders = [
                int(event["order_index"])
                for event in stage_events
                if event["event_type"] == "stage_consumed"
            ]
            assert all(created_order < order < snapshot_order for order in consume_orders)
            drop_orders = [
                int(event["order_index"])
                for event in stage_events
                if event["event_type"] == "stage_dropped"
            ]
            assert all(created_order < order < snapshot_order for order in drop_orders)
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_lifecycle_sweep_preserves_results_and_reduces_alive_stage_count():
    base_dir = workspace_temp_dir()
    lifecycle_dir = workspace_temp_dir()
    try:
        df = build_ordered_stage_df()
        expressions = stage_lifecycle_expressions()

        base_engine = FactorEngine()
        lifecycle_engine = FactorEngine()
        base = base_engine.evaluate_many(
            expressions,
            df,
            profiling=True,
            profile_output_dir=base_dir,
            lifecycle=False,
        )
        swept = lifecycle_engine.evaluate_many(
            expressions,
            df,
            profiling=True,
            profile_output_dir=lifecycle_dir,
            lifecycle=True,
        )

        assert_frames_equal_with_nan(swept, base)

        base_run = json.loads((base_dir / "latest_run.json").read_text(encoding="utf-8"))
        swept_run = json.loads((lifecycle_dir / "latest_run.json").read_text(encoding="utf-8"))

        assert swept_run["dropped_stage_count"] > 0
        assert swept_run["alive_stage_at_batch_end_count"] < base_run["alive_stage_at_batch_end_count"]
        assert swept_run["peak_frame_col_count"] >= swept_run["input_column_count"]
    finally:
        shutil.rmtree(base_dir, ignore_errors=True)
        shutil.rmtree(lifecycle_dir, ignore_errors=True)


def test_planned_lifecycle_preserves_reusable_child_stage_without_recompute():
    base_dir = workspace_temp_dir()
    lifecycle_dir = workspace_temp_dir()
    try:
        df = build_ordered_stage_df()
        expressions = [
            ("a", "argmax(ts_mean(close, 2), 2)"),
            ("b", "argmin(ts_mean(close, 2), 2)"),
            ("c", "argmax(ts_mean(close, 2), 3)"),
        ]
        baseline = FactorEngine().evaluate_many(
            expressions,
            df,
            profiling=True,
            profile_output_dir=base_dir,
            lifecycle=False,
        )
        lifecycle = FactorEngine().evaluate_many(
            expressions,
            df,
            profiling=True,
            profile_output_dir=lifecycle_dir,
            lifecycle=True,
        )
        assert_frames_equal_with_nan(lifecycle, baseline)

        baseline_summary = load_summary(base_dir)
        lifecycle_summary = load_summary(lifecycle_dir)
        assert lifecycle_summary["total_stage_count"] == baseline_summary["total_stage_count"]
        assert lifecycle_summary["dropped_stage_count"] > 0
        assert lifecycle_summary["alive_stage_at_batch_end_count"] == 0

        stages = read_jsonl(lifecycle_dir / "latest_stage_details.jsonl")
        events = read_jsonl(lifecycle_dir / "latest_stage_events.jsonl")
        reusable = [
            stage
            for stage in stages
            if stage["planned_consumer_count_total"] and stage["planned_consumer_count_total"] > 1
        ]
        assert reusable
        assert all(stage["actual_consume_count"] == stage["planned_consumer_count_total"] for stage in reusable)
        assert all(stage["dropped_after_planned_last_use"] for stage in stages if stage["dropped"])
        assert any(event["event_type"] == "planned_stage_registered" for event in events)
        assert any(event["event_type"] == "planned_stage_reused" for event in events)
        assert any(event["event_type"] == "planned_last_use_reached" for event in events)

        batch = read_jsonl(lifecycle_dir / "latest_batch_details.jsonl")[0]
        assert batch["planned_reusable_stage_count"] >= 1
        assert batch["avoided_recomputation_count"] >= 1
        assert batch["recomputed_stage_count"] == 0
    finally:
        shutil.rmtree(base_dir, ignore_errors=True)
        shutil.rmtree(lifecycle_dir, ignore_errors=True)


@pytest.mark.skipif(not native_available(), reason="native positional extension is not installed")
def test_native_positional_kernel_matches_python_fallback(monkeypatch):
    python_dir = workspace_temp_dir()
    native_dir = workspace_temp_dir()
    try:
        df = pl.DataFrame(
            {
                "time": [1, 2, 3, 4, 1, 2, 3, 4],
                "code": ["A", "A", "A", "A", "B", "B", "B", "B"],
                "close": [5.0, 7.0, 7.0, None, None, 3.0, 3.0, 1.0],
                "open": [4.0, 6.0, 6.0, 6.0, 2.0, 2.0, 2.0, 2.0],
            }
        )
        expressions = [
            ("argmaxed", "argmax(close, 3)"),
            ("argmined", "argmin(close, 3)"),
            ("nested", "argmax(ts_mean(fill_null(close, open), 2), 3)"),
        ]

        monkeypatch.delenv("FACTOR_ENGINE_POSITIONAL_KERNEL", raising=False)
        python_result = FactorEngine().evaluate_many(
            expressions,
            df,
            profiling=True,
            profile_output_dir=python_dir,
            lifecycle=True,
        )

        monkeypatch.setenv("FACTOR_ENGINE_POSITIONAL_KERNEL", "native")
        native_result = FactorEngine().evaluate_many(
            expressions,
            df,
            profiling=True,
            profile_output_dir=native_dir,
            lifecycle=True,
        )

        assert_frames_equal_with_nan(native_result, python_result)
        native_phases = read_jsonl(native_dir / "latest_positional_phase_details.jsonl")
        assert native_phases
        assert all(item["native_kernel_used"] is True for item in native_phases)
        assert all(item["python_kernel_used"] is False for item in native_phases)
        assert all(item["native_low_copy_bridge_used"] is True for item in native_phases)
        assert all(item["python_object_bridge_used"] is False for item in native_phases)
    finally:
        shutil.rmtree(python_dir, ignore_errors=True)
        shutil.rmtree(native_dir, ignore_errors=True)


@pytest.mark.parametrize("workload", WORKLOADS, ids=lambda item: item.name)
def test_synthetic_benchmark_lifecycle_metrics_do_not_regress(workload):
    base_dir = workspace_temp_dir()
    lifecycle_dir = workspace_temp_dir()
    try:
        df = build_workload(code_count=8, time_count=32)
        baseline = FactorEngine().evaluate_many(
            workload.expressions,
            df,
            profiling=True,
            profile_output_dir=base_dir,
            benchmark_name=f"pytest_{workload.name}_v1",
            dataset_name="pytest_synthetic_stage_lifecycle",
            lifecycle=False,
        )
        lifecycle = FactorEngine().evaluate_many(
            workload.expressions,
            df,
            profiling=True,
            profile_output_dir=lifecycle_dir,
            benchmark_name=f"pytest_{workload.name}_v2",
            dataset_name="pytest_synthetic_stage_lifecycle",
            lifecycle=True,
        )
        assert_frames_equal_with_nan(lifecycle, baseline)

        baseline_summary = load_summary(base_dir)
        lifecycle_summary = load_summary(lifecycle_dir)

        assert lifecycle_summary["dropped_stage_count"] > 0
        assert (
            lifecycle_summary["alive_stage_at_batch_end_count"] == 0
            or lifecycle_summary["alive_stage_at_batch_end_count"]
            < baseline_summary["alive_stage_at_batch_end_count"]
        )
        assert lifecycle_summary["peak_frame_col_count"] <= baseline_summary["peak_frame_col_count"]
        assert (
            lifecycle_summary["peak_live_stage_count_estimate"]
            <= baseline_summary["peak_live_stage_count_estimate"]
        )
    finally:
        shutil.rmtree(base_dir, ignore_errors=True)
        shutil.rmtree(lifecycle_dir, ignore_errors=True)
