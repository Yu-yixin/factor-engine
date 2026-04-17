from __future__ import annotations

import json
import shutil
from pathlib import Path
from uuid import uuid4

import polars as pl
from polars.testing import assert_frame_equal

from factor_engine.engine import FactorEngine
from factor_engine.lifecycle import (
    FirstWaveCandidateInput,
    HelperFirstWaveCandidateInput,
    HelperSecondWaveNestedCandidateInput,
    is_first_wave_helper_candidate,
    is_first_wave_candidate,
    is_second_wave_nested_candidate,
    normalize_frame_projection_mode,
    normalize_fusion_mode,
    normalize_helper_lifecycle_mode,
    normalize_lifecycle_mode,
    normalize_output_attach_mode,
    normalize_planner_cse_mode,
)
from factor_engine.executor import Executor
from factor_engine.planner import ExecutionPlanner


def build_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "time": [1, 1, 2, 2, 3, 3, 4, 4],
            "code": ["A", "B", "A", "B", "A", "B", "A", "B"],
            "close": [10.0, 20.0, 11.0, 19.0, 12.0, 18.0, 13.0, 17.0],
            "open": [9.0, 19.0, 10.0, 18.0, 11.0, 17.0, 12.0, 16.0],
            "volume": [100.0, 200.0, 120.0, 220.0, 130.0, 230.0, 140.0, 240.0],
        }
    )


def temp_dir() -> Path:
    root = Path(__file__).resolve().parents[1] / ".tmp_test_dag_cse"
    root.mkdir(exist_ok=True)
    target = root / f"profile-{uuid4().hex}"
    target.mkdir()
    return target


def test_dag_identity_deduplicates_repeated_heavy_subexpression():
    inspection = FactorEngine().inspect_dag(
        [
            ("a", "argmax(ts_mean(close, 2), 2)"),
            ("b", "argmin(ts_mean(close, 2), 2)"),
        ],
        build_df(),
    )

    deduped = inspection["deduplicated_nodes"]
    labels = {item["label"] for item in deduped}

    assert inspection["ast_node_count"] > inspection["dag_node_count"]
    assert "ts_mean" in labels
    ts_mean = next(item for item in deduped if item["label"] == "ts_mean")
    assert ts_mean["share_decision"] == "materialize"
    assert ts_mean["share_reason"] == "repeated_expensive_node"
    assert ts_mean["materialization_kind"] == "shared_intermediate"
    assert ts_mean["materialization_reason"] == "shared_reuse_and_path_normalization"
    assert ts_mean["materialization_eligibility"] == "materialize_for_both"
    assert ts_mean["lifecycle"]["producer_step"] is not None
    assert ts_mean["lifecycle"]["ref_count_initial"] == 2
    assert ts_mean["lifecycle"]["drop_candidate"] is True
    assert ts_mean["lifecycle"]["drop_blocker_reason"] == ""


def test_dag_canonicalizes_default_kwargs_without_merging_different_options():
    default_rank = FactorEngine().inspect_dag(
        [
            ("a", "rank(close)"),
            ("b", "rank(close, ascending=false, pct=false)"),
        ],
        build_df(),
    )
    different_rank = FactorEngine().inspect_dag(
        [
            ("a", "rank(close)"),
            ("b", "rank(close, pct=true)"),
        ],
        build_df(),
    )

    assert any(item["label"] == "rank" for item in default_rank["deduplicated_nodes"])
    assert not any(item["label"] == "rank" for item in different_rank["deduplicated_nodes"])


def test_dag_canonicalizes_alpha101_aliases_to_existing_ordered_nodes():
    inspection = FactorEngine().inspect_dag(
        [
            ("a", "sum(close, 2)"),
            ("b", "ts_sum(close, 2)"),
        ],
        build_df(),
    )

    ts_sum = next(item for item in inspection["deduplicated_nodes"] if item["label"] == "ts_sum")
    assert ts_sum["occurrence_count"] == 2
    assert ts_sum["outputs"] == ("a", "b")
    assert ts_sum["share_decision"] in {"inline", "materialize"}


def test_dag_keeps_repeated_cheap_nodes_inline():
    inspection = FactorEngine().inspect_dag(
        [
            ("a", "close + open"),
            ("b", "close + open"),
        ],
        build_df(),
    )

    binary_node = next(item for item in inspection["deduplicated_nodes"] if item["label"] == "+")
    assert binary_node["cost_class"] == "cheap"
    assert binary_node["share_decision"] == "inline"
    assert binary_node["materialization_kind"] == "final"


def test_repeated_heavy_positional_subexpression_executes_once(monkeypatch):
    calls = {"count": 0}
    original = Executor._evaluate_positional_kernel

    def counted(self, value_series, group_codes, window, *, mode):
        calls["count"] += 1
        return original(self, value_series, group_codes, window, mode=mode)

    monkeypatch.setattr(Executor, "_evaluate_positional_kernel", counted)

    result = FactorEngine().evaluate_many(
        [
            ("a", "argmax(ts_mean(close, 2), 2)"),
            ("b", "argmax(ts_mean(close, 2), 2)"),
        ],
        build_df(),
    )

    assert result.columns[-2:] == ["a", "b"]
    assert calls["count"] == 1
    assert result["a"].to_list() == result["b"].to_list()


