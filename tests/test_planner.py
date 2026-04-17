import polars as pl
import pytest

from factor_engine.lexer import Lexer
from factor_engine.parser import Parser
from factor_engine.physical_properties import PhysicalProperties, satisfies
from factor_engine.planner import BatchPlanningItem, ExecutionPlanner
from factor_engine.registry import build_operator_contract, get_function_spec
from factor_engine.validator import Validator


def parse_expression(text: str):
    tokens = Lexer(text).tokenize()
    return Parser(tokens).parse()


def build_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "time": [1, 1, 1, 1, 2, 2, 2, 2],
            "code": ["A", "B", "C", "D"] * 2,
            "industry": ["X", "X", "Y", "Y"] * 2,
            "close": [10.0, 20.0, 100.0, 200.0, 11.0, 19.0, 101.0, 199.0],
            "open": [9.0, 19.0, 99.0, 198.0, 10.0, 18.0, 100.0, 197.0],
        }
    )


def validate_expression(text: str, df: pl.DataFrame):
    expr = parse_expression(text)
    validation = Validator(schema=df.schema).validate(expr)
    return expr, validation


def test_planner_routes_simple_expression_to_compiled():
    expr, validation = validate_expression("close - open", build_df())
    plan = ExecutionPlanner().build_plan(expr, validation)

    assert plan.route == "compiled"
    assert plan.staged is None


def test_physical_properties_satisfy_plain_child():
    child = PhysicalProperties()
    parent = PhysicalProperties(partition_by=("code",), order_by=("time",))

    assert satisfies(child, parent) is True


def test_physical_properties_satisfy_plain_parent():
    child = PhysicalProperties(partition_by=("code",), order_by=("time",))
    parent = PhysicalProperties()

    assert satisfies(child, parent) is True


def test_physical_properties_satisfy_prefix_order_rule():
    child = PhysicalProperties(partition_by=("code",), order_by=("time", "subtime"))
    parent = PhysicalProperties(partition_by=("code",), order_by=("time",))

    assert satisfies(child, parent) is True


def test_physical_properties_reject_partition_mismatch():
    child = PhysicalProperties(partition_by=("time",))
    parent = PhysicalProperties(partition_by=("code",), order_by=("time",))

    assert satisfies(child, parent) is False


def test_registry_builds_explicit_cross_section_contract():
    spec = get_function_spec("rank")
    assert spec is not None

    contract = build_operator_contract(spec, time_col="time", code_col="code")

    assert contract.requires == PhysicalProperties(partition_by=("time",))
    assert contract.produced_properties() == PhysicalProperties(partition_by=("time",))


def test_registry_builds_explicit_grouped_contract():
    spec = get_function_spec("group_rank")
    assert spec is not None

    contract = build_operator_contract(
        spec,
        time_col="time",
        code_col="code",
        group_col="industry",
    )

    assert contract.requires == PhysicalProperties(partition_by=("time", "industry"))
    assert contract.produced_properties() == PhysicalProperties(partition_by=("time", "industry"))


def test_registry_builds_explicit_ordered_contract():
    spec = get_function_spec("ts_mean")
    assert spec is not None

    contract = build_operator_contract(spec, time_col="time", code_col="code")

    assert contract.requires == PhysicalProperties(partition_by=("code",), order_by=("time",))
    assert contract.produced_properties() == PhysicalProperties(
        partition_by=("code",),
        order_by=("time",),
    )
    assert contract.is_single_input_ordered_root is True


@pytest.mark.parametrize("func_name, window", [
    ("ts_min", 3),
    ("ts_max", 3),
    ("ts_median", 3),
    ("ts_sum", 3),
    ("skew", 3),
    ("kurt", 4),
])
def test_registry_marks_supported_single_input_ordered_family(
    func_name: str,
    window: int,
):
    spec = get_function_spec(func_name)
    assert spec is not None

    contract = build_operator_contract(spec, time_col="time", code_col="code")

    assert contract.requires == PhysicalProperties(partition_by=("code",), order_by=("time",))
    assert contract.is_single_input_ordered_root is True


