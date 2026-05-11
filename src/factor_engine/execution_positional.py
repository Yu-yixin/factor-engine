from __future__ import annotations

from collections import deque
from collections.abc import Callable, Sequence
import time
from typing import Any, Literal

import polars as pl

from factor_engine.ast_nodes import CallNode, Expr
from factor_engine.errors import ExecutionError
from factor_engine.execution_ordering import PreparedFrame
from factor_engine.execution_output import restore_selected_columns
from factor_engine.execution_profiling import build_positional_phase_detail


KernelProfile = dict[str, float | int | bool]


def evaluate_positional_ordered_column(
    prepared: PreparedFrame,
    base_df: pl.DataFrame,
    expr: Expr,
    *,
    output_name: str,
    materialize_positional_call: Callable[[pl.DataFrame], tuple[pl.DataFrame, str, dict[tuple, str]]],
) -> pl.DataFrame:
    sorted_df, final_stage_name, _stage_cache = materialize_positional_call(prepared.sorted_df)
    if final_stage_name != output_name:
        sorted_df = sorted_df.with_columns(pl.col(final_stage_name).alias(output_name))

    return restore_selected_columns(
        sorted_df,
        prepared.row_index_name,
        [*base_df.columns, output_name],
    )


def materialize_positional_call_on_sorted_df(
    sorted_df: pl.DataFrame,
    *,
    expr: Expr,
    reserved_names: set[str],
    stage_cache: dict[tuple, str],
    runtime: Any = None,
    output_name: str | None = None,
    expect_positive_numeric_literal: Callable[[Expr, str], int],
    expr_key: Callable[[Expr], tuple],
    materialize_expr_on_sorted_df: Callable[..., tuple[pl.DataFrame, str, dict[tuple, str]]],
    temporary_helper_name: Callable[..., str],
    attach_positional_kernel_from_stage: Callable[..., pl.DataFrame],
) -> tuple[pl.DataFrame, str, dict[tuple, str]]:
    if not isinstance(expr, CallNode) or expr.name not in {"argmax", "argmin"}:
        raise ExecutionError("Internal error: positional ordered route expects argmax/argmin")
    if len(expr.args) != 2 or expr.kwargs:
        raise ExecutionError(f"{expr.name}(x, n) expects exactly 2 positional arguments")

    window = expect_positive_numeric_literal(expr.args[1], expr.name)
    result_cache_key = (
        "positional_kernel",
        expr.name,
        expr_key(expr.args[0]),
        window,
    )
    result_stage_name = stage_cache.get(result_cache_key)
    if result_stage_name is not None:
        return sorted_df, result_stage_name, stage_cache

    child_started_at = time.perf_counter()
    sorted_df, value_stage_name, stage_cache = materialize_expr_on_sorted_df(
        sorted_df,
        expr=expr.args[0],
        reserved_names=reserved_names,
        stage_cache=stage_cache,
        runtime=runtime,
    )
    child_expr_time_ms = (time.perf_counter() - child_started_at) * 1000
    result_stage_name = temporary_helper_name("__stage_value", reserved=reserved_names)
    sorted_df = attach_positional_kernel_from_stage(
        sorted_df,
        value_stage_name=value_stage_name,
        result_stage_name=result_stage_name,
        window=window,
        mode=expr.name,
        runtime=runtime,
        expression=repr(expr_key(expr)),
        output_name=output_name or result_stage_name,
        child_expr_time_ms=child_expr_time_ms,
    )
    if runtime is not None:
        runtime.register_stage(
            expr_key=result_cache_key,
            column_name=result_stage_name,
            stage_kind="positional_result",
            producer_route="positional_ordered",
            frame=sorted_df,
            cache_key=result_cache_key,
        )
    reserved_names.add(result_stage_name)
    stage_cache[result_cache_key] = result_stage_name
    return sorted_df, result_stage_name, stage_cache


