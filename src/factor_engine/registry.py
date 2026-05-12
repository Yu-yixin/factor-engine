from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from factor_engine.physical_properties import OperatorContract, PhysicalProperties


ResultKind = Literal["column", "table"]
ArgRule = Literal["any_expr", "variable_only"]
ExecutionKind = Literal["pointwise", "cross_sectional", "time_series", "table"]
WindowKind = Literal["none", "rolling", "positional", "segmented", "recursive"]
ProducesMode = Literal["same_as_requires", "custom"]
PropertyToken = Literal["$time", "$code", "$group"]
OrderedAuditStatus = Literal["audited", "blocked"]


@dataclass(frozen=True)
class FunctionSpec:
    # FunctionSpec is the semantic layer between parsing and execution.
    name: str
    min_args: int
    max_args: int
    allowed_kwargs: frozenset[str] = frozenset()
    result_kind: ResultKind = "column"
    root_only: bool = False
    arg_rule: ArgRule = "any_expr"
    backend: str | None = None
    requires_time_col: bool = False
    requires_code_col: bool = False
    numeric_arg_positions: tuple[int, ...] = ()
    boolean_arg_positions: tuple[int, ...] = ()
    execution_kind: ExecutionKind = "pointwise"
    window_kind: WindowKind = "none"
    needs_code_group: bool = False
    needs_time_group: bool = False
    needs_time_order: bool = False
    requires_partition_by: tuple[PropertyToken, ...] = ()
    requires_order_by: tuple[PropertyToken, ...] = ()
    requires_segment: str | None = None
    produces_partition_by: tuple[PropertyToken, ...] = ()
    produces_order_by: tuple[PropertyToken, ...] = ()
    produces_segment: str | None = None
    produces_mode: ProducesMode = "same_as_requires"
    accepts_materialized_input: bool = False
    is_single_input_ordered_root: bool = False


@dataclass(frozen=True)
class OrderedAuditEntry:
    name: str
    family: str
    audit_status: OrderedAuditStatus
    current_route: str
    risk: str
    test_status: str
    audit_status_label: str


def _spec(
    name: str,
    min_args: int,
    max_args: int,
    *,
    allowed_kwargs: set[str] | None = None,
    result_kind: ResultKind = "column",
    root_only: bool = False,
    arg_rule: ArgRule = "any_expr",
    backend: str | None = None,
    requires_time_col: bool = False,
    requires_code_col: bool = False,
    numeric_arg_positions: tuple[int, ...] = (),
    boolean_arg_positions: tuple[int, ...] = (),
    execution_kind: ExecutionKind = "pointwise",
    window_kind: WindowKind = "none",
    needs_code_group: bool = False,
    needs_time_group: bool = False,
    needs_time_order: bool = False,
    requires_partition_by: tuple[PropertyToken, ...] = (),
    requires_order_by: tuple[PropertyToken, ...] = (),
    requires_segment: str | None = None,
    produces_partition_by: tuple[PropertyToken, ...] = (),
    produces_order_by: tuple[PropertyToken, ...] = (),
    produces_segment: str | None = None,
    produces_mode: ProducesMode = "same_as_requires",
    accepts_materialized_input: bool = False,
    is_single_input_ordered_root: bool = False,
) -> FunctionSpec:
    return FunctionSpec(
        name=name,
        min_args=min_args,
        max_args=max_args,
        allowed_kwargs=frozenset(allowed_kwargs or set()),
        result_kind=result_kind,
        root_only=root_only,
        arg_rule=arg_rule,
        backend=backend,
        requires_time_col=requires_time_col,
        requires_code_col=requires_code_col,
        numeric_arg_positions=numeric_arg_positions,
        boolean_arg_positions=boolean_arg_positions,
        execution_kind=execution_kind,
        window_kind=window_kind,
        needs_code_group=needs_code_group,
        needs_time_group=needs_time_group,
        needs_time_order=needs_time_order,
        requires_partition_by=requires_partition_by,
        requires_order_by=requires_order_by,
        requires_segment=requires_segment,
        produces_partition_by=produces_partition_by,
        produces_order_by=produces_order_by,
        produces_segment=produces_segment,
        produces_mode=produces_mode,
        accepts_materialized_input=accepts_materialized_input,
        is_single_input_ordered_root=is_single_input_ordered_root,
    )


def _resolve_property_tokens(
    tokens: tuple[PropertyToken, ...],
    *,
    time_col: str,
    code_col: str,
    group_col: str | None = None,
) -> tuple[str, ...]:
    resolved: list[str] = []
    for token in tokens:
        if token == "$time":
            resolved.append(time_col)
            continue
        if token == "$code":
            resolved.append(code_col)
            continue
        if token == "$group":
            if group_col is None:
                raise ValueError("group property token requires an explicit group column")
            resolved.append(group_col)
            continue
        raise ValueError(f"Unsupported property token: {token}")
    return tuple(resolved)