def test_registry_builds_explicit_segmented_contract():
    spec = get_function_spec("seg_mean")
    assert spec is not None

    contract = build_operator_contract(spec, time_col="time", code_col="code")

    assert contract.requires == PhysicalProperties(
        partition_by=("code",),
        order_by=("time",),
        segment="segment_spec",
    )
    assert contract.produced_properties() == PhysicalProperties(
        partition_by=("code",),
        order_by=("time",),
        segment="segment_spec",
    )


def test_planner_routes_segmented_expression_to_segmented():
    expr, validation = validate_expression("seg_mean(close, 2)", build_df())
    plan = ExecutionPlanner().build_plan(expr, validation)

    assert plan.route == "segmented"
    assert plan.staged is None


def test_planner_routes_nested_cross_section_over_ordered_to_staged():
    expr, validation = validate_expression("demean(ts_rank(close, 2))", build_df())
    plan = ExecutionPlanner().build_plan(expr, validation)

    assert plan.route == "staged"
    assert plan.staged is not None
    assert plan.staged.source_expr == parse_expression("ts_rank(close, 2)")
    assert [step.func_name for step in plan.staged.steps] == ["demean"]


def test_planner_routes_scale_over_ordered_to_staged():
    expr, validation = validate_expression("scale(ts_rank(close, 2), 2)", build_df())
    plan = ExecutionPlanner().build_plan(expr, validation)

    assert plan.route == "staged"
    assert plan.staged is not None
    assert plan.staged.source_expr == parse_expression("ts_rank(close, 2)")
    assert len(plan.staged.steps) == 1
    assert plan.staged.steps[0].func_name == "scale"
    assert plan.staged.steps[0].scale_to == 2.0


def test_planner_routes_group_rank_over_ordered_to_staged():
    expr, validation = validate_expression(
        "group_rank(ts_rank(close, 2), industry, pct=true)",
        build_df(),
    )
    plan = ExecutionPlanner().build_plan(expr, validation)

    assert plan.route == "staged"
    assert plan.staged is not None
    assert plan.staged.source_expr == parse_expression("ts_rank(close, 2)")
    assert len(plan.staged.steps) == 1
    assert plan.staged.steps[0].func_name == "group_rank"
    assert plan.staged.steps[0].group_col == "industry"
    assert plan.staged.steps[0].pct is True


def test_planner_keeps_plain_cross_section_compiled():
    expr, validation = validate_expression("rank(close, pct=true)", build_df())
    plan = ExecutionPlanner().build_plan(expr, validation)

    assert plan.route == "compiled"
    assert plan.staged is None


def test_planner_builds_recursive_staged_chain_for_deep_expression():
    expr, validation = validate_expression(
        "rank(demean(ts_mean(close, 5)), pct=true)",
        build_df(),
    )
    plan = ExecutionPlanner().build_plan(expr, validation)

    assert plan.route == "staged"
    assert plan.staged is not None
    assert plan.staged.source_expr == parse_expression("ts_mean(close, 5)")
    assert [step.func_name for step in plan.staged.steps] == ["demean", "rank"]
    assert plan.staged.steps[-1].pct is True


def test_planner_routes_corr_over_cross_section_to_materialized_ordered():
    expr, validation = validate_expression(
        "corr(rank(open), rank(close), 3)",
        build_df(),
    )
    plan = ExecutionPlanner().build_plan(expr, validation)

    assert plan.route == "materialized_ordered"
    assert plan.staged is None
    assert plan.materialized_ordered is not None
    assert plan.materialized_ordered.func_name == "corr"
    assert plan.materialized_ordered.input_exprs == (
        parse_expression("rank(open)"),
        parse_expression("rank(close)"),
    )
    assert plan.materialized_ordered.window == 3