def test_profile_records_dag_and_node_result_store_metrics():
    profile_dir = temp_dir()
    try:
        FactorEngine().evaluate_many(
            [
                ("a", "argmax(ts_mean(close, 2), 2)"),
                ("b", "argmin(ts_mean(close, 2), 2)"),
            ],
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
        )

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        batch = json.loads(
            (profile_dir / "latest_batch_details.jsonl").read_text(encoding="utf-8").splitlines()[0]
        )

        assert run["ast_node_count"] > run["dag_node_count"]
        assert run["deduplicated_node_count"] > 0
        assert run["shared_node_count"] > 0
        assert run["materialized_node_count"] > 0
        assert run["result_store_peak_entry_count"] >= 2
        assert batch["compiled_output_eval_time_ms"] >= 0
        assert batch["restore_assemble_time_ms"] >= 0
        assert batch["finalize_time_ms"] == batch["restore_assemble_time_ms"] + batch["append_time_ms"]
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_r4_repeated_heavy_compiled_subexpression_hits_node_store():
    profile_dir = temp_dir()
    try:
        FactorEngine().evaluate_many(
            [
                (
                    "reuse",
                    "ts_rank(close, 2) + ts_rank(close, 2) + ts_rank(close, 2)",
                )
            ],
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
        )

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        node_details = [
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        shared = [item for item in node_details if item["materialization_kind"] == "shared_intermediate"]

        assert run["total_compute_calls"] == 1
        assert run["node_store_compute_calls"] == 1
        assert run["compiled_output_heavy_occurrence_count"] == 0
        assert run["node_store_read_count"] >= 3
        assert run["reuse_consumer_count"] == 1
        assert shared
        assert shared[0]["compute_count"] == 1
        assert shared[0]["node_store_read_count"] >= 3
        assert shared[0]["reuse_consumer_count"] == 1
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_r4_dag_cse_off_preserves_results_without_store_hits():
    profile_dir = temp_dir()
    df = build_df()
    expressions = [
        (
            "reuse",
            "ts_rank(close, 2) + ts_rank(close, 2) + ts_rank(close, 2)",
        )
    ]
    try:
        optimized = FactorEngine().evaluate_many(expressions, df, dag_cse=True)
        baseline = FactorEngine().evaluate_many(
            expressions,
            df,
            dag_cse=False,
            profiling=True,
            profile_output_dir=profile_dir,
        )

        assert optimized["reuse"].to_list() == baseline["reuse"].to_list()

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        assert run["total_compute_calls"] == 3
        assert run["node_store_compute_calls"] == 0
        assert run["compiled_output_heavy_occurrence_count"] == 3
        assert run["total_store_hits"] == 0
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_r4_repeated_cheap_subexpression_stays_inline():
    profile_dir = temp_dir()
    try:
        FactorEngine().evaluate_many(
            [("cheap", "(close + open) + (close + open) + (close + open)")],
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
        )

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        node_details = (profile_dir / "latest_node_execution_details.jsonl").read_text(
            encoding="utf-8"
        )

        assert run["materialized_node_count"] == 0
        assert run["total_compute_calls"] == 0
        assert run["compiled_output_heavy_occurrence_count"] == 0
        assert run["total_store_hits"] == 0
        assert node_details == ""
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l1_planner_lifecycle_metadata_tracks_output_consumers():
    repeated = FactorEngine().inspect_dag(
        [("reuse", "ts_rank(close, 2) + ts_rank(close, 2)")],
        build_df(),
    )
    repeated_plan = next(
        item
        for item in repeated["lifecycle_plans"]
        if item["materialization_reason"] == "shared_reuse_and_path_normalization"
    )

    assert repeated_plan["producer_step"] is not None
    assert len(repeated_plan["consumer_steps"]) == 2
    assert repeated_plan["last_use_step"] == repeated_plan["consumer_steps"][-1]
    assert repeated_plan["ref_count_initial"] == 2
    assert repeated_plan["drop_candidate"] is True
    assert repeated_plan["drop_blocker_reason"] == ""

    multi = FactorEngine().inspect_dag(
        [
            ("a", "ts_rank(close, 2) + 1"),
            ("b", "ts_rank(close, 2) + 2"),
            ("c", "ts_rank(close, 2) + 3"),
            ("d", "ts_rank(close, 2) + 4"),
        ],
        build_df(),
    )
    multi_plan = next(
        item
        for item in multi["lifecycle_plans"]
        if item["materialization_reason"] == "shared_reuse_and_path_normalization"
    )

    assert len(multi_plan["consumer_steps"]) == 4
    assert multi_plan["ref_count_initial"] == 4
    assert multi_plan["last_use_step"] == multi_plan["consumer_steps"][-1]
    assert multi_plan["drop_candidate"] is True


def test_l1_runtime_trace_records_theoretical_and_actual_node_lifecycle():
    profile_dir = temp_dir()
    try:
        FactorEngine().evaluate_many(
            [("reuse", "ts_rank(close, 2) + ts_rank(close, 2)")],
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
        )

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        batch = json.loads(
            (profile_dir / "latest_batch_details.jsonl").read_text(encoding="utf-8").splitlines()[0]
        )
        node_details = [
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        shared = next(
            item for item in node_details if item["materialization_kind"] == "shared_intermediate"
        )

        assert shared["planner_producer_step"] is not None
        assert shared["planner_consumer_steps"]
        assert shared["planner_last_use_step"] == shared["planner_consumer_steps"][-1]
        assert shared["planner_ref_count_initial"] == 2
        assert shared["planner_drop_candidate"] is True
        assert shared["materialized_at_step"] == shared["planner_producer_step"]
        assert shared["first_read_step"] == shared["planner_consumer_steps"][0]
        assert shared["last_read_step"] == shared["planner_last_use_step"]
        assert shared["retained_until_end"] is True
        assert shared["theoretical_release_step"] == shared["planner_last_use_step"]
        assert shared["batch_end_step"] > shared["planner_last_use_step"]
        assert shared["release_lag_steps"] == shared["structural_release_lag_steps"]
        assert shared["structural_release_lag_steps"] > 0
        assert shared["retained_past_last_read"] is True
        assert shared["finalize_retention_lag_steps"] > 0
        assert shared["potential_live_bytes_step_savings"] > 0
        assert shared["l2_first_wave_candidate"] is True
        assert run["lifecycle_candidate_count"] == 1
        assert run["lifecycle_releasable_node_count"] == 1
        assert run["batch_end_step"] == shared["batch_end_step"]
        assert run["max_structural_release_lag_steps"] == shared["structural_release_lag_steps"]
        assert run["potential_live_bytes_step_savings"] == shared[
            "potential_live_bytes_step_savings"
        ]
        assert run["l2_first_wave_candidate_count"] == 1
        assert batch["lifecycle_peak_live_node_count"] == 1
        assert batch["batch_end_step"] == shared["batch_end_step"]
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l2_1_first_wave_drops_repeated_heavy_store_entry_after_planned_uses():
    profile_dir = temp_dir()
    try:
        expressions = [("reuse", "ts_rank(close, 2) + ts_rank(close, 2)")]
        baseline = FactorEngine().evaluate_many(expressions, build_df())
        active = FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
            lifecycle_mode="first_wave",
        )
        assert_frame_equal(active, baseline)

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        node_details = [
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        shared = next(
            item for item in node_details if item["materialization_kind"] == "shared_intermediate"
        )

        assert shared["active_drop_eligible"] is True
        assert shared["dropped_at_step"] == shared["drop_expected_step"]
        assert shared["drop_delay_steps"] == 0
        assert shared["drop_reason"] == "ref_count_zero"
        assert shared["ref_count_remaining_final"] == 0
        assert shared["drop_missed"] is False
        assert shared["retained_until_end"] is False
        assert run["dropped_node_count"] == 1
        assert run["drop_hit_count"] == 1
        assert run["drop_miss_count"] == 0
        assert run["lifecycle_mode"] == "first_wave"
        assert run["lifecycle_effective"] is True
        assert run["peak_live_bytes_est_after_drop"] < run["peak_live_bytes_est_before_drop"]
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l2_1_first_wave_drops_multi_consumer_after_last_consumer_only():
    profile_dir = temp_dir()
    try:
        expressions = [
            ("a", "ts_rank(close, 2) + 1"),
            ("b", "ts_rank(close, 2) + 2"),
            ("c", "ts_rank(close, 2) + 3"),
            ("d", "ts_rank(close, 2) + 4"),
        ]
        baseline = FactorEngine().evaluate_many(expressions, build_df())
        active = FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
            lifecycle_mode="first_wave",
        )
        assert_frame_equal(active, baseline)

        shared = next(
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if json.loads(line)["materialization_kind"] == "shared_intermediate"
        )

        assert shared["planner_ref_count_initial"] == 4
        assert shared["node_store_read_count"] == 4
        assert shared["reuse_consumer_count"] == 4
        assert shared["drop_expected_step"] == shared["planner_last_use_step"]
        assert shared["dropped_at_step"] == shared["planner_consumer_steps"][-1]
        assert shared["dropped_at_step"] == shared["drop_expected_step"]
        assert shared["ref_count_remaining_final"] == 0
        assert shared["drop_missed"] is False
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l2_1_first_wave_does_not_active_drop_native_heavy_probe():
    profile_dir = temp_dir()
    try:
        expressions = [("native", "argmax(close, 2) + argmax(close, 2)")]
        baseline = FactorEngine().evaluate_many(expressions, build_df())
        active = FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
            lifecycle_mode="first_wave",
        )
        assert_frame_equal(active, baseline)

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        shared = next(
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if json.loads(line)["materialization_kind"] == "shared_intermediate"
        )

        assert shared["node_lifecycle_class"] == "native_heavy"
        assert shared["l2_first_wave_candidate"] is False
        assert shared["active_drop_eligible"] is False
        assert shared["dropped_at_step"] is None
        assert shared["drop_missed"] is False
        assert run["dropped_node_count"] == 0
        assert run["l2_first_wave_candidate_count"] == 0
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l3a_native_heavy_lifecycle_is_observable_only_without_active_drop():
    profile_dir = temp_dir()
    try:
        expressions = [("native", "argmax(close, 2) + argmax(close, 2)")]
        FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
            lifecycle_mode="first_wave",
        )

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        shared = next(
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if json.loads(line)["materialization_kind"] == "shared_intermediate"
        )

        assert run["native_heavy_node_count"] == 1
        assert run["native_heavy_observable_only_count"] == 1
        assert run["native_heavy_candidate_future_count"] == 0
        assert run["native_node_store_read_count"] == shared["node_store_read_count"]
        assert run["native_storage_residency_bytes"] == shared["bytes_estimate"]
        assert shared["node_lifecycle_class"] == "native_heavy"
        assert shared["native_heavy_lifecycle_eligibility"] == "observable_only"
        assert shared["native_heavy_blocker_reason"] == "unstable_consumer_semantics"
        assert shared["native_rewrite_applied"] is True
        assert shared["native_helper_usage_pattern"] == "single_consumer_multi_read"
        assert shared["native_logical_consumer_count"] == shared["reuse_consumer_count"]
        assert shared["native_effective_use_count"] == shared["node_store_read_count"]
        assert shared["active_drop_eligible"] is False
        assert shared["dropped_at_step"] is None
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l3a_native_heavy_cse_off_reports_fallback_without_native_lifecycle_candidate():
    profile_dir = temp_dir()
    try:
        expressions = [("native", "argmax(close, 2) + argmax(close, 2)")]
        FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
            dag_cse=False,
            lifecycle_mode="off",
        )

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        shared = next(
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if json.loads(line)["node_lifecycle_class"] == "native_heavy"
        )
        assert run["native_fallback_eval_count"] == 1
        assert run["native_heavy_node_count"] == 1
        assert run["native_heavy_forbidden_count"] == 1
        assert run["native_heavy_candidate_future_count"] == 0
        assert shared["native_heavy_lifecycle_eligibility"] == "forbidden"
        assert shared["native_heavy_blocker_reason"] == "unresolved_fallback_path"
        assert shared["native_rewrite_applied"] is False
        assert run["dropped_node_count"] == 0
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l3b_helper_column_lifecycle_observes_logically_dead_shared_helper():
    profile_dir = temp_dir()
    try:
        expressions = [("reuse", "ts_rank(close, 2) + ts_rank(close, 2)")]
        FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
            lifecycle_mode="off",
        )

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        helper = next(
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if json.loads(line)["materialization_kind"] == "shared_intermediate"
        )

        assert helper["helper_column_name"] is not None
        assert helper["helper_column_created_step"] == helper["planner_producer_step"]
        assert helper["helper_last_use_step"] == helper["planner_last_use_step"]
        assert helper["helper_structural_lag_steps"] > 0
        assert helper["helper_bytes_estimate"] > 0
        assert helper["helper_potential_bytes_step_savings"] > 0
        assert helper["helper_lifecycle_state"] == "logically_dead"
        assert helper["helper_drop_blocker_reason"] == ""
        assert helper["helper_retained_until_end"] is True
        assert run["helper_column_count"] == 1
        assert run["helper_releasable_count"] == 1
        assert run["helper_blocked_count"] == 0
        assert run["helper_peak_live_bytes"] == helper["helper_bytes_estimate"]
        assert run["helper_potential_savings"] == helper[
            "helper_potential_bytes_step_savings"
        ]
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l3b_helper_observability_does_not_delete_frame_columns_under_lifecycle():
    profile_dir = temp_dir()
    try:
        expressions = [("reuse", "ts_rank(close, 2) + ts_rank(close, 2)")]
        result = FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
            lifecycle_mode="first_wave",
        )

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        helper = next(
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if json.loads(line)["materialization_kind"] == "shared_intermediate"
        )

        assert "reuse" in result.columns
        assert run["dropped_node_count"] == 1
        assert run["helper_column_count"] == 1
        assert helper["dropped_at_step"] == helper["drop_expected_step"]
        assert helper["helper_lifecycle_state"] == "logically_dead"
        assert helper["helper_retained_until_end"] is True
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l3b_3_repeated_heavy_helper_active_drop_is_batch_safe():
    off_dir = temp_dir()
    active_dir = temp_dir()
    try:
        expressions = [("reuse", "ts_rank(close, 2) + ts_rank(close, 2)")]
        baseline = FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=off_dir,
            lifecycle_mode="first_wave",
            helper_lifecycle_mode="off",
            benchmark_name="r4_repeated_heavy_2_cse_on",
        )
        active = FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=active_dir,
            lifecycle_mode="first_wave",
            helper_lifecycle_mode="first_wave",
            benchmark_name="r4_repeated_heavy_2_cse_on",
        )
        assert_frame_equal(active, baseline)

        off_run = json.loads((off_dir / "latest_run.json").read_text(encoding="utf-8"))
        run = json.loads((active_dir / "latest_run.json").read_text(encoding="utf-8"))
        helper = next(
            json.loads(line)
            for line in (active_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if json.loads(line)["materialization_kind"] == "shared_intermediate"
        )

        assert off_run["helper_dropped_count"] == 0
        assert off_run["helper_peak_live_bytes_after_drop"] == off_run["helper_peak_live_bytes"]
        assert run["helper_lifecycle_mode"] == "first_wave"
        assert run["helper_lifecycle_effective"] is True
        assert run["helper_dropped_count"] == 1
        assert run["helper_drop_miss_count"] == 0
        assert run["helper_peak_live_bytes_before_drop"] > run[
            "helper_peak_live_bytes_after_drop"
        ]
        assert run["helper_frame_width_before_drop"] > run["helper_frame_width_after_drop"]
        assert helper["helper_drop_candidate"] is True
        assert helper["helper_drop_revalidated"] is True
        assert helper["helper_dropped_at_step"] == helper["helper_drop_safe_step"]
        assert helper["helper_drop_delay_steps"] == 0
        assert helper["helper_retained_until_end"] is False
        assert helper["helper_drop_reason"] == "batch_safe_projection"
    finally:
        shutil.rmtree(off_dir, ignore_errors=True)
        shutil.rmtree(active_dir, ignore_errors=True)


def test_l3b_3_multi_shared_helpers_drop_as_independent_batch():
    profile_dir = temp_dir()
    try:
        expressions = [
            (
                "out",
                "ts_rank(close, 2) + ts_rank(close, 2) + "
                "ts_rank(open, 2) + ts_rank(open, 2)",
            )
        ]
        baseline = FactorEngine().evaluate_many(expressions, build_df())
        active = FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
            lifecycle_mode="first_wave",
            helper_lifecycle_mode="first_wave",
            benchmark_name="r4_multi_shared_nodes_2_cse_on",
        )
        assert_frame_equal(active, baseline)

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        shared = [
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if json.loads(line)["materialization_kind"] == "shared_intermediate"
        ]

        assert len(shared) == 2
        assert run["helper_dropped_count"] == 2
        assert run["helper_drop_miss_count"] == 0
        assert run["helper_peak_live_bytes_after_drop"] == 0
        assert all(item["helper_dropped_at_step"] == item["helper_drop_safe_step"] for item in shared)
        assert all(item["helper_drop_delay_steps"] == 0 for item in shared)
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l3b_3_partial_reuse_helper_drop_waits_until_safe_step():
    profile_dir = temp_dir()
    try:
        expressions = [
            ("partial_a", "ts_mean(close, 2) + 1"),
            ("partial_b", "ts_rank(ts_mean(close, 2), 2)"),
        ]
        baseline = FactorEngine().evaluate_many(expressions, build_df())
        active = FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
            lifecycle_mode="first_wave",
            helper_lifecycle_mode="first_wave",
            benchmark_name="r4_partial_reuse_2_cse_on",
        )
        assert_frame_equal(active, baseline)

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        helper = next(
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if json.loads(line)["materialization_kind"] == "shared_intermediate"
        )

        assert run["helper_dropped_count"] == 1
        assert run["helper_drop_miss_count"] == 0
        assert helper["helper_dropped_at_step"] >= helper["helper_last_use_step"]
        assert helper["helper_dropped_at_step"] == helper["helper_drop_safe_step"]
        assert helper["helper_drop_candidate"] is True
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l3b_3_nested_dag_is_denied_from_helper_first_wave():
    profile_dir = temp_dir()
    try:
        expressions = [
            ("out", "ts_rank(ts_mean(close, 2), 2) + ts_rank(ts_mean(close, 2), 2)")
        ]
        FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
            lifecycle_mode="first_wave",
            helper_lifecycle_mode="first_wave",
            benchmark_name="r4_nested_dag_2_cse_on",
        )

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        shared = [
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if json.loads(line)["materialization_kind"] == "shared_intermediate"
        ]

        assert run["helper_lifecycle_mode"] == "first_wave"
        assert run["helper_dropped_count"] == 0
        assert run["helper_lifecycle_effective"] is False
        assert len(shared) == 2
        assert all(item["helper_drop_candidate"] is False for item in shared)
        assert all(item["helper_dropped_at_step"] is None for item in shared)
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l3b_5_second_wave_nested_drops_pure_chain_helpers_only():
    profile_dir = temp_dir()
    try:
        expressions = [
            ("out", "ts_rank(ts_mean(close, 2), 2) + ts_rank(ts_mean(close, 2), 2)")
        ]
        baseline = FactorEngine().evaluate_many(
            expressions,
            build_df(),
            lifecycle_mode="first_wave",
            helper_lifecycle_mode="first_wave",
            benchmark_name="r4_nested_probe_a_2_cse_on",
        )
        active = FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
            lifecycle_mode="first_wave",
            helper_lifecycle_mode="second_wave_nested",
            benchmark_name="r4_nested_probe_a_2_cse_on",
        )
        assert_frame_equal(active, baseline)

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        shared = [
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if json.loads(line)["materialization_kind"] == "shared_intermediate"
        ]

        assert run["helper_lifecycle_mode"] == "second_wave_nested"
        assert run["nested_helper_lifecycle_effective"] is True
        assert run["nested_helper_dropped_count"] == 2
        assert run["nested_helper_drop_missed_count"] == 0
        assert run["nested_helper_peak_live_bytes_before_drop"] > run[
            "nested_helper_peak_live_bytes_after_drop"
        ]
        assert run["nested_helper_frame_width_before_drop"] > run[
            "nested_helper_frame_width_after_drop"
        ]
        assert len(shared) == 2
        assert all(item["helper_drop_candidate_kind"] == "second_wave_nested" for item in shared)
        assert all(item["nested_helper_candidate"] is True for item in shared)
        assert all(item["helper_dropped_at_step"] == item["helper_drop_safe_step"] for item in shared)
        assert all(item["helper_drop_delay_steps"] == 0 for item in shared)
        assert all(item["nested_helper_miss_reason"] == "" for item in shared)
        assert all("nested_helper_candidate" in item["nested_helper_trace_events"] for item in shared)
        assert all("nested_helper_revalidate_pass" in item["nested_helper_trace_events"] for item in shared)
        assert all("nested_helper_dropped" in item["nested_helper_trace_events"] for item in shared)

        inner = next(item for item in shared if item["parent_helper_column_name"])
        outer = next(item for item in shared if item["child_helper_columns"])
        assert inner["helper_structural_dependency_end_step"] >= inner[
            "helper_logical_last_use_step"
        ]
        assert inner["helper_structural_dependency_end_step"] >= outer[
            "helper_logical_last_use_step"
        ]
        assert inner["helper_drop_safe_step"] >= inner["helper_structural_dependency_end_step"]
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l3b_5_first_wave_semantics_stay_unchanged_for_nested_dag():
    profile_dir = temp_dir()
    try:
        expressions = [
            ("out", "ts_rank(ts_mean(close, 2), 2) + ts_rank(ts_mean(close, 2), 2)")
        ]
        FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
            lifecycle_mode="first_wave",
            helper_lifecycle_mode="first_wave",
            benchmark_name="r4_nested_probe_a_2_cse_on",
        )

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        shared = [
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if json.loads(line)["materialization_kind"] == "shared_intermediate"
        ]

        assert run["helper_lifecycle_mode"] == "first_wave"
        assert run["helper_dropped_count"] == 0
        assert run["nested_helper_dropped_count"] == 0
        assert run["nested_helper_lifecycle_effective"] is False
        assert all(item["helper_drop_candidate"] is False for item in shared)
        assert all(item["helper_dropped_at_step"] is None for item in shared)
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l3b_5_second_wave_misses_shared_inner_shape():
    profile_dir = temp_dir()
    try:
        expressions = [
            ("out", "ts_rank(ts_mean(close, 2), 2) + ts_std(ts_mean(close, 2), 2)")
        ]
        baseline = FactorEngine().evaluate_many(expressions, build_df())
        active = FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
            lifecycle_mode="first_wave",
            helper_lifecycle_mode="second_wave_nested",
            benchmark_name="r4_nested_probe_c_2_cse_on",
        )
        assert_frame_equal(active, baseline)

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        shared = [
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if json.loads(line)["materialization_kind"] == "shared_intermediate"
        ]

        assert run["nested_helper_dropped_count"] == 0
        assert run["nested_helper_lifecycle_effective"] is False
        assert shared
        assert all(item["nested_helper_candidate"] is False for item in shared)
        assert all(item["helper_dropped_at_step"] is None for item in shared)
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l3b_5_second_wave_misses_non_helper_downstream_consumer():
    profile_dir = temp_dir()
    try:
        expressions = [
            ("direct", "ts_mean(close, 2) + 1"),
            ("nested", "ts_rank(ts_mean(close, 2), 2) + ts_rank(ts_mean(close, 2), 2)"),
        ]
        baseline = FactorEngine().evaluate_many(expressions, build_df())
        active = FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
            lifecycle_mode="first_wave",
            helper_lifecycle_mode="second_wave_nested",
            benchmark_name="r4_nested_probe_mixed_2_cse_on",
        )
        assert_frame_equal(active, baseline)

        shared = [
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if json.loads(line)["materialization_kind"] == "shared_intermediate"
        ]
        inner = next(item for item in shared if item["parent_helper_column_name"])

        assert inner["nested_helper_candidate"] is False
        assert inner["nested_helper_miss_reason"] == "non_helper_consumer"
        assert inner["helper_dropped_at_step"] is None
        assert "nested_helper_drop_missed" in inner["nested_helper_trace_events"]
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l3b_5_second_wave_misses_output_pinned_helper():
    profile_dir = temp_dir()
    try:
        expressions = [
            ("pinned", "ts_mean(close, 2)"),
            ("nested", "ts_rank(ts_mean(close, 2), 2) + ts_rank(ts_mean(close, 2), 2)"),
        ]
        baseline = FactorEngine().evaluate_many(expressions, build_df())
        active = FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
            lifecycle_mode="first_wave",
            helper_lifecycle_mode="second_wave_nested",
            benchmark_name="r4_nested_probe_pinned_2_cse_on",
        )
        assert_frame_equal(active, baseline)

        shared = [
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if json.loads(line)["materialization_kind"] == "shared_intermediate"
        ]
        all_helpers = [
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if json.loads(line)["helper_column_name"] is not None
        ]
        pinned = next(item for item in all_helpers if item["parent_helper_column_name"])

        assert not any(item["helper_dropped_at_step"] is not None for item in all_helpers)
        assert all(item["helper_drop_candidate"] is False for item in shared)
        assert pinned["helper_drop_blocker_reason"] == "final_output_dependency"
        assert pinned["nested_helper_miss_reason"] in {"has_blocker", "output_pinned"}
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l2_2_wave_2a_drops_multiple_shared_nodes_independently():
    profile_dir = temp_dir()
    try:
        expressions = [
            (
                "out",
                "ts_rank(close, 2) + ts_rank(close, 2) + "
                "ts_rank(open, 2) + ts_rank(open, 2)",
            )
        ]
        baseline = FactorEngine().evaluate_many(expressions, build_df())
        active = FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
            lifecycle_mode="first_wave",
        )
        assert_frame_equal(active, baseline)

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        node_details = [
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        dropped = [
            item for item in node_details if item["materialization_kind"] == "shared_intermediate"
        ]

        assert len(dropped) == 2
        assert all(item["dropped_at_step"] == item["drop_expected_step"] for item in dropped)
        assert all(item["drop_delay_steps"] == 0 for item in dropped)
        assert all(item["ref_count_remaining_final"] == 0 for item in dropped)
        assert run["dropped_node_count"] == 2
        assert run["drop_miss_count"] == 0
        assert run["multi_node_overlap_peak"] == 2
        assert run["multi_node_peak_live_bytes_before"] == sum(
            item["bytes_estimate"] for item in dropped
        )
        assert run["multi_node_peak_live_bytes_after"] == 0
        assert set(run["per_node_drop_order"]) == {item["node_id"] for item in dropped}
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l2_2_wave_2b_nested_dag_drops_inner_before_outer():
    profile_dir = temp_dir()
    try:
        expressions = [
            ("out", "ts_rank(ts_mean(close, 2), 2) + ts_rank(ts_mean(close, 2), 2)")
        ]
        baseline = FactorEngine().evaluate_many(expressions, build_df())
        active = FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
            lifecycle_mode="first_wave",
        )
        assert_frame_equal(active, baseline)

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        node_details = [
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        shared = [
            item for item in node_details if item["materialization_kind"] == "shared_intermediate"
        ]
        inner = next(item for item in shared if item["parent_node_id"] is not None)
        outer = next(item for item in shared if item["parent_node_id"] is None)

        assert len(shared) == 2
        assert inner["node_depth"] < outer["node_depth"]
        assert inner["dropped_at_step"] <= outer["dropped_at_step"]
        assert inner["drop_expected_step"] == outer["planner_producer_step"]
        assert all(item["drop_delay_steps"] == 0 for item in shared)
        assert all(item["compute_count"] == 1 for item in shared)
        assert run["nested_drop_order_valid"] is True
        assert run["dropped_node_count"] == 2
        assert run["drop_miss_count"] == 0
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l2_2_wave_2c_partial_reuse_waits_for_last_consumer_step():
    profile_dir = temp_dir()
    try:
        expressions = [
            ("a", "ts_mean(close, 2) + 1"),
            ("b", "ts_rank(ts_mean(close, 2), 2)"),
        ]
        baseline = FactorEngine().evaluate_many(expressions, build_df())
        active = FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=profile_dir,
            lifecycle_mode="first_wave",
        )
        assert_frame_equal(active, baseline)

        run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
        shared = next(
            json.loads(line)
            for line in (profile_dir / "latest_node_execution_details.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if json.loads(line)["materialization_kind"] == "shared_intermediate"
        )

        assert shared["planner_ref_count_initial"] == 2
        assert len(set(shared["planner_consumer_steps"])) == 2
        assert shared["drop_expected_step"] == max(shared["planner_consumer_steps"])
        assert shared["dropped_at_step"] == shared["drop_expected_step"]
        assert shared["dropped_at_step"] >= shared["last_read_step"]
        assert shared["drop_delay_steps"] == 0
        assert shared["drop_missed"] is False
        assert run["partial_reuse_safety_flag"] is True
        assert run["dropped_node_count"] == 1
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def test_l2_3_lifecycle_mode_alias_and_off_boundary():
    off_dir = temp_dir()
    alias_dir = temp_dir()
    try:
        expressions = [("reuse", "ts_rank(close, 2) + ts_rank(close, 2)")]
        FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=off_dir,
            lifecycle_mode="off",
        )
        FactorEngine().evaluate_many(
            expressions,
            build_df(),
            profiling=True,
            profile_output_dir=alias_dir,
            lifecycle=True,
        )

        off_run = json.loads((off_dir / "latest_run.json").read_text(encoding="utf-8"))
        alias_run = json.loads((alias_dir / "latest_run.json").read_text(encoding="utf-8"))

        assert off_run["lifecycle_mode"] == "off"
        assert off_run["dropped_node_count"] == 0
        assert off_run["lifecycle_effective"] is False
        assert alias_run["lifecycle_mode"] == "first_wave"
        assert alias_run["dropped_node_count"] == 1
        assert normalize_lifecycle_mode(lifecycle=True) == "first_wave"
    finally:
        shutil.rmtree(off_dir, ignore_errors=True)
        shutil.rmtree(alias_dir, ignore_errors=True)


