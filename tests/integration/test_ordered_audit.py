import polars as pl
import pytest

from factor_engine.engine import FactorEngine
from factor_engine.planner import ExecutionPlanner
from factor_engine.registry import get_ordered_audit_matrix, get_ordered_roots
from factor_engine.validator import Validator


def build_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "time": [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3],
            "code": ["A", "B", "C", "D"] * 3,
            "industry": ["X", "X", "Y", "Y"] * 3,
            "close": [10.0, 20.0, 100.0, 200.0, 11.0, 19.0, 101.0, 199.0, 12.0, 18.0, 102.0, 198.0],
            "open": [9.0, 19.0, 99.0, 198.0, 10.0, 18.0, 100.0, 197.0, 11.0, 17.0, 101.0, 196.0],
            "volume": [5.0, 6.0, 20.0, 30.0, 6.0, 7.0, 18.0, 28.0, 7.0, 8.0, 16.0, 26.0],
        }
    )


def parse_and_plan(expr_text: str):
    engine = FactorEngine()
    expr = engine.parse(expr_text)
    validation = Validator(schema=build_df().schema).validate(expr)
    plan = ExecutionPlanner().build_plan(expr, validation)
    return plan


def assert_optional_float_lists_close(actual: list[object], expected: list[object]) -> None:
    assert len(actual) == len(expected)
    for observed, target in zip(actual, expected, strict=True):
        if observed is None or target is None:
            assert observed is None and target is None
            continue
        if isinstance(observed, float) and isinstance(target, float):
            if observed != observed or target != target:
                assert observed != observed and target != target
                continue
        assert observed == pytest.approx(target)


@pytest.mark.parametrize(
    ("family", "name", "expr_text", "manual_source", "manual_step", "window"),
    [
        ("rolling_single", "ts_mean", "ts_mean(rank(close), 2)", "rank(close)", "ts_mean(x, 2)", 2),
        ("rolling_single", "ts_std", "ts_std(rank(close), 2)", "rank(close)", "ts_std(x, 2)", 2),
        ("rolling_single", "ts_sum", "ts_sum(rank(close), 2)", "rank(close)", "ts_sum(x, 2)", 2),
        ("rolling_single", "ts_min", "ts_min(rank(close), 2)", "rank(close)", "ts_min(x, 2)", 2),
        ("rolling_single", "ts_max", "ts_max(rank(close), 2)", "rank(close)", "ts_max(x, 2)", 2),
        ("rolling_single", "ts_median", "ts_median(rank(close), 2)", "rank(close)", "ts_median(x, 2)", 2),
        ("rolling_single", "skew", "skew(rank(close), 3)", "rank(close)", "skew(x, 3)", 3),
        ("rolling_single", "kurt", "kurt(rank(close), 4)", "rank(close)", "kurt(x, 4)", 4),
        ("pair", "corr", "corr(rank(open), rank(volume), 3)", None, None, 3),
        ("pair", "cov", "cov(rank(open), rank(volume), 3)", None, None, 3),
        ("positional", "argmax", "argmax(rank(close), 2)", "rank(close)", "argmax(x, 2)", 2),
        ("positional", "argmin", "argmin(rank(close), 2)", "rank(close)", "argmin(x, 2)", 2),
        ("rank", "ts_rank", "ts_rank(rank(close), 2)", "rank(close)", "ts_rank(x, 2)", 2),
    ],
)
def test_ordered_audit_split_step_matches_nested(
    family: str,
    name: str,
    expr_text: str,
    manual_source: str | None,
    manual_step: str | None,
    window: int,
):
    df = build_df()
    engine = FactorEngine()

    if family == "pair":
        staged = engine.evaluate_many(
            [
                ("left", "rank(open)"),
                ("right", "rank(volume)"),
            ],
            df,
        )
        manual = engine.evaluate(f"{name}(left, right, {window})", staged)
    else:
        staged = engine.evaluate(manual_source, df, output_name="x")
        manual = engine.evaluate(manual_step, staged)

    nested = engine.evaluate(expr_text, df)
    assert_optional_float_lists_close(nested["result"].to_list(), manual["result"].to_list())


@pytest.mark.parametrize(
    ("expr_text", "expected_route"),
    [
        ("ts_mean(rank(close), 2)", "materialized_ordered"),
        ("ts_std(rank(close), 2)", "materialized_ordered"),
        ("ts_sum(rank(close), 2)", "materialized_ordered"),
        ("sum(rank(close), 2)", "materialized_ordered"),
        ("ts_min(rank(close), 2)", "materialized_ordered"),
        ("ts_max(rank(close), 2)", "materialized_ordered"),
        ("ts_median(rank(close), 2)", "materialized_ordered"),
        ("skew(rank(close), 3)", "materialized_ordered"),
        ("kurt(rank(close), 4)", "materialized_ordered"),
        ("corr(rank(open), rank(volume), 3)", "materialized_ordered"),
        ("cov(rank(open), rank(volume), 3)", "materialized_ordered"),
        ("argmax(rank(close), 2)", "materialized_ordered"),
        ("argmin(rank(close), 2)", "materialized_ordered"),
        ("ts_rank(rank(close), 2)", "materialized_ordered"),
    ],
)
def test_ordered_audit_routes_audited_roots_to_safe_path(expr_text: str, expected_route: str):
    plan = parse_and_plan(expr_text)
    assert plan.route == expected_route