def test_planner_keeps_plain_corr_compiled():
    expr, validation = validate_expression("corr(open, close, 3)", build_df())
    plan = ExecutionPlanner().build_plan(expr, validation)

    assert plan.route == "compiled"
    assert plan.materialized_ordered is None


@pytest.mark.parametrize("func_name", ["argmax", "argmin"])
def test_planner_routes_plain_positional_root_to_positional_ordered(func_name: str):
    expr, validation = validate_expression(f"{func_name}(close, 20)", build_df())
    plan = ExecutionPlanner().build_plan(expr, validation)

    assert plan.route == "positional_ordered"
    assert plan.materialized_ordered is None


@pytest.mark.parametrize("expr_text, func_name, window", [
    ("ts_mean(rank(close), 3)", "ts_mean", 3),
    ("ts_std(rank(close), 3)", "ts_std", 3),
    ("ts_min(rank(close), 3)", "ts_min", 3),
    ("ts_max(rank(close), 3)", "ts_max", 3),
    ("ts_median(rank(close), 3)", "ts_median", 3),
    ("ts_sum(rank(close), 3)", "ts_sum", 3),
    ("sum(rank(close), 3)", "ts_sum", 3),
    ("skew(rank(close), 3)", "skew", 3),
    ("kurt(rank(close), 4)", "kurt", 4),
])
def test_planner_routes_single_input_ordered_over_cross_family_to_materialized_ordered(
    expr_text: str,
    func_name: str,
    window: int,
):
    expr, validation = validate_expression(expr_text, build_df())

    plan = ExecutionPlanner().build_plan(expr, validation)

    assert plan.route == "materialized_ordered"
    assert plan.materialized_ordered is not None
    assert plan.materialized_ordered.func_name == func_name
    assert plan.materialized_ordered.input_exprs == (parse_expression("rank(close)"),)
    assert plan.materialized_ordered.window == window


def test_planner_routes_argmax_over_cross_family_to_materialized_ordered():
    expr, validation = validate_expression("argmax(rank(close), 3)", build_df())

    plan = ExecutionPlanner().build_plan(expr, validation)

    assert plan.route == "materialized_ordered"
    assert plan.materialized_ordered is not None
    assert plan.materialized_ordered.func_name == "argmax"
    assert plan.materialized_ordered.input_exprs == (parse_expression("rank(close)"),)
    assert plan.materialized_ordered.window == 3


def test_planner_provides_stable_keys_for_shared_staged_chain_prefixes():
    planner = ExecutionPlanner()
    left_expr, left_validation = validate_expression(
        "rank(demean(ts_mean(close, 5)), pct=true)",
        build_df(),
    )
    right_expr, right_validation = validate_expression(
        "zscore(demean(ts_mean(close, 5)))",
        build_df(),
    )

    left_plan = planner.build_plan(left_expr, left_validation)
    right_plan = planner.build_plan(right_expr, right_validation)

    assert left_plan.staged is not None
    assert right_plan.staged is not None
    assert planner.expr_key(left_plan.staged.source_expr) == planner.expr_key(right_plan.staged.source_expr)
    assert planner.staged_step_key(left_plan.staged.steps[0]) == planner.staged_step_key(right_plan.staged.steps[0])