def test_m3_output_attach_mode_policy_is_explicit():
    assert normalize_output_attach_mode(output_attach_mode=None) == "materialize"
    assert normalize_output_attach_mode(output_attach_mode="materialize") == "materialize"
    assert normalize_output_attach_mode(output_attach_mode="finalize_select") == "finalize_select"
    assert normalize_output_attach_mode(output_attach_mode="last_use_select") == "last_use_select"
    assert normalize_planner_cse_mode(planner_cse_mode=None) == "baseline"
    assert normalize_planner_cse_mode(planner_cse_mode="baseline") == "baseline"
    assert (
        normalize_planner_cse_mode(planner_cse_mode="expanded_repeated_family")
        == "expanded_repeated_family"
    )
    assert normalize_fusion_mode(fusion_mode=None) == "off"
    assert normalize_fusion_mode(fusion_mode="off") == "off"
    assert normalize_fusion_mode(fusion_mode="unary_chain_fusion") == "unary_chain_fusion"
    assert normalize_frame_projection_mode(frame_projection_mode=None) == "off"
    assert normalize_frame_projection_mode(frame_projection_mode="off") == "off"
    assert (
        normalize_frame_projection_mode(frame_projection_mode="dependency_driven")
        == "dependency_driven"
    )


def test_m3_recomputation_guardrail_blocks_unsafe_threshold_skip():
    engine = FactorEngine()
    expr = engine.parse("ts_rank(close, 2) + ts_rank(close, 2)")
    planner = ExecutionPlanner()

    blocked = planner.build_expression_dag(
        [("out", expr)],
        materialization_threshold_mode="reuse_ge_3_guarded",
        recomputation_guardrail_max_expansion=0,
    )
    allowed = planner.build_expression_dag(
        [("out", expr)],
        materialization_threshold_mode="reuse_ge_3_guarded",
        recomputation_guardrail_max_expansion=1,
    )

    blocked_shared = next(item for item in blocked.nodes if item.label == "ts_rank")
    allowed_shared = next(item for item in allowed.nodes if item.label == "ts_rank")

    assert blocked_shared.recomputation_expansion_if_inline == 1
    assert blocked_shared.recomputation_guardrail_pass is False
    assert blocked_shared.materialize is True
    assert allowed_shared.recomputation_guardrail_pass is True
    assert allowed_shared.materialize is False


