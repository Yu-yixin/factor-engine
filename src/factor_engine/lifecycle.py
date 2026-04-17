from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

LifecycleMode = Literal["off", "first_wave"]
HelperLifecycleMode = Literal["off", "first_wave", "second_wave_nested"]
OutputAttachMode = Literal["materialize", "finalize_select", "last_use_select"]
FrameProjectionMode = Literal["off", "dependency_driven"]
MaterializationThresholdMode = Literal["reuse_ge_2", "reuse_ge_3_guarded"]
PlannerCseMode = Literal["baseline", "expanded_repeated_family"]
FusionMode = Literal["off", "unary_chain_fusion"]
NativeHeavyLifecycleEligibility = Literal["forbidden", "observable_only", "candidate_future"]

L2_FIRST_WAVE_BYTES_THRESHOLD = 1
_VALID_LIFECYCLE_MODES: set[str] = {"off", "first_wave"}
_VALID_HELPER_LIFECYCLE_MODES: set[str] = {"off", "first_wave", "second_wave_nested"}
_VALID_OUTPUT_ATTACH_MODES: set[str] = {
    "materialize",
    "finalize_select",
    "last_use_select",
}
_VALID_FRAME_PROJECTION_MODES: set[str] = {"off", "dependency_driven"}
_VALID_MATERIALIZATION_THRESHOLD_MODES: set[str] = {"reuse_ge_2", "reuse_ge_3_guarded"}
_VALID_PLANNER_CSE_MODES: set[str] = {"baseline", "expanded_repeated_family"}
_VALID_FUSION_MODES: set[str] = {"off", "unary_chain_fusion"}
L3B_HELPER_FIRST_WAVE_WORKLOADS: frozenset[str] = frozenset(
    {"repeated_heavy", "multi_shared_nodes", "partial_reuse"}
)


@dataclass(frozen=True)
class FirstWaveCandidateInput:
    materialization_eligibility: str
    drop_candidate: bool
    drop_blocker_reason: str
    structural_release_lag_steps: int
    node_lifecycle_class: str
    bytes_estimate: int


@dataclass(frozen=True)
class NativeHeavyLifecycleInput:
    is_native_heavy: bool
    materialized: bool
    rewrite_applied: bool
    logical_consumer_count: int
    effective_use_count: int
    consumer_semantics_stable: bool = False


@dataclass(frozen=True)
class HelperFirstWaveCandidateInput:
    helper_lifecycle_state: str
    helper_drop_blocker_reason: str
    helper_structural_lag_steps: int
    helper_bytes_estimate: int
    materialization_kind: str
    materialization_eligibility: str
    node_lifecycle_class: str
    workload_name: str
    nested_dependency_present: bool


@dataclass(frozen=True)
class HelperSecondWaveNestedCandidateInput:
    helper_lifecycle_state: str
    helper_drop_blocker_reason: str
    helper_structural_lag_steps: int
    helper_bytes_estimate: int
    materialization_kind: str
    materialization_eligibility: str
    node_lifecycle_class: str
    parent_helper_column_name: str | None
    child_helper_columns: tuple[str, ...]
    parent_child_count: int
    materialized_helper_count: int
    nested_output_pinned: bool
    helper_structural_dependency_end_step: int | None
    helper_drop_safe_step: int | None
    node_store_read_count: int
    reuse_consumer_count: int


def normalize_lifecycle_mode(
    *,
    lifecycle: bool = False,
    lifecycle_mode: str | None = None,
) -> LifecycleMode:
    if lifecycle_mode is None:
        return "first_wave" if lifecycle else "off"
    if lifecycle_mode not in _VALID_LIFECYCLE_MODES:
        allowed = ", ".join(sorted(_VALID_LIFECYCLE_MODES))
        raise ValueError(f"Unsupported lifecycle_mode: {lifecycle_mode!r}. Expected one of: {allowed}")
    if lifecycle and lifecycle_mode == "off":
        raise ValueError("Conflicting lifecycle settings: lifecycle=True with lifecycle_mode='off'")
    return lifecycle_mode  # type: ignore[return-value]


def normalize_helper_lifecycle_mode(
    *,
    helper_lifecycle_mode: str | None = None,
) -> HelperLifecycleMode:
    if helper_lifecycle_mode is None:
        return "off"
    if helper_lifecycle_mode not in _VALID_HELPER_LIFECYCLE_MODES:
        allowed = ", ".join(sorted(_VALID_HELPER_LIFECYCLE_MODES))
        raise ValueError(
            f"Unsupported helper_lifecycle_mode: {helper_lifecycle_mode!r}. "
            f"Expected one of: {allowed}"
        )
    return helper_lifecycle_mode  # type: ignore[return-value]