def test_planner_builds_batch_staged_prefix_graph():
    df = build_df()
    planner = ExecutionPlanner()
    planned_items: list[BatchPlanningItem] = []

    for output_name, text in [
        ("ranked", "rank(demean(ts_mean(close, 5)), pct=true)"),
        ("scored", "zscore(demean(ts_mean(close, 5)))"),
        ("lagged", "delay(close, 1)"),
        ("segmented", "seg_mean(close, 2)"),
    ]:
        expr, validation = validate_expression(text, df)
        planned_items.append(
            BatchPlanningItem(
                output_name=output_name,
                expr=expr,
                validation=validation,
                plan=planner.build_plan(expr, validation),
            )
        )

    batch_plan = planner.build_batch_plan(planned_items)

    assert [item.output_name for item in batch_plan.compiled_items] == ["lagged"]
    assert [item.output_name for item in batch_plan.segmented_items] == ["segmented"]
    assert [item.output_name for item in batch_plan.staged_items] == ["ranked", "scored"]
    assert len(batch_plan.staged_sources) == 1
    assert batch_plan.staged_sources[0].expr == parse_expression("ts_mean(close, 5)")
    assert batch_plan.staged_sources[0].consumer_outputs == ("ranked", "scored")
    assert len(batch_plan.staged_prefix_nodes) == 3
    assert len(batch_plan.staged_nodes) == 4
    assert [node.kind for node in batch_plan.staged_nodes] == ["source", "prefix", "prefix", "prefix"]
    assert batch_plan.staged_nodes[0].expr == parse_expression("ts_mean(close, 5)")
    assert batch_plan.staged_nodes[1].depends_on_cache_key == batch_plan.staged_nodes[0].cache_key
    assert batch_plan.staged_nodes[2].depends_on_cache_key == batch_plan.staged_nodes[1].cache_key
    assert batch_plan.staged_nodes[3].depends_on_cache_key == batch_plan.staged_nodes[1].cache_key
    assert [binding.output_name for binding in batch_plan.staged_output_bindings] == ["ranked", "scored"]

    shared_prefix = batch_plan.staged_prefix_nodes[0]
    assert [step.func_name for step in shared_prefix.steps] == ["demean"]
    assert shared_prefix.consumer_outputs == ("ranked", "scored")

    leaf_names = {
        tuple(step.func_name for step in node.steps): node.consumer_outputs
        for node in batch_plan.staged_prefix_nodes[1:]
    }
    assert leaf_names[("demean", "rank")] == ("ranked",)
    assert leaf_names[("demean", "zscore")] == ("scored",)
    assert batch_plan.staged_output_bindings[0].cache_key == batch_plan.staged_nodes[2].cache_key
    assert batch_plan.staged_output_bindings[1].cache_key == batch_plan.staged_nodes[3].cache_key


def test_planner_builds_batch_plan_for_materialized_ordered_items():
    df = build_df()
    planner = ExecutionPlanner()
    planned_items: list[BatchPlanningItem] = []

    for output_name, text in [
        ("corr_ranked", "corr(rank(open), rank(close), 3)"),
        ("lagged", "delay(close, 1)"),
    ]:
        expr, validation = validate_expression(text, df)
        planned_items.append(
            BatchPlanningItem(
                output_name=output_name,
                expr=expr,
                validation=validation,
                plan=planner.build_plan(expr, validation),
            )
        )

    batch_plan = planner.build_batch_plan(planned_items)

    assert [item.output_name for item in batch_plan.compiled_items] == ["lagged"]
    assert [item.output_name for item in batch_plan.materialized_ordered_items] == ["corr_ranked"]
    assert not batch_plan.positional_items
    assert not batch_plan.segmented_items
    assert not batch_plan.staged_items


def test_planner_builds_batch_plan_for_positional_items():
    df = build_df()
    planner = ExecutionPlanner()
    planned_items: list[BatchPlanningItem] = []

    for output_name, text in [
        ("argmaxed", "argmax(close, 20)"),
        ("lagged", "delay(close, 1)"),
    ]:
        expr, validation = validate_expression(text, df)
        planned_items.append(
            BatchPlanningItem(
                output_name=output_name,
                expr=expr,
                validation=validation,
                plan=planner.build_plan(expr, validation),
            )
        )

    batch_plan = planner.build_batch_plan(planned_items)

    assert [item.output_name for item in batch_plan.compiled_items] == ["lagged"]
    assert [item.output_name for item in batch_plan.positional_items] == ["argmaxed"]
    assert not batch_plan.segmented_items
    assert not batch_plan.staged_items
    assert not batch_plan.materialized_ordered_items