def attach_positional_kernel_from_stage(
    sorted_df: pl.DataFrame,
    *,
    value_stage_name: str,
    result_stage_name: str,
    window: int,
    mode: Literal["argmax", "argmin"],
    code_col: str,
    evaluate_positional_kernel: Callable[..., tuple[pl.Series, KernelProfile]],
    current_rss_mb: Callable[[], float],
    runtime: Any = None,
    expression: str = "",
    output_name: str = "",
    child_expr_time_ms: float = 0.0,
) -> pl.DataFrame:
    if runtime is not None:
        runtime.consume_stage(
            value_stage_name,
            consumer_kind="positional_kernel",
            frame=sorted_df,
        )
    rss_before = current_rss_mb()
    positional_started_at = time.perf_counter()
    result, kernel_profile = evaluate_positional_kernel(
        sorted_df.get_column(value_stage_name),
        sorted_df.get_column(code_col),
        window,
        mode=mode,
    )
    positional_total_time_ms = (time.perf_counter() - positional_started_at) * 1000
    native_buffer_id: str | None = None
    if runtime is not None and bool(kernel_profile["native_kernel_used"]):
        native_buffer_id = runtime.register_native_buffer_created(
            related_output_name=output_name or result_stage_name,
            bytes_estimate=int(kernel_profile["native_output_buffer_bytes_estimate"]),
            frame=sorted_df,
            native_parallel_used=bool(kernel_profile["native_parallel_used"]),
            parallel_worker_count=int(kernel_profile["group_parallelism_level"]),
        )
    attach_started_at = time.perf_counter()
    attached = sorted_df.with_columns(result.alias(result_stage_name))
    result_attach_time_ms = (
        float(kernel_profile["series_construct_time_ms"])
        + (time.perf_counter() - attach_started_at) * 1000
    )
    if runtime is not None and native_buffer_id is not None:
        runtime.mark_native_buffer_attached(native_buffer_id, frame=attached)
        del result
        runtime.mark_native_buffer_released(native_buffer_id, frame=attached)
    rss_after = current_rss_mb()
    if runtime is not None:
        runtime.add_positional_phase(
            build_positional_phase_detail(
                run_id=runtime.profiler.run_id if runtime.profiler is not None else "",
                batch_id=runtime.batch_id,
                expression=expression,
                output_name=output_name or result_stage_name,
                function_name=mode,
                rows=sorted_df.height,
                groups=int(kernel_profile["group_count"]),
                window=window,
                child_stage_kind=runtime.stage_kind_for_column(value_stage_name),
                prepare_sort_time_ms=runtime.prepare_sort_time_ms,
                child_expr_time_ms=child_expr_time_ms,
                positional_total_time_ms=positional_total_time_ms,
                positional_to_list_time_ms=float(kernel_profile["to_list_time_ms"]),
                positional_group_scan_time_ms=float(kernel_profile["group_scan_time_ms"]),
                result_attach_time_ms=result_attach_time_ms,
                restore_time_ms=runtime.restore_time_ms,
                python_kernel_used=not bool(kernel_profile["native_kernel_used"]),
                native_kernel_used=bool(kernel_profile["native_kernel_used"]),
                native_low_copy_bridge_used=bool(kernel_profile["native_low_copy_bridge_used"]),
                python_object_bridge_used=bool(kernel_profile["python_object_bridge_used"]),
                native_parallel_used=bool(kernel_profile["native_parallel_used"]),
                group_parallelism_level=int(kernel_profile["group_parallelism_level"]),
                group_count=int(kernel_profile["group_count"]),
                avg_group_size=float(kernel_profile["avg_group_size"]),
                max_group_size=int(kernel_profile["max_group_size"]),
                output_non_null_count=int(kernel_profile["output_non_null_count"]),
                rss_before_mb=rss_before,
                rss_after_mb=rss_after,
                peak_rss_mb=max(rss_before, rss_after),
            )
        )
    return attached