def test_m4_expanded_cse_merges_neutral_add_rolling_family_only():
    engine = FactorEngine()
    expressions = [
        ("out", "ts_rank(close + 0, 2) + ts_rank(close, 2)"),
    ]
    parsed = [(name, engine.parse(expr)) for name, expr in expressions]
    planner = ExecutionPlanner()

    baseline = planner.build_expression_dag(parsed, planner_cse_mode="baseline")
    expanded = planner.build_expression_dag(
        parsed,
        planner_cse_mode="expanded_repeated_family",
    )

    baseline_rank_nodes = [
        node for node in baseline.nodes if node.label == "ts_rank"
    ]
    expanded_rank_nodes = [
        node for node in expanded.nodes if node.label == "ts_rank"
    ]
    audit = expanded.to_inspection()["expanded_cse_audit"]

    assert len(baseline_rank_nodes) == 2
    assert len(expanded_rank_nodes) == 1
    assert expanded_rank_nodes[0].occurrence_count == 2
    assert expanded_rank_nodes[0].materialize is True
    assert audit["selected_family"] == "rolling_neutral_add_input"
    assert audit["matched_groups"] == 1
    assert audit["reused_groups"] == 1


def test_m4_unary_chain_fusion_suppresses_only_inner_helper():
    engine = FactorEngine()
    parsed = [
        (
            "out",
            engine.parse(
                "ts_rank(ts_mean(close, 2), 2) + ts_rank(ts_mean(close, 2), 2)"
            ),
        )
    ]
    planner = ExecutionPlanner()

    baseline = planner.build_expression_dag(parsed, fusion_mode="off")
    fused = planner.build_expression_dag(parsed, fusion_mode="unary_chain_fusion")

    baseline_mean = next(node for node in baseline.nodes if node.label == "ts_mean")
    baseline_rank = next(node for node in baseline.nodes if node.label == "ts_rank")
    fused_mean = next(node for node in fused.nodes if node.label == "ts_mean")
    fused_rank = next(node for node in fused.nodes if node.label == "ts_rank")
    audit = fused.to_inspection()["fusion_audit"]

    assert baseline_mean.materialize is True
    assert baseline_rank.materialize is True
    assert fused_mean.materialize is False
    assert fused_mean.share_reason == "fused_into_parent_unary_chain"
    assert fused_rank.materialize is True
    assert audit["selected_family"] == "rolling_unary_chain_ts_mean_into_ts_rank"
    assert audit["matched_chains"] == 1
    assert audit["nodes_reduced"] == 1


