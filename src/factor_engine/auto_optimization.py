from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


CandidatePhase = Literal["m3_v1", "m4_bridge"]
CandidateStatus = Literal["proposal", "executable"]
CandidateKind = Literal[
    "attach_strategy",
    "materialization_threshold",
    "projection_strategy",
    "hybrid",
    "cse_expansion",
    "execution_route_rewrite",
    "node_fusion",
    "batching_segmentation",
    "materialization_elimination",
]


@dataclass(frozen=True)
class OptimizationCandidate:
    id: str
    phase: CandidatePhase
    kind: CandidateKind
    params: dict[str, object]
    rationale: str
    candidate_status: CandidateStatus = "proposal"
    engine_supported: bool = False

    @property
    def is_executable(self) -> bool:
        return self.candidate_status == "executable" and self.engine_supported

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class OptimizationHistoryEntry:
    id: str
    score: float
    accepted: bool
    memory_reduction: float
    frame_width_reduction: float
    time_increase: float
    candidate_status: CandidateStatus = "executable"
    recomputation_expansion_delta: float = 0.0
    phase: CandidatePhase = "m3_v1"
    candidate_class: str = ""
    selected_family: str = ""
    matched_groups: int = 0
    reused_groups: int = 0
    estimated_helper_bytes_saved: int = 0
    correctness_pass: bool = True
    audit_explainable: bool = True
    isolation_pass: bool = True
    decision: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CandidateEvaluation:
    candidate: OptimizationCandidate
    score: float
    accepted: bool
    memory_reduction: float
    frame_width_reduction: float
    time_increase: float
    metrics: dict[str, object]
    recomputation_expansion_delta: float = 0.0
    correctness_pass: bool = True
    audit_explainable: bool = True
    isolation_pass: bool = True
    selected_family: str = ""
    matched_groups: int = 0
    reused_groups: int = 0
    estimated_helper_bytes_saved: int = 0

    def to_history_entry(self) -> OptimizationHistoryEntry:
        return OptimizationHistoryEntry(
            id=self.candidate.id,
            score=self.score,
            accepted=self.accepted,
            memory_reduction=self.memory_reduction,
            frame_width_reduction=self.frame_width_reduction,
            time_increase=self.time_increase,
            candidate_status=self.candidate.candidate_status,
            recomputation_expansion_delta=self.recomputation_expansion_delta,
            phase=self.candidate.phase,
            candidate_class=self.candidate.kind,
            selected_family=self.selected_family,
            matched_groups=self.matched_groups,
            reused_groups=self.reused_groups,
            estimated_helper_bytes_saved=self.estimated_helper_bytes_saved,
            correctness_pass=self.correctness_pass,
            audit_explainable=self.audit_explainable,
            isolation_pass=self.isolation_pass,
            decision="ACCEPT" if self.accepted else "REJECT",
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "candidate": self.candidate.to_dict(),
            "score": self.score,
            "accepted": self.accepted,
            "memory_reduction": self.memory_reduction,
            "frame_width_reduction": self.frame_width_reduction,
            "time_increase": self.time_increase,
            "recomputation_expansion_delta": self.recomputation_expansion_delta,
            "correctness_pass": self.correctness_pass,
            "audit_explainable": self.audit_explainable,
            "isolation_pass": self.isolation_pass,
            "selected_family": self.selected_family,
            "matched_groups": self.matched_groups,
            "reused_groups": self.reused_groups,
            "estimated_helper_bytes_saved": self.estimated_helper_bytes_saved,
            "metrics": self.metrics,
        }


