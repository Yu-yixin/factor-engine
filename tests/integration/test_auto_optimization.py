from factor_engine.auto_optimization import (
    BottleneckReport,
    OptimizationCandidate,
    OptimizationHistoryEntry,
    build_structural_bottleneck_report,
    candidate_seen_before,
    detect_bottlenecks,
    generate_m3_candidates,
    generate_m3_proposal_candidates,
    generate_m4_executable_candidates,
    generate_m4_candidates,
    optimization_score,
    select_best_candidate,
    stagnation_detected,
)
from factor_engine.auto_optimization import CandidateEvaluation


def candidate(identifier: str, score: float) -> CandidateEvaluation:
    opt = OptimizationCandidate(
        id=identifier,
        phase="m3_v1",
        kind="attach_strategy",
        params={},
        rationale="test",
        candidate_status="executable",
        engine_supported=True,
    )
    return CandidateEvaluation(
        candidate=opt,
        score=score,
        accepted=score > 0,
        memory_reduction=score,
        frame_width_reduction=0,
        time_increase=0,
        metrics={},
    )


def test_m3_score_rewards_memory_and_width_and_penalizes_time():
    score = optimization_score(
        memory_reduction=10,
        frame_width_reduction=5,
        time_increase=3,
    )

    assert score == 5.9


def test_m3_candidate_generation_returns_only_executable_knobs():
    history = [
        OptimizationHistoryEntry(
            id="m3_delayed_output_attach_finalize_select",
            score=0,
            accepted=False,
            memory_reduction=0,
            frame_width_reduction=0,
            time_increase=0,
        )
    ]
    generated = generate_m3_candidates(history, max_candidates_per_round=2)

    assert [item.id for item in generated] == [
        "m3_projection_dependency_driven",
        "m3_materialization_reuse_ge_3",
    ]
    assert candidate_seen_before(
        OptimizationCandidate(
            id="m3_delayed_output_attach_finalize_select",
            phase="m3_v1",
            kind="attach_strategy",
            params={},
            rationale="test",
            candidate_status="executable",
            engine_supported=True,
        ),
        history,
    )


def test_m3_proposals_are_queued_but_not_executable():
    executable = generate_m3_candidates([], max_candidates_per_round=4)
    proposals = generate_m3_proposal_candidates([], max_candidates_per_round=3)

    assert [item.id for item in executable] == [
        "m3_delayed_output_attach_finalize_select",
        "m3_projection_dependency_driven",
        "m3_materialization_reuse_ge_3",
        "m3_attach_last_use",
    ]
    assert all(item.is_executable is True for item in executable)
    assert proposals == []


def test_m3_select_best_allows_periodic_exploration():
    evaluations = [candidate("best", 10), candidate("second", 5), candidate("bad", -1)]

    assert select_best_candidate(evaluations, round_index=1).candidate.id == "best"
    assert select_best_candidate(evaluations, round_index=3).candidate.id == "second"


def test_m3_stagnation_requires_three_bad_rounds_low_improvement_and_exhaustion():
    history = [
        OptimizationHistoryEntry("a", 0, False, 0, 0, 0),
        OptimizationHistoryEntry("b", -1, False, 0, 0, 0),
        OptimizationHistoryEntry("c", 0, False, 0, 0, 0),
    ]

    assert stagnation_detected(
        history,
        memory_improvement=1.5,
        frame_improvement=1.0,
        candidate_exhausted=True,
    )
    assert not stagnation_detected(
        history,
        memory_improvement=3.0,
        frame_improvement=1.0,
        candidate_exhausted=True,
    )


def test_bridge_bottleneck_detection_and_m4_candidate_generation():
    report = detect_bottlenecks(
        run_summaries=[{"workload": "w", "total_time_sec": 1.0}],
        node_details=[
            {
                "node_id": "n1",
                "identity": "rank",
                "bytes_estimate": 100,
                "node_store_read_count": 4,
                "reuse_consumer_count": 4,
                "node_depth": 3,
                "consumer_count": 4,
                "compute_time_ms": 9.0,
            }
        ],
    )
    candidates = generate_m4_candidates(report)

    assert isinstance(report, BottleneckReport)
    assert report.bottleneck_detected
    assert {item.kind for item in candidates} >= {
        "cse_expansion",
        "execution_route_rewrite",
        "node_fusion",
        "batching_segmentation",
        "materialization_elimination",
    }
    assert [item.id for item in candidates] == [
        "m4_cse_expand_repeated_subgraphs",
        "m4_fuse_deep_operator_chains",
        "m4_eliminate_materialized_intermediates",
        "m4_batch_wide_fanout_nodes",
        "m4_rewrite_heavy_execution_path",
    ]


def test_m4_structural_bottleneck_report_is_ranked_and_explainable():
    report = build_structural_bottleneck_report(
        run_summaries=[{"workload": "w", "total_time_sec": 2.0, "peak_rss_mb": 9.0}],
        node_details=[
            {
                "node_id": "n1",
                "identity": "rank(close)",
                "helper_bytes_estimate": 100,
                "bytes_estimate": 100,
                "compute_time_ms": 5.0,
                "consumer_count": 3,
                "node_store_read_count": 3,
                "dependency_chain": ["src", "n1"],
                "materialization_kind": "shared_intermediate",
            },
            {
                "node_id": "n2",
                "identity": "rank(close)",
                "helper_bytes_estimate": 100,
                "bytes_estimate": 100,
                "compute_time_ms": 4.0,
                "consumer_count": 2,
                "node_store_read_count": 2,
                "dependency_chain": ["src", "n1", "n2"],
                "materialization_kind": "shared_intermediate",
            },
        ],
    )

    assert report.structural_observability_complete
    assert report.repeated_subgraphs[0]["occurrences"] == 2
    assert report.deep_chains
    assert report.wide_fanout_nodes
    assert report.heavy_paths
    assert report.proposal_priority[0] == "m4_cse_expand_repeated_subgraphs"


def test_m4_first_executable_is_expanded_cse_candidate():
    candidates = generate_m4_executable_candidates([])

    assert [item.id for item in candidates] == ["m4_cse_expand_repeated_subgraphs"]
    assert candidates[0].is_executable
    assert candidates[0].params["planner_cse_mode"] == "expanded_repeated_family"


def test_m4_second_executable_is_unary_chain_fusion_after_cse():
    history = [
        OptimizationHistoryEntry(
            id="m4_cse_expand_repeated_subgraphs",
            score=1.0,
            accepted=True,
            memory_reduction=0.0,
            frame_width_reduction=0.0,
            time_increase=-5.0,
            phase="m4_bridge",
            candidate_class="cse_expansion",
            decision="ACCEPT",
        )
    ]

    candidates = generate_m4_executable_candidates(history)

    assert [item.id for item in candidates] == ["m4_fuse_deep_operator_chains"]
    assert candidates[0].is_executable
    assert candidates[0].params["fusion_mode"] == "unary_chain_fusion"
    assert candidates[0].params["baseline_fusion_mode"] == "off"