def test_l2_3_first_wave_candidate_single_source_allowlist_and_denylist():
    base = dict(
        materialization_eligibility="materialize_for_both",
        drop_candidate=True,
        drop_blocker_reason="",
        structural_release_lag_steps=1,
        node_lifecycle_class="shared_heavy",
        bytes_estimate=8,
    )
    assert is_first_wave_candidate(FirstWaveCandidateInput(**base)) is True

    denied_cases = [
        {"materialization_eligibility": "inline_required"},
        {"drop_candidate": False},
        {"drop_blocker_reason": "final_output_dependency"},
        {"structural_release_lag_steps": 0},
        {"node_lifecycle_class": "native_heavy"},
        {"bytes_estimate": 0},
    ]
    for override in denied_cases:
        candidate = FirstWaveCandidateInput(**(base | override))
        assert is_first_wave_candidate(candidate) is False


def test_l3b_3_helper_candidate_single_source_allowlist_and_denylist():
    base = dict(
        helper_lifecycle_state="logically_dead",
        helper_drop_blocker_reason="",
        helper_structural_lag_steps=1,
        helper_bytes_estimate=8,
        materialization_kind="shared_intermediate",
        materialization_eligibility="materialize_for_both",
        node_lifecycle_class="shared_heavy",
        workload_name="repeated_heavy",
        nested_dependency_present=False,
    )
    assert is_first_wave_helper_candidate(HelperFirstWaveCandidateInput(**base)) is True
    assert normalize_helper_lifecycle_mode(helper_lifecycle_mode=None) == "off"
    assert normalize_helper_lifecycle_mode(helper_lifecycle_mode="first_wave") == "first_wave"

    denied_cases = [
        {"helper_lifecycle_state": "active"},
        {"helper_drop_blocker_reason": "final_output_dependency"},
        {"helper_structural_lag_steps": 0},
        {"helper_bytes_estimate": 0},
        {"materialization_kind": "final"},
        {"materialization_eligibility": "inline_required"},
        {"node_lifecycle_class": "native_heavy"},
        {"workload_name": "nested_dag"},
        {"nested_dependency_present": True},
    ]
    for override in denied_cases:
        candidate = HelperFirstWaveCandidateInput(**(base | override))
        assert is_first_wave_helper_candidate(candidate) is False