@pytest.mark.parametrize(
    ("expr_text", "expected_func", "expected_input_count", "expected_window"),
    [
        ("ts_mean(rank(close), 2)", "ts_mean", 1, 2),
        ("sum(rank(close), 2)", "ts_sum", 1, 2),
        ("corr(rank(open), rank(volume), 3)", "corr", 2, 3),
        ("correlation(rank(open), rank(volume), 3)", "corr", 2, 3),
        ("argmax(rank(close), 2)", "argmax", 1, 2),
        ("ts_rank(rank(close), 2)", "ts_rank", 1, 2),
    ],
)
def test_ordered_audit_route_trace_is_explicit(
    expr_text: str,
    expected_func: str,
    expected_input_count: int,
    expected_window: int,
):
    trace = FactorEngine().inspect_plan(expr_text, build_df())

    assert trace["route"] == "materialized_ordered"
    assert trace["materialized_func"] == expected_func
    assert trace["materialized_input_count"] == expected_input_count
    assert trace["materialized_window"] == expected_window


@pytest.mark.parametrize(
    ("alias_expr", "canonical_expr"),
    [
        ("sum(rank(close), 2)", "ts_sum(rank(close), 2)"),
        ("stddev(rank(close), 2)", "ts_std(rank(close), 2)"),
        ("min(rank(close), 2)", "ts_min(rank(close), 2)"),
        ("max(rank(close), 2)", "ts_max(rank(close), 2)"),
        ("correlation(rank(open), rank(volume), 3)", "corr(rank(open), rank(volume), 3)"),
        ("covariance(rank(open), rank(volume), 3)", "cov(rank(open), rank(volume), 3)"),
    ],
)
def test_alias_route_trace_matches_canonical_ordered_function(
    alias_expr: str,
    canonical_expr: str,
):
    alias_trace = FactorEngine().inspect_plan(alias_expr, build_df())
    canonical_trace = FactorEngine().inspect_plan(canonical_expr, build_df())

    assert alias_trace["route"] == canonical_trace["route"]
    assert alias_trace["root_window_kind"] == canonical_trace["root_window_kind"]
    assert alias_trace["materialized_func"] == canonical_trace["materialized_func"]
    assert alias_trace["materialized_input_count"] == canonical_trace["materialized_input_count"]
    assert alias_trace["materialized_window"] == canonical_trace["materialized_window"]


def test_ordered_audit_marks_positional_roots_with_positional_window_kind():
    trace = FactorEngine().inspect_plan("argmax(close, 3)", build_df())

    assert trace["route"] == "positional_ordered"
    assert trace["root_window_kind"] == "positional"


@pytest.mark.parametrize(
    "expr_text",
    [
        "argmax(seg_mean(close, 2), 2)",
        "ts_rank(seg_mean(close, 2), 2)",
        "corr(seg_mean(open, 2), rank(volume), 3)",
    ],
)
def test_ordered_audit_segmented_children_do_not_silently_downgrade_to_plain_compiled(
    expr_text: str,
):
    trace = FactorEngine().inspect_plan(expr_text, build_df())

    assert trace["route"] != "compiled"


def test_ordered_audit_completeness_matches_registry_source_of_truth():
    ordered_roots = {spec.name for spec in get_ordered_roots()}
    documented_roots = {entry.name for entry in get_ordered_audit_matrix()}

    assert documented_roots == ordered_roots


def test_ordered_audit_matrix_contains_only_audited_entries():
    matrix = get_ordered_audit_matrix()

    assert matrix
    assert all(entry.audit_status == "audited" for entry in matrix)
    assert all(entry.audit_status_label == "audited" for entry in matrix)


def test_ordered_audit_preserves_input_row_alignment_for_materialized_paths():
    df = build_df().sample(fraction=1.0, shuffle=True, seed=7)
    result = FactorEngine().evaluate("argmax(rank(close), 2)", df)

    assert result.select(df.columns).to_dict(as_series=False) == df.to_dict(as_series=False)
    assert result.height == df.height


def test_ordered_audit_preserves_group_boundaries_for_grouped_children():
    df = build_df()
    engine = FactorEngine()

    manual_stage = engine.evaluate("group_rank(close, industry)", df, output_name="x")
    manual = engine.evaluate("ts_rank(x, 2)", manual_stage)
    nested = engine.evaluate("ts_rank(group_rank(close, industry), 2)", df)

    assert_optional_float_lists_close(nested["result"].to_list(), manual["result"].to_list())


def test_ordered_audit_preserves_null_contract_for_grouped_rank_child():
    df = build_df().with_columns(
        pl.when(pl.col("code") == "A").then(None).otherwise(pl.col("close")).alias("close")
    )
    engine = FactorEngine()

    manual_stage = engine.evaluate("group_rank(close, industry)", df, output_name="x")
    manual = engine.evaluate("argmin(x, 2)", manual_stage)
    nested = engine.evaluate("argmin(group_rank(close, industry), 2)", df)

    assert nested["result"].to_list() == manual["result"].to_list()


@pytest.mark.parametrize(
    "expr_text",
    [
        "ts_mean(group_rank(close, industry), 2)",
        "ts_std(group_demean(close, industry), 2)",
        "ts_rank(group_rank(close, industry), 2)",
        "argmax(group_rank(close, industry), 2)",
        "argmin(group_rank(close, industry), 2)",
        "corr(group_rank(open, industry), group_rank(volume, industry), 3)",
        "cov(group_rank(open, industry), group_rank(volume, industry), 3)",
    ],
)
def test_ordered_audit_accepts_grouped_cross_inputs(expr_text: str):
    result = FactorEngine().evaluate(expr_text, build_df())
    assert "result" in result.columns