def evaluate_positional_kernel(
    value_series: pl.Series,
    group_codes: pl.Series,
    window: int,
    *,
    mode: Literal["argmax", "argmin"],
    native_kernel: Callable[..., Any],
) -> tuple[pl.Series, KernelProfile]:
    native_result = native_kernel(
        value_series,
        group_codes,
        window,
        mode=mode,
    )
    if native_result is not None:
        group_lengths = (
            group_codes.to_frame("__code")
            .group_by("__code", maintain_order=True)
            .agg(pl.len().alias("__len"))
            .get_column("__len")
            .to_list()
        )
        output_non_null_count = native_result.series.is_not_null().sum()
        group_count = len(group_lengths)
        return native_result.series, {
            "to_list_time_ms": native_result.to_list_time_ms,
            "group_scan_time_ms": native_result.group_scan_time_ms,
            "series_construct_time_ms": native_result.series_construct_time_ms,
            "native_kernel_used": native_result.native_kernel_used,
            "native_low_copy_bridge_used": native_result.low_copy_bridge_used,
            "python_object_bridge_used": native_result.python_object_bridge_used,
            "native_parallel_used": native_result.native_parallel_used,
            "group_parallelism_level": native_result.group_parallelism_level,
            "native_output_buffer_bytes_estimate": native_result.output_buffer_bytes_estimate,
            "group_count": group_count,
            "avg_group_size": value_series.len() / group_count if group_count else 0.0,
            "max_group_size": max(group_lengths, default=0),
            "output_non_null_count": int(output_non_null_count),
        }

    to_list_started_at = time.perf_counter()
    values = value_series.to_list()
    to_list_time_ms = (time.perf_counter() - to_list_started_at) * 1000
    scan_started_at = time.perf_counter()
    group_lengths = (
        group_codes.to_frame("__code")
        .group_by("__code", maintain_order=True)
        .agg(pl.len().alias("__len"))
        .get_column("__len")
        .to_list()
    )
    output: list[int | None] = [None] * len(values)

    group_start = 0
    for group_length in group_lengths:
        group_end = group_start + group_length
        scan_group_positional_extreme(
            values,
            group_start,
            group_end,
            window,
            mode=mode,
            output=output,
        )
        group_start = group_end

    group_scan_time_ms = (time.perf_counter() - scan_started_at) * 1000
    series_started_at = time.perf_counter()
    result = pl.Series(value_series.name, output, dtype=pl.Int64)
    series_construct_time_ms = (time.perf_counter() - series_started_at) * 1000
    group_count = len(group_lengths)
    return result, {
        "to_list_time_ms": to_list_time_ms,
        "group_scan_time_ms": group_scan_time_ms,
        "series_construct_time_ms": series_construct_time_ms,
        "native_kernel_used": False,
        "native_low_copy_bridge_used": False,
        "python_object_bridge_used": True,
        "native_parallel_used": False,
        "group_parallelism_level": 1,
        "native_output_buffer_bytes_estimate": 0,
        "group_count": group_count,
        "avg_group_size": len(values) / group_count if group_count else 0.0,
        "max_group_size": max(group_lengths, default=0),
        "output_non_null_count": sum(item is not None for item in output),
    }


def scan_group_positional_extreme(
    values: Sequence[object],
    start: int,
    end: int,
    window: int,
    *,
    mode: Literal["argmax", "argmin"],
    output: list[int | None],
) -> None:
    candidates: deque[int] = deque()
    choose_max = mode == "argmax"

    for index in range(start, end):
        first_valid_index = index - window + 1
        while candidates and candidates[0] < first_valid_index:
            candidates.popleft()

        current_value = values[index]
        if current_value is not None:
            while candidates:
                tail_value = values[candidates[-1]]
                if tail_value is None:
                    candidates.pop()
                    continue
                if choose_max:
                    should_drop_tail = current_value >= tail_value
                else:
                    should_drop_tail = current_value <= tail_value
                if not should_drop_tail:
                    break
                candidates.pop()
            candidates.append(index)

        output[index] = None if not candidates else index - candidates[0]