def normalize_output_attach_mode(
    *,
    output_attach_mode: str | None = None,
) -> OutputAttachMode:
    if output_attach_mode is None:
        return "materialize"
    if output_attach_mode not in _VALID_OUTPUT_ATTACH_MODES:
        allowed = ", ".join(sorted(_VALID_OUTPUT_ATTACH_MODES))
        raise ValueError(
            f"Unsupported output_attach_mode: {output_attach_mode!r}. "
            f"Expected one of: {allowed}"
        )
    return output_attach_mode  # type: ignore[return-value]


def normalize_frame_projection_mode(
    *,
    frame_projection_mode: str | None = None,
) -> FrameProjectionMode:
    if frame_projection_mode is None:
        return "off"
    if frame_projection_mode not in _VALID_FRAME_PROJECTION_MODES:
        allowed = ", ".join(sorted(_VALID_FRAME_PROJECTION_MODES))
        raise ValueError(
            f"Unsupported frame_projection_mode: {frame_projection_mode!r}. "
            f"Expected one of: {allowed}"
        )
    return frame_projection_mode  # type: ignore[return-value]


def normalize_materialization_threshold_mode(
    *,
    materialization_threshold_mode: str | None = None,
) -> MaterializationThresholdMode:
    if materialization_threshold_mode is None:
        return "reuse_ge_2"
    if materialization_threshold_mode not in _VALID_MATERIALIZATION_THRESHOLD_MODES:
        allowed = ", ".join(sorted(_VALID_MATERIALIZATION_THRESHOLD_MODES))
        raise ValueError(
            f"Unsupported materialization_threshold_mode: {materialization_threshold_mode!r}. "
            f"Expected one of: {allowed}"
        )
    return materialization_threshold_mode  # type: ignore[return-value]


def normalize_planner_cse_mode(
    *,
    planner_cse_mode: str | None = None,
) -> PlannerCseMode:
    if planner_cse_mode is None:
        return "baseline"
    if planner_cse_mode not in _VALID_PLANNER_CSE_MODES:
        allowed = ", ".join(sorted(_VALID_PLANNER_CSE_MODES))
        raise ValueError(
            f"Unsupported planner_cse_mode: {planner_cse_mode!r}. "
            f"Expected one of: {allowed}"
        )
    return planner_cse_mode  # type: ignore[return-value]


def normalize_fusion_mode(
    *,
    fusion_mode: str | None = None,
) -> FusionMode:
    if fusion_mode is None:
        return "off"
    if fusion_mode not in _VALID_FUSION_MODES:
        allowed = ", ".join(sorted(_VALID_FUSION_MODES))
        raise ValueError(
            f"Unsupported fusion_mode: {fusion_mode!r}. Expected one of: {allowed}"
        )
    return fusion_mode  # type: ignore[return-value]


def is_lifecycle_active(mode: LifecycleMode) -> bool:
    return mode == "first_wave"


def is_helper_lifecycle_active(mode: HelperLifecycleMode) -> bool:
    return mode in {"first_wave", "second_wave_nested"}


def is_first_wave_candidate(candidate: FirstWaveCandidateInput) -> bool:
    return (
        candidate.materialization_eligibility == "materialize_for_both"
        and candidate.drop_candidate
        and candidate.drop_blocker_reason == ""
        and candidate.structural_release_lag_steps > 0
        and candidate.node_lifecycle_class != "native_heavy"
        and candidate.bytes_estimate >= L2_FIRST_WAVE_BYTES_THRESHOLD
    )


def is_first_wave_helper_candidate(candidate: HelperFirstWaveCandidateInput) -> bool:
    return (
        candidate.workload_name in L3B_HELPER_FIRST_WAVE_WORKLOADS
        and candidate.helper_lifecycle_state == "logically_dead"
        and candidate.helper_drop_blocker_reason == ""
        and candidate.helper_structural_lag_steps > 0
        and candidate.helper_bytes_estimate > 0
        and candidate.materialization_kind == "shared_intermediate"
        and candidate.materialization_eligibility == "materialize_for_both"
        and candidate.node_lifecycle_class != "native_heavy"
        and not candidate.nested_dependency_present
    )


