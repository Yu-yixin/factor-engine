from __future__ import annotations

from types import SimpleNamespace

from factor_engine.execution_materialization import (
    apply_dag_materialization_runtime_summary,
    build_materialization_guardrail_summary,
    materialized_consumer_count,
    recomputation_guardrail_candidates,
)


def _node(
    *,
    occurrence_count=1,
    consumers=(),
    output_names=(),
    materialize=True,
    default_materialize=True,
    recomputation_expansion_if_inline=0,
    recomputation_guardrail_pass=False,
):
    return SimpleNamespace(
        occurrence_count=occurrence_count,
        consumers=consumers,
        output_names=output_names,
        materialize=materialize,
        default_materialize=default_materialize,
        recomputation_expansion_if_inline=recomputation_expansion_if_inline,
        recomputation_guardrail_pass=recomputation_guardrail_pass,
    )


def test_materialized_consumer_count_matches_existing_policy():
    node = _node(occurrence_count=2, consumers=("a", "b", "c"), output_names=("out",))

    assert materialized_consumer_count(node) == 4


def test_recomputation_guardrail_candidates_filter_default_materialized_expansion():
    allowed = _node(recomputation_expansion_if_inline=3, recomputation_guardrail_pass=True)
    ignored_no_expansion = _node(recomputation_expansion_if_inline=0)
    ignored_non_default = _node(default_materialize=False, recomputation_expansion_if_inline=2)

    assert recomputation_guardrail_candidates(
        [allowed, ignored_no_expansion, ignored_non_default]
    ) == [allowed]


def test_guardrail_summary_preserves_candidate_and_delta_counts():
    summary = build_materialization_guardrail_summary(
        [
            _node(occurrence_count=3, recomputation_expansion_if_inline=2, recomputation_guardrail_pass=True),
            _node(
                occurrence_count=4,
                materialize=False,
                recomputation_expansion_if_inline=5,
                recomputation_guardrail_pass=False,
            ),
        ]
    )

    assert summary.candidate_count == 2
    assert summary.allowed_count == 1
    assert summary.blocked_count == 1
    assert summary.expansion_estimate == 2
    assert summary.expansion_actual_delta == 5
    assert summary.estimated_unshared_compute_calls == 3


def test_apply_dag_materialization_runtime_summary_updates_runtime_fields():
    runtime = SimpleNamespace()
    dag = SimpleNamespace(
        ast_node_count=10,
        dag_node_count=4,
        deduplicated_node_count=1,
        shared_node_count=2,
        materialized_node_count=1,
        expensive_node_count=1,
        nodes=[
            _node(occurrence_count=3, recomputation_expansion_if_inline=2, recomputation_guardrail_pass=True),
        ],
    )

    apply_dag_materialization_runtime_summary(runtime, dag)

    assert runtime.ast_node_count == 10
    assert runtime.dag_node_count == 4
    assert runtime.recomputation_guardrail_candidate_count == 1
    assert runtime.recomputation_guardrail_allowed_count == 1
    assert runtime.estimated_unshared_compute_calls == 3