@dataclass(frozen=True)
class BottleneckReport:
    high_memory_nodes: tuple[dict[str, object], ...]
    repeated_patterns: tuple[dict[str, object], ...]
    deep_chains: tuple[dict[str, object], ...]
    wide_nodes: tuple[dict[str, object], ...]
    compute_hotspots: tuple[dict[str, object], ...]

    @property
    def bottleneck_detected(self) -> bool:
        return any(
            (
                self.high_memory_nodes,
                self.repeated_patterns,
                self.deep_chains,
                self.wide_nodes,
                self.compute_hotspots,
            )
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class StructuralBottleneckReport:
    repeated_subgraphs: tuple[dict[str, object], ...]
    deep_chains: tuple[dict[str, object], ...]
    wide_fanout_nodes: tuple[dict[str, object], ...]
    heavy_paths: tuple[dict[str, object], ...]
    dominant_bottleneck_class: str
    proposal_priority: tuple[str, ...]

    @property
    def structural_observability_complete(self) -> bool:
        return any(
            (
                self.repeated_subgraphs,
                self.deep_chains,
                self.wide_fanout_nodes,
                self.heavy_paths,
            )
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def optimization_score(
    *,
    memory_reduction: float,
    frame_width_reduction: float,
    time_increase: float,
    memory_weight: float = 0.5,
    frame_width_weight: float = 0.3,
    time_weight: float = 0.2,
) -> float:
    return (
        memory_weight * memory_reduction
        + frame_width_weight * frame_width_reduction
        - time_weight * time_increase
    )


def candidate_seen_before(
    candidate: OptimizationCandidate,
    history: list[OptimizationHistoryEntry],
) -> bool:
    seen_ids = {entry.id for entry in history}
    return candidate.id in seen_ids


def m3_candidate_catalog() -> list[OptimizationCandidate]:
    return [
        OptimizationCandidate(
            id="m3_delayed_output_attach_finalize_select",
            phase="m3_v1",
            kind="attach_strategy",
            params={
                "baseline_output_attach_mode": "materialize",
                "output_attach_mode": "finalize_select",
            },
            rationale=(
                "Executable candidate: keep output expressions in a registry-like "
                "finalize select path instead of attaching output columns to the "
                "ordered working frame."
            ),
            candidate_status="executable",
            engine_supported=True,
        ),
        OptimizationCandidate(
            id="m3_projection_dependency_driven",
            phase="m3_v1",
            kind="projection_strategy",
            params={
                "baseline_frame_projection_mode": "off",
                "frame_projection_mode": "dependency_driven",
            },
            rationale=(
                "Executable candidate: before output finalization, project the "
                "ordered working frame to columns required by final output "
                "expressions."
            ),
            candidate_status="executable",
            engine_supported=True,
        ),
        OptimizationCandidate(
            id="m3_materialization_reuse_ge_3",
            phase="m3_v1",
            kind="materialization_threshold",
            params={
                "baseline_materialization_threshold_mode": "reuse_ge_2",
                "materialization_threshold_mode": "reuse_ge_3_guarded",
                "recomputation_guardrail_max_expansion": 0,
            },
            rationale=(
                "Executable candidate: raise materialization threshold only when "
                "the recomputation guardrail predicts no extra repeated heavy "
                "compute."
            ),
            candidate_status="executable",
            engine_supported=True,
        ),
        OptimizationCandidate(
            id="m3_attach_last_use",
            phase="m3_v1",
            kind="attach_strategy",
            params={
                "baseline_output_attach_mode": "materialize",
                "output_attach_mode": "last_use_select",
                "attach_safe_step_model": "final_output_last_use",
            },
            rationale=(
                "Executable candidate: attach outputs through the last-use safe "
                "selection path. In the current ordered batch model, final output "
                "last use is the restore/final-assemble boundary, so this remains "
                "a conservative A/B knob rather than a route change."
            ),
            candidate_status="executable",
            engine_supported=True,
        ),
    ]


def generate_m3_executable_candidates(
    history: list[OptimizationHistoryEntry],
    *,
    max_candidates_per_round: int = 1,
) -> list[OptimizationCandidate]:
    return [
        candidate
        for candidate in m3_candidate_catalog()
        if candidate.is_executable and not candidate_seen_before(candidate, history)
    ][:max_candidates_per_round]


def generate_m3_proposal_candidates(
    history: list[OptimizationHistoryEntry] | None = None,
    *,
    max_candidates_per_round: int = 3,
) -> list[OptimizationCandidate]:
    # Proposals are queue entries, not scored experiment records. History is only
    # used defensively if a proposal id was later promoted and evaluated.
    seen_history = history or []
    return [
        candidate
        for candidate in m3_candidate_catalog()
        if candidate.candidate_status == "proposal"
        and not candidate_seen_before(candidate, seen_history)
    ][:max_candidates_per_round]


def generate_m3_candidates(
    history: list[OptimizationHistoryEntry],
    *,
    max_candidates_per_round: int = 1,
) -> list[OptimizationCandidate]:
    """Return executable M3 candidates only.

    Proposal candidates are intentionally exposed through
    ``generate_m3_proposal_candidates`` so unimplemented ideas cannot be scored as
    failed experiments.
    """

    return generate_m3_executable_candidates(
        history,
        max_candidates_per_round=max_candidates_per_round,
    )


def select_best_candidate(
    evaluations: list[CandidateEvaluation],
    *,
    round_index: int,
) -> CandidateEvaluation | None:
    if not evaluations:
        return None
    ranked = sorted(evaluations, key=lambda item: item.score, reverse=True)
    # Every third round can explore a non-best candidate if it is still positive.
    if round_index > 0 and round_index % 3 == 0 and len(ranked) > 1:
        exploratory = next((item for item in ranked[1:] if item.score > 0), None)
        if exploratory is not None:
            return exploratory
    return ranked[0]


def candidate_space_exhausted(
    history: list[OptimizationHistoryEntry],
    *,
    max_candidates_per_round: int = 1,
) -> bool:
    return not generate_m3_executable_candidates(
        history,
        max_candidates_per_round=max_candidates_per_round,
    )


def stagnation_detected(
    history: list[OptimizationHistoryEntry],
    *,
    memory_improvement: float,
    frame_improvement: float,
    candidate_exhausted: bool,
) -> bool:
    if len(history) < 3:
        return False
    last_three = history[-3:]
    return (
        all(entry.score <= 0 for entry in last_three)
        and memory_improvement < 2
        and frame_improvement < 2
        and candidate_exhausted
    )


def _top_items(
    items: list[dict[str, object]],
    *,
    key: str,
    limit: int,
) -> tuple[dict[str, object], ...]:
    return tuple(
        sorted(
            items,
            key=lambda item: float(item.get(key, 0) or 0),
            reverse=True,
        )[:limit]
    )


def _as_int(value: object) -> int:
    if value is None:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _as_float(value: object) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _node_pressure_score(detail: dict[str, Any]) -> float:
    memory_weight = _as_int(detail.get("bytes_estimate")) + _as_int(
        detail.get("helper_bytes_estimate")
    )
    time_weight = _as_float(detail.get("compute_time_ms")) + _as_float(
        detail.get("native_compute_time_ms")
    )
    read_weight = max(
        _as_int(detail.get("node_store_read_count")),
        _as_int(detail.get("consumer_count")),
        _as_int(detail.get("reuse_consumer_count")),
    )
    return memory_weight / 1_000_000 + time_weight + read_weight


def build_structural_bottleneck_report(
    *,
    run_summaries: list[dict[str, Any]],
    node_details: list[dict[str, Any]],
    top_k: int = 5,
) -> StructuralBottleneckReport:
    repeated_by_signature: dict[str, dict[str, object]] = {}
    for detail in node_details:
        signature = str(detail.get("identity", ""))
        if not signature:
            continue
        item = repeated_by_signature.setdefault(
            signature,
            {
                "signature": signature,
                "occurrences": 0,
                "nodes": set(),
                "estimated_helper_bytes": 0,
                "estimated_compute_weight": 0.0,
            },
        )
        item["occurrences"] = _as_int(item["occurrences"]) + 1
        nodes = item["nodes"]
        if isinstance(nodes, set):
            nodes.add(str(detail.get("node_id", "")))
        item["estimated_helper_bytes"] = _as_int(
            item["estimated_helper_bytes"]
        ) + _as_int(detail.get("helper_bytes_estimate"))
        item["estimated_compute_weight"] = _as_float(
            item["estimated_compute_weight"]
        ) + _as_float(detail.get("compute_time_ms"))
    repeated_subgraphs = []
    for item in repeated_by_signature.values():
        if _as_int(item["occurrences"]) <= 1:
            continue
        nodes = item["nodes"]
        repeated_subgraphs.append(
            {
                "signature": item["signature"],
                "occurrences": item["occurrences"],
                "nodes": sorted(nodes) if isinstance(nodes, set) else [],
                "estimated_helper_bytes": item["estimated_helper_bytes"],
                "estimated_compute_weight": item["estimated_compute_weight"],
            }
        )
    repeated_subgraphs = list(
        _top_items(
            repeated_subgraphs,
            key="estimated_helper_bytes",
            limit=top_k,
        )
    )

    detail_by_node_id = {
        str(detail.get("node_id", "")): detail
        for detail in node_details
        if str(detail.get("node_id", ""))
    }
    chains: dict[tuple[str, ...], dict[str, object]] = {}
    for detail in node_details:
        raw_chain = detail.get("dependency_chain", ())
        if not isinstance(raw_chain, (list, tuple)) or len(raw_chain) < 2:
            continue
        chain = tuple(str(item) for item in raw_chain)
        item = chains.setdefault(
            chain,
            {
                "chain_id": "->".join(chain),
                "depth": len(chain),
                "nodes": list(chain),
                "materialized_hops": 0,
                "transient_hops": 0,
                "estimated_chain_pressure": 0,
            },
        )
        materialized_hops = sum(
            1
            for node_id in chain
            if str(detail_by_node_id.get(node_id, {}).get("materialization_kind", ""))
            in {"shared_intermediate", "final"}
        )
        chain_pressure = sum(
            _as_int(detail_by_node_id.get(node_id, {}).get("helper_bytes_estimate"))
            + _as_int(detail_by_node_id.get(node_id, {}).get("bytes_estimate"))
            for node_id in chain
        )
        item["materialized_hops"] = max(
            _as_int(item["materialized_hops"]),
            materialized_hops,
        )
        item["transient_hops"] = max(0, len(chain) - _as_int(item["materialized_hops"]))
        item["estimated_chain_pressure"] = max(
            _as_int(item["estimated_chain_pressure"]),
            chain_pressure,
        )
    deep_chains = list(
        _top_items(
            list(chains.values()),
            key="estimated_chain_pressure",
            limit=top_k,
        )
    )

    wide_by_identity: dict[str, dict[str, object]] = {}
    for detail in node_details:
        fanout_degree = max(
            _as_int(detail.get("consumer_count")),
            _as_int(detail.get("node_store_read_count")),
        )
        if fanout_degree < 2:
            continue
        signature = str(detail.get("identity", detail.get("node_id", "")))
        item = wide_by_identity.setdefault(
            signature,
            {
                "node_id": detail.get("node_id", ""),
                "fanout_degree": 0,
                "child_nodes": set(),
                "estimated_fanout_pressure": 0,
                "identity": signature,
                "occurrences": 0,
            },
        )
        item["occurrences"] = _as_int(item["occurrences"]) + 1
        item["fanout_degree"] = max(_as_int(item["fanout_degree"]), fanout_degree)
        children = item["child_nodes"]
        if isinstance(children, set):
            for child in detail.get("child_helper_columns", ()) or ():
                children.add(str(child))
        item["estimated_fanout_pressure"] = _as_int(
            item["estimated_fanout_pressure"]
        ) + fanout_degree * (
            _as_int(detail.get("helper_bytes_estimate"))
            + _as_int(detail.get("bytes_estimate"))
        )
    wide_fanout_nodes = []
    for item in wide_by_identity.values():
        children = item["child_nodes"]
        wide_fanout_nodes.append(
            {
                **item,
                "child_nodes": sorted(children) if isinstance(children, set) else [],
            }
        )
    wide_fanout_nodes = list(
        _top_items(
            wide_fanout_nodes,
            key="estimated_fanout_pressure",
            limit=top_k,
        )
    )

    heavy_paths = list(
        _top_items(
            [
                {
                    "path_id": "->".join(
                        str(item)
                        for item in detail.get("dependency_chain", ())
                        if str(item)
                    )
                    or str(detail.get("node_id", "")),
                    "nodes": list(detail.get("dependency_chain", ()))
                    or [detail.get("node_id", "")],
                    "estimated_memory_weight": _as_int(detail.get("bytes_estimate"))
                    + _as_int(detail.get("helper_bytes_estimate")),
                    "estimated_time_weight": _as_float(detail.get("compute_time_ms"))
                    + _as_float(detail.get("native_compute_time_ms")),
                    "combined_pressure_score": _node_pressure_score(detail),
                    "identity": detail.get("identity", ""),
                }
                for detail in node_details
                if _node_pressure_score(detail) > 0
            ],
            key="combined_pressure_score",
            limit=top_k,
        )
    )
    if not heavy_paths:
        heavy_paths = list(
            _top_items(
                [
                    {
                        "path_id": str(
                            summary.get("workload", summary.get("benchmark_name", ""))
                        ),
                        "nodes": [],
                        "estimated_memory_weight": _as_float(
                            summary.get("peak_rss_mb", 0)
                        ),
                        "estimated_time_weight": _as_float(
                            summary.get("total_time_sec", 0)
                        ),
                        "combined_pressure_score": _as_float(
                            summary.get("total_time_sec", 0)
                        )
                        + _as_float(summary.get("peak_rss_mb", 0)),
                    }
                    for summary in run_summaries
                ],
                key="combined_pressure_score",
                limit=top_k,
            )
        )

    pressure_by_class = {
        "repeated_subgraphs": sum(
            _as_float(item.get("estimated_helper_bytes"))
            + _as_float(item.get("estimated_compute_weight"))
            for item in repeated_subgraphs
        ),
        "deep_chains": sum(
            _as_float(item.get("estimated_chain_pressure")) for item in deep_chains
        ),
        "wide_fanout": sum(
            _as_float(item.get("estimated_fanout_pressure"))
            for item in wide_fanout_nodes
        ),
        "heavy_paths": sum(
            _as_float(item.get("combined_pressure_score")) for item in heavy_paths
        ),
    }
    dominant = max(pressure_by_class, key=pressure_by_class.get)
    if pressure_by_class[dominant] <= 0:
        dominant = "none"
    default_priority = [
        "m4_cse_expand_repeated_subgraphs",
        "m4_fuse_deep_operator_chains",
        "m4_eliminate_materialized_intermediates",
        "m4_batch_wide_fanout_nodes",
        "m4_rewrite_heavy_execution_path",
    ]
    priority = default_priority
    return StructuralBottleneckReport(
        repeated_subgraphs=tuple(repeated_subgraphs),
        deep_chains=tuple(deep_chains),
        wide_fanout_nodes=tuple(wide_fanout_nodes),
        heavy_paths=tuple(heavy_paths),
        dominant_bottleneck_class=dominant,
        proposal_priority=tuple(priority),
    )


def detect_bottlenecks(
    *,
    run_summaries: list[dict[str, Any]],
    node_details: list[dict[str, Any]],
    top_k: int = 5,
) -> BottleneckReport:
    high_memory_nodes = _top_items(
        [
            {
                "node_id": detail.get("node_id", ""),
                "identity": detail.get("identity", ""),
                "bytes_estimate": detail.get("bytes_estimate", 0),
                "helper_bytes_estimate": detail.get("helper_bytes_estimate", 0),
                "materialization_kind": detail.get("materialization_kind", ""),
            }
            for detail in node_details
            if int(detail.get("bytes_estimate", 0) or 0) > 0
            or int(detail.get("helper_bytes_estimate", 0) or 0) > 0
        ],
        key="bytes_estimate",
        limit=top_k,
    )
    repeated_patterns = _top_items(
        [
            {
                "node_id": detail.get("node_id", ""),
                "identity": detail.get("identity", ""),
                "consumer_count": detail.get("consumer_count", 0),
                "reuse_consumer_count": detail.get("reuse_consumer_count", 0),
                "node_store_read_count": detail.get("node_store_read_count", 0),
            }
            for detail in node_details
            if int(detail.get("node_store_read_count", 0) or 0) > 1
            or int(detail.get("reuse_consumer_count", 0) or 0) > 1
        ],
        key="node_store_read_count",
        limit=top_k,
    )
    deep_chains = _top_items(
        [
            {
                "node_id": detail.get("node_id", ""),
                "identity": detail.get("identity", ""),
                "node_depth": detail.get("node_depth", 0),
                "helper_depth": detail.get("helper_depth", 0),
            }
            for detail in node_details
            if int(detail.get("node_depth", 0) or 0) >= 2
            or int(detail.get("helper_depth", 0) or 0) >= 2
        ],
        key="node_depth",
        limit=top_k,
    )
    wide_nodes = _top_items(
        [
            {
                "node_id": detail.get("node_id", ""),
                "identity": detail.get("identity", ""),
                "consumer_count": detail.get("consumer_count", 0),
                "reuse_consumer_count": detail.get("reuse_consumer_count", 0),
            }
            for detail in node_details
            if int(detail.get("consumer_count", 0) or 0) >= 3
            or int(detail.get("reuse_consumer_count", 0) or 0) >= 3
        ],
        key="consumer_count",
        limit=top_k,
    )
    compute_hotspots = _top_items(
        [
            {
                "node_id": detail.get("node_id", ""),
                "identity": detail.get("identity", ""),
                "compute_time_ms": detail.get("compute_time_ms", 0.0),
                "compiled_output_eval_time_ms": detail.get(
                    "compiled_output_eval_time_ms",
                    0.0,
                ),
            }
            for detail in node_details
            if float(detail.get("compute_time_ms", 0.0) or 0.0) > 0
        ],
        key="compute_time_ms",
        limit=top_k,
    )
    if not compute_hotspots:
        compute_hotspots = _top_items(
            [
                {
                    "workload": summary.get("workload", summary.get("benchmark_name", "")),
                    "total_time_sec": summary.get("total_time_sec", 0.0),
                    "compiled_output_eval_time_ms": summary.get(
                        "compiled_output_eval_time_ms",
                        0.0,
                    ),
                    "node_store_compute_time_ms": summary.get(
                        "node_store_compute_time_ms",
                        0.0,
                    ),
                }
                for summary in run_summaries
            ],
            key="total_time_sec",
            limit=top_k,
        )
    return BottleneckReport(
        high_memory_nodes=high_memory_nodes,
        repeated_patterns=repeated_patterns,
        deep_chains=deep_chains,
        wide_nodes=wide_nodes,
        compute_hotspots=compute_hotspots,
    )


def generate_m4_candidates(
    report: BottleneckReport,
    *,
    max_candidates: int = 5,
) -> list[OptimizationCandidate]:
    candidates: dict[str, OptimizationCandidate] = {}
    if report.repeated_patterns:
        candidates["m4_cse_expand_repeated_subgraphs"] = (
            OptimizationCandidate(
                id="m4_cse_expand_repeated_subgraphs",
                phase="m4_bridge",
                kind="cse_expansion",
                params={"target": "repeated_subgraphs"},
                rationale="Repeated node-store read patterns remain after M3 scoring.",
                candidate_status="proposal",
            )
        )
    if report.compute_hotspots:
        candidates["m4_rewrite_heavy_execution_path"] = (
            OptimizationCandidate(
                id="m4_rewrite_heavy_execution_path",
                phase="m4_bridge",
                kind="execution_route_rewrite",
                params={"target": "compute_hotspots"},
                rationale="Compute hotspots suggest route-level path normalization or rewrite work.",
                candidate_status="proposal",
            )
        )
    if report.deep_chains:
        candidates["m4_fuse_deep_operator_chains"] = (
            OptimizationCandidate(
                id="m4_fuse_deep_operator_chains",
                phase="m4_bridge",
                kind="node_fusion",
                params={"target": "deep_chains"},
                rationale="Deep chains suggest fusion may remove intermediate nodes entirely.",
                candidate_status="proposal",
            )
        )
    if report.wide_nodes:
        candidates["m4_batch_wide_fanout_nodes"] = (
            OptimizationCandidate(
                id="m4_batch_wide_fanout_nodes",
                phase="m4_bridge",
                kind="batching_segmentation",
                params={"target": "wide_fanout_nodes"},
                rationale="Wide fan-out nodes suggest batching or segmentation may reduce repeated access.",
                candidate_status="proposal",
            )
        )
    if report.high_memory_nodes:
        candidates["m4_eliminate_materialized_intermediates"] = (
            OptimizationCandidate(
                id="m4_eliminate_materialized_intermediates",
                phase="m4_bridge",
                kind="materialization_elimination",
                params={"target": "high_memory_nodes"},
                rationale="High-memory helper nodes suggest structural materialization elimination.",
                candidate_status="proposal",
            )
        )
    priority = [
        "m4_cse_expand_repeated_subgraphs",
        "m4_fuse_deep_operator_chains",
        "m4_eliminate_materialized_intermediates",
        "m4_batch_wide_fanout_nodes",
        "m4_rewrite_heavy_execution_path",
    ]
    return [candidates[item] for item in priority if item in candidates][:max_candidates]


def generate_m4_executable_candidates(
    history: list[OptimizationHistoryEntry],
    *,
    max_candidates_per_round: int = 1,
) -> list[OptimizationCandidate]:
    candidates = [
        OptimizationCandidate(
            id="m4_cse_expand_repeated_subgraphs",
            phase="m4_bridge",
            kind="cse_expansion",
            params={
                "baseline_planner_cse_mode": "baseline",
                "planner_cse_mode": "expanded_repeated_family",
                "selected_family": "rolling_neutral_add_input",
            },
            rationale=(
                "Executable M4.2 candidate: expand CSE only for the selected "
                "rolling neutral-add input family, where ts_rank/ts_mean(var + 0, "
                "window) can share the same value identity as ts_rank/ts_mean(var, "
                "window)."
            ),
            candidate_status="executable",
            engine_supported=True,
        ),
        OptimizationCandidate(
            id="m4_fuse_deep_operator_chains",
            phase="m4_bridge",
            kind="node_fusion",
            params={
                "baseline_planner_cse_mode": "expanded_repeated_family",
                "planner_cse_mode": "expanded_repeated_family",
                "baseline_fusion_mode": "off",
                "fusion_mode": "unary_chain_fusion",
                "selected_family": "rolling_unary_chain_ts_mean_into_ts_rank",
            },
            rationale=(
                "Executable M4.3 candidate: fuse only the pure repeated "
                "ts_rank(ts_mean(variable, w1), w2) unary rolling chain by "
                "keeping the inner ts_mean transient and materializing the outer "
                "ts_rank helper."
            ),
            candidate_status="executable",
            engine_supported=True,
        ),
    ]
    return [
        candidate
        for candidate in candidates
        if not candidate_seen_before(candidate, history)
    ][:max_candidates_per_round]