def properties_for_spec_requires(
    spec: FunctionSpec,
    *,
    time_col: str,
    code_col: str,
    group_col: str | None = None,
) -> PhysicalProperties:
    return PhysicalProperties(
        partition_by=_resolve_property_tokens(
            spec.requires_partition_by,
            time_col=time_col,
            code_col=code_col,
            group_col=group_col,
        ),
        order_by=_resolve_property_tokens(
            spec.requires_order_by,
            time_col=time_col,
            code_col=code_col,
            group_col=group_col,
        ),
        segment=spec.requires_segment,
    )


def properties_for_spec_produces(
    spec: FunctionSpec,
    *,
    time_col: str,
    code_col: str,
    group_col: str | None = None,
) -> PhysicalProperties | None:
    if spec.produces_mode != "custom":
        return None

    return PhysicalProperties(
        partition_by=_resolve_property_tokens(
            spec.produces_partition_by,
            time_col=time_col,
            code_col=code_col,
            group_col=group_col,
        ),
        order_by=_resolve_property_tokens(
            spec.produces_order_by,
            time_col=time_col,
            code_col=code_col,
            group_col=group_col,
        ),
        segment=spec.produces_segment,
    )


def build_operator_contract(
    spec: FunctionSpec,
    *,
    time_col: str,
    code_col: str,
    group_col: str | None = None,
) -> OperatorContract:
    requires = properties_for_spec_requires(
        spec,
        time_col=time_col,
        code_col=code_col,
        group_col=group_col,
    )
    return OperatorContract(
        requires=requires,
        produces_mode=spec.produces_mode,
        produces=properties_for_spec_produces(
            spec,
            time_col=time_col,
            code_col=code_col,
            group_col=group_col,
        ),
        accepts_materialized_input=spec.accepts_materialized_input,
        is_single_input_ordered_root=spec.is_single_input_ordered_root,
    )