def test_l3b_5_second_wave_nested_candidate_policy_is_separate_from_first_wave():
    base = dict(
        helper_lifecycle_state="logically_dead",
        helper_drop_blocker_reason="",
        helper_structural_lag_steps=1,
        helper_bytes_estimate=8,
        materialization_kind="shared_intermediate",
        materialization_eligibility="materialize_for_both",
        node_lifecycle_class="shared_heavy",
        parent_helper_column_name="__parent",
        child_helper_columns=(),
        parent_child_count=1,
        materialized_helper_count=2,
        nested_output_pinned=False,
        helper_structural_dependency_end_step=6,
        helper_drop_safe_step=7,
        node_store_read_count=1,
        reuse_consumer_count=1,
    )

    assert normalize_helper_lifecycle_mode(
        helper_lifecycle_mode="second_wave_nested"
    ) == "second_wave_nested"
    assert is_second_wave_nested_candidate(HelperSecondWaveNestedCandidateInput(**base)) is True

    denied_cases = [
        {"parent_helper_column_name": None, "child_helper_columns": ()},
        {"helper_drop_blocker_reason": "final_output_dependency"},
        {"node_lifecycle_class": "native_heavy"},
        {"materialization_kind": "final"},
        {"materialization_eligibility": "inline_required"},
        {"helper_lifecycle_state": "active"},
        {"helper_structural_lag_steps": 0},
        {"child_helper_columns": ("a", "b")},
        {"parent_child_count": 2},
        {"materialized_helper_count": 3},
        {"nested_output_pinned": True},
        {"reuse_consumer_count": 2},
        {"helper_drop_safe_step": 5},
    ]
    for override in denied_cases:
        candidate = HelperSecondWaveNestedCandidateInput(**(base | override))
        assert is_second_wave_nested_candidate(candidate) is False