def second_wave_nested_miss_reason(
    candidate: HelperSecondWaveNestedCandidateInput,
) -> str:
    has_parent = candidate.parent_helper_column_name is not None
    child_count = len(candidate.child_helper_columns)
    is_nested = has_parent or child_count > 0
    if candidate.helper_drop_blocker_reason:
        return "has_blocker"
    if candidate.node_lifecycle_class == "native_heavy":
        return "native_pinned"
    if not is_nested:
        return "not_nested"
    if candidate.nested_output_pinned:
        return "output_pinned"
    if candidate.materialization_kind != "shared_intermediate":
        return "unsupported_shape"
    if candidate.materialization_eligibility != "materialize_for_both":
        return "unsupported_shape"
    if candidate.helper_lifecycle_state != "logically_dead":
        return "live_consumer_detected"
    if candidate.helper_structural_lag_steps <= 0 or candidate.helper_bytes_estimate <= 0:
        return "unsupported_shape"
    if child_count > 1:
        return "unsupported_shape"
    if candidate.parent_child_count > 1:
        return "unsupported_shape"
    if candidate.materialized_helper_count != 2:
        return "unsupported_shape"
    # Pure-chain inner helpers are consumed only by their parent helper. If a
    # parent-backed helper has more than one logical consumer, it is a
    # shared-inner or mixed-use shape and must wait for a later wave.
    if has_parent and candidate.reuse_consumer_count != 1:
        return "non_helper_consumer"
    if (
        candidate.helper_structural_dependency_end_step is None
        or candidate.helper_drop_safe_step is None
    ):
        return "safe_step_mismatch"
    if candidate.helper_drop_safe_step < candidate.helper_structural_dependency_end_step:
        return "children_not_ended"
    return ""


def is_second_wave_nested_candidate(
    candidate: HelperSecondWaveNestedCandidateInput,
) -> bool:
    return second_wave_nested_miss_reason(candidate) == ""


def collect_helper_drop_candidate_kind(
    *,
    mode: HelperLifecycleMode,
    first_wave_candidate: HelperFirstWaveCandidateInput,
    second_wave_candidate: HelperSecondWaveNestedCandidateInput,
) -> tuple[bool, str, str]:
    if mode == "off":
        return False, "", "mode_disabled"
    if is_first_wave_helper_candidate(first_wave_candidate):
        return True, "first_wave", ""
    if mode == "second_wave_nested":
        miss_reason = second_wave_nested_miss_reason(second_wave_candidate)
        if miss_reason == "":
            return True, "second_wave_nested", ""
        return False, "", miss_reason
    return False, "", "not_first_wave_helper_candidate"


def lifecycle_effective(
    *,
    dropped_node_count: int,
    drop_miss_count: int,
    peak_live_bytes_est_before_drop: int,
    peak_live_bytes_est_after_drop: int,
    drop_delay_steps_max: int,
) -> bool:
    return (
        dropped_node_count > 0
        and peak_live_bytes_est_after_drop < peak_live_bytes_est_before_drop
        and drop_miss_count == 0
        and drop_delay_steps_max == 0
    )


def helper_lifecycle_effective(
    *,
    helper_dropped_count: int,
    helper_drop_miss_count: int,
    helper_peak_live_bytes_before_drop: int,
    helper_peak_live_bytes_after_drop: int,
    helper_drop_delay_steps_max: int,
) -> bool:
    return (
        helper_dropped_count > 0
        and helper_peak_live_bytes_after_drop < helper_peak_live_bytes_before_drop
        and helper_drop_miss_count == 0
        and helper_drop_delay_steps_max == 0
    )


def native_helper_usage_pattern(
    *,
    logical_consumer_count: int,
    effective_use_count: int,
) -> str:
    if effective_use_count <= 0:
        return "unread"
    if logical_consumer_count <= 1 and effective_use_count > 1:
        return "single_consumer_multi_read"
    if logical_consumer_count > 1:
        return "multi_consumer"
    return "single_consumer_single_read"


def classify_native_heavy_lifecycle(
    observation: NativeHeavyLifecycleInput,
) -> tuple[NativeHeavyLifecycleEligibility, str]:
    if not observation.is_native_heavy:
        return "forbidden", "not_native_heavy"
    if not observation.materialized:
        return "forbidden", "unresolved_fallback_path"
    if not observation.rewrite_applied:
        return "forbidden", "helper_alias_still_referenced"
    if not observation.consumer_semantics_stable:
        return "observable_only", "unstable_consumer_semantics"
    if observation.logical_consumer_count <= 0 or observation.effective_use_count <= 0:
        return "forbidden", "compiled_dependency_uncertain"
    return "candidate_future", ""