FUNCTION_REGISTRY: dict[str, FunctionSpec] = {
    "abs": _spec(
        "abs",
        1,
        1,
        numeric_arg_positions=(0,),
    ),
    "corr": _spec(
        "corr",
        3,
        3,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0, 1),
        execution_kind="time_series",
        window_kind="positional",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        accepts_materialized_input=True,
    ),
    "argmax": _spec(
        "argmax",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="positional",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        accepts_materialized_input=True,
        is_single_input_ordered_root=True,
    ),
    "argmin": _spec(
        "argmin",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="positional",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        accepts_materialized_input=True,
        is_single_input_ordered_root=True,
    ),
    "clip": _spec(
        "clip",
        3,
        3,
        numeric_arg_positions=(0, 1, 2),
    ),
    "cov": _spec(
        "cov",
        3,
        3,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0, 1),
        execution_kind="time_series",
        window_kind="rolling",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        accepts_materialized_input=True,
    ),
    "delay": _spec(
        "delay",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        execution_kind="time_series",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
    ),
    "delta": _spec(
        "delta",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="time_series",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
    ),
    "ema": _spec(
        "ema",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="recursive",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
    ),
    "demean": _spec(
        "demean",
        1,
        1,
        requires_time_col=True,
        numeric_arg_positions=(0,),
        execution_kind="cross_sectional",
        needs_time_group=True,
        requires_partition_by=("$time",),
        accepts_materialized_input=True,
    ),
    "group_demean": _spec(
        "group_demean",
        2,
        2,
        requires_time_col=True,
        numeric_arg_positions=(0,),
        execution_kind="cross_sectional",
        needs_time_group=True,
        requires_partition_by=("$time", "$group"),
        accepts_materialized_input=True,
    ),
    "group_rank": _spec(
        "group_rank",
        2,
        2,
        allowed_kwargs={"ascending", "pct"},
        requires_time_col=True,
        numeric_arg_positions=(0,),
        execution_kind="cross_sectional",
        needs_time_group=True,
        requires_partition_by=("$time", "$group"),
        accepts_materialized_input=True,
    ),
    "group_zscore": _spec(
        "group_zscore",
        2,
        2,
        requires_time_col=True,
        numeric_arg_positions=(0,),
        execution_kind="cross_sectional",
        needs_time_group=True,
        requires_partition_by=("$time", "$group"),
        accepts_materialized_input=True,
    ),
    "fill_null": _spec("fill_null", 2, 2),
    "fft": _spec(
        "fft",
        1,
        1,
        result_kind="table",
        root_only=True,
        arg_rule="variable_only",
        backend="fft",
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="table",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
    ),
    "is_null": _spec("is_null", 1, 1),
    "log": _spec(
        "log",
        1,
        1,
        numeric_arg_positions=(0,),
    ),
    "kurt": _spec(
        "kurt",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="rolling",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        accepts_materialized_input=True,
        is_single_input_ordered_root=True,
    ),
    "pct_change": _spec(
        "pct_change",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="time_series",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
    ),
    "rank": _spec(
        "rank",
        1,
        1,
        allowed_kwargs={"ascending", "pct"},
        requires_time_col=True,
        numeric_arg_positions=(0,),
        execution_kind="cross_sectional",
        needs_time_group=True,
        requires_partition_by=("$time",),
        accepts_materialized_input=True,
    ),
    "seg_mean": _spec(
        "seg_mean",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="segmented",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        requires_segment="segment_spec",
    ),
    "seg_sum": _spec(
        "seg_sum",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="segmented",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        requires_segment="segment_spec",
    ),
    "seglen_mean": _spec(
        "seglen_mean",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="segmented",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        requires_segment="segment_spec",
    ),
    "seglen_sum": _spec(
        "seglen_sum",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="segmented",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        requires_segment="segment_spec",
    ),
    "seglen_count": _spec(
        "seglen_count",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        boolean_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="segmented",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        requires_segment="segment_spec",
    ),
    "seglen_any": _spec(
        "seglen_any",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        boolean_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="segmented",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        requires_segment="segment_spec",
    ),
    "seglen_all": _spec(
        "seglen_all",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        boolean_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="segmented",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        requires_segment="segment_spec",
    ),
    "seg_count": _spec(
        "seg_count",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        boolean_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="segmented",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        requires_segment="segment_spec",
    ),
    "seg_any": _spec(
        "seg_any",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        boolean_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="segmented",
        needs_code_group=True,
        needs_time_order=True,
    ),
    "seg_all": _spec(
        "seg_all",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        boolean_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="segmented",
        needs_code_group=True,
        needs_time_order=True,
    ),
    "sign": _spec(
        "sign",
        1,
        1,
        numeric_arg_positions=(0,),
    ),
    "signedpower": _spec(
        "signedpower",
        2,
        2,
        numeric_arg_positions=(0, 1),
    ),
    "skew": _spec(
        "skew",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="time_series",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        accepts_materialized_input=True,
        is_single_input_ordered_root=True,
    ),
    "ts_all": _spec(
        "ts_all",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        boolean_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="rolling",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
    ),
    "ts_any": _spec(
        "ts_any",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        boolean_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="rolling",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
    ),
    "ts_count": _spec(
        "ts_count",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        boolean_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="rolling",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
    ),
    "ts_max": _spec(
        "ts_max",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="rolling",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        accepts_materialized_input=True,
        is_single_input_ordered_root=True,
    ),
    "ts_median": _spec(
        "ts_median",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="rolling",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        accepts_materialized_input=True,
        is_single_input_ordered_root=True,
    ),
    "scale": _spec(
        "scale",
        1,
        2,
        numeric_arg_positions=(0, 1),
        requires_time_col=True,
        execution_kind="cross_sectional",
        needs_time_group=True,
        requires_partition_by=("$time",),
        accepts_materialized_input=True,
    ),
    "ts_mean": _spec(
        "ts_mean",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="rolling",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        accepts_materialized_input=True,
        is_single_input_ordered_root=True,
    ),
    "ts_min": _spec(
        "ts_min",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="rolling",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        accepts_materialized_input=True,
        is_single_input_ordered_root=True,
    ),
    "ts_rank": _spec(
        "ts_rank",
        2,
        2,
        allowed_kwargs={"ascending", "pct"},
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="rolling",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        accepts_materialized_input=True,
        is_single_input_ordered_root=True,
    ),
    "ts_std": _spec(
        "ts_std",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="rolling",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        accepts_materialized_input=True,
        is_single_input_ordered_root=True,
    ),
    "ts_sum": _spec(
        "ts_sum",
        2,
        2,
        requires_time_col=True,
        requires_code_col=True,
        numeric_arg_positions=(0,),
        execution_kind="time_series",
        window_kind="rolling",
        needs_code_group=True,
        needs_time_order=True,
        requires_partition_by=("$code",),
        requires_order_by=("$time",),
        accepts_materialized_input=True,
        is_single_input_ordered_root=True,
    ),
    "where": _spec("where", 3, 3),
    "zscore": _spec(
        "zscore",
        1,
        1,
        requires_time_col=True,
        numeric_arg_positions=(0,),
        execution_kind="cross_sectional",
        needs_time_group=True,
        requires_partition_by=("$time",),
        accepts_materialized_input=True,
    ),
}


FUNCTION_ALIASES: dict[str, str] = {
    "sum": "ts_sum",
    "stddev": "ts_std",
    "correlation": "corr",
    "covariance": "cov",
    "min": "ts_min",
    "max": "ts_max",
}


ORDERED_AUDIT_MATRIX: tuple[OrderedAuditEntry, ...] = (
    OrderedAuditEntry(
        name="ts_mean",
        family="rolling_single",
        audit_status="audited",
        current_route="materialized_ordered when child is cross/grouped, else positional_ordered",
        risk="medium",
        test_status="split-step covered",
        audit_status_label="audited",
    ),
    OrderedAuditEntry(
        name="ts_std",
        family="rolling_single",
        audit_status="audited",
        current_route="materialized_ordered when child is cross/grouped, else positional_ordered",
        risk="medium",
        test_status="split-step covered",
        audit_status_label="audited",
    ),
    OrderedAuditEntry(
        name="ts_sum",
        family="rolling_single",
        audit_status="audited",
        current_route="materialized_ordered when child is cross/grouped, else compiled",
        risk="medium",
        test_status="split-step covered",
        audit_status_label="audited",
    ),
    OrderedAuditEntry(
        name="ts_min",
        family="rolling_single",
        audit_status="audited",
        current_route="materialized_ordered when child is cross/grouped, else compiled",
        risk="medium",
        test_status="split-step covered",
        audit_status_label="audited",
    ),
    OrderedAuditEntry(
        name="ts_max",
        family="rolling_single",
        audit_status="audited",
        current_route="materialized_ordered when child is cross/grouped, else compiled",
        risk="medium",
        test_status="split-step covered",
        audit_status_label="audited",
    ),
    OrderedAuditEntry(
        name="ts_median",
        family="rolling_single",
        audit_status="audited",
        current_route="materialized_ordered when child is cross/grouped, else compiled",
        risk="medium",
        test_status="split-step covered",
        audit_status_label="audited",
    ),
    OrderedAuditEntry(
        name="skew",
        family="rolling_single",
        audit_status="audited",
        current_route="materialized_ordered when child is cross/grouped, else compiled",
        risk="medium",
        test_status="split-step covered",
        audit_status_label="audited",
    ),
    OrderedAuditEntry(
        name="kurt",
        family="rolling_single",
        audit_status="audited",
        current_route="materialized_ordered when child is cross/grouped, else compiled",
        risk="medium",
        test_status="split-step covered",
        audit_status_label="audited",
    ),
    OrderedAuditEntry(
        name="corr",
        family="pair",
        audit_status="audited",
        current_route="materialized_ordered when either child is cross/grouped, else compiled",
        risk="high",
        test_status="split-step covered",
        audit_status_label="audited",
    ),
    OrderedAuditEntry(
        name="cov",
        family="pair",
        audit_status="audited",
        current_route="materialized_ordered when either child is cross/grouped, else compiled",
        risk="high",
        test_status="split-step covered",
        audit_status_label="audited",
    ),
    OrderedAuditEntry(
        name="argmax",
        family="positional",
        audit_status="audited",
        current_route="materialized_ordered when child is cross/grouped, else compiled",
        risk="medium",
        test_status="split-step covered",
        audit_status_label="audited",
    ),
    OrderedAuditEntry(
        name="argmin",
        family="positional",
        audit_status="audited",
        current_route="materialized_ordered when child is cross/grouped, else compiled",
        risk="medium",
        test_status="split-step covered",
        audit_status_label="audited",
    ),
    OrderedAuditEntry(
        name="ts_rank",
        family="rank",
        audit_status="audited",
        current_route="materialized_ordered when child is cross/grouped, else compiled",
        risk="medium",
        test_status="split-step covered",
        audit_status_label="audited",
    ),
)


def get_ordered_roots() -> tuple[FunctionSpec, ...]:
    return tuple(
        spec
        for spec in FUNCTION_REGISTRY.values()
        if spec.needs_time_order and spec.accepts_materialized_input
    )


def get_ordered_audit_matrix() -> tuple[OrderedAuditEntry, ...]:
    return ORDERED_AUDIT_MATRIX


def canonical_function_name(name: str) -> str:
    return FUNCTION_ALIASES.get(name, name)


def get_function_spec(name: str) -> FunctionSpec | None:
    return FUNCTION_REGISTRY.get(canonical_function_name(name))
