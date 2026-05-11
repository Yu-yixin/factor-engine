# M3 Auto Pipeline And M4 Bridge

## Goal

M3 is an automatic optimization loop:

```text
proposal -> executable -> benchmark -> score -> accept/reject -> history
```

The loop is deliberately separate from frozen M2 lifecycle. It does not modify
first-wave lifecycle, second-wave nested lifecycle, execution routes, DSL
semantics, or M1 profiling semantics.

## Candidate Layers

M3 separates optimization ideas into two layers.

| layer | meaning | allowed actions |
| --- | --- | --- |
| proposal | an optimization idea without a runnable engine knob | record, inspect, queue |
| executable | a candidate with an explicit A/B switch | benchmark, score, accept/reject |

Proposal candidates are never scored. This prevents an unimplemented idea from
being recorded as a failed experiment, and prevents timing noise from being
accepted as a real optimization.

## First Executable Candidate

The first executable M3 candidate is delayed output attach:

```text
baseline:  output_attach_mode = materialize
candidate: output_attach_mode = finalize_select
```

`materialize` attaches output columns to the ordered working frame before
restore. `finalize_select` evaluates final output expressions into a temporary
finalize selection and avoids widening the working frame with output columns.

The candidate is exposed through:

```text
FactorEngine.evaluate_many(..., output_attach_mode="finalize_select")
```

## Proposal Queue

The M3 v1 proposal queue is now exhausted. The previous
`m3_attach_last_use` proposal has been promoted to the final executable M3 v1
candidate. No additional M3 v1 proposals are added after this point.

The second executable M3 candidate is dependency-driven frame projection:

```text
baseline:  frame_projection_mode = off
candidate: frame_projection_mode = dependency_driven
```

`dependency_driven` performs one conservative projection before output
finalization. It keeps only the row index plus columns referenced by final output
expressions. If expression root discovery is unavailable, it keeps the full
frame.

The third executable M3 candidate is guarded materialization threshold:

```text
baseline:  materialization_threshold_mode = reuse_ge_2
candidate: materialization_threshold_mode = reuse_ge_3_guarded
guardrail: recomputation_guardrail_max_expansion = 0
```

The threshold change is protected by a recomputation guardrail. A helper can be
skipped only when the estimated repeated-heavy recomputation expansion is within
the configured limit. The benchmark reports `recompute delta` separately from
memory/frame/time score so threshold experiments cannot hide extra compute.

Only one proposal is promoted into an executable candidate per round.

The fourth and final executable M3 v1 candidate is last-use output attach:

```text
baseline:  output_attach_mode = materialize
candidate: output_attach_mode = last_use_select
safe step: final output last-use / restore-assemble boundary
```

In the current ordered-batch execution model, final output last-use is the
restore/final-assemble boundary. `last_use_select` therefore stays conservative:
it exposes the last-use attach idea as an A/B switch without changing routes,
DSL semantics, or frozen M2 lifecycle behavior.

## Runner

Runner:

```text
benchmarks/scripts/benchmark_m3_auto_pipeline.py
```

## M4 Structural Bridge

Once M3 v1 has no remaining executable candidates and no proposal queue, the
runner builds an explicit structural bottleneck report before any M4 proposal is
allowed to become executable.

Artifacts:

```text
structural_bottleneck_report.json
structural_bottleneck_report.md
```

The report contains four ledgers:

| ledger | purpose |
| --- | --- |
| repeated_subgraphs | repeated canonical identities, occurrence count, helper bytes, compute weight |
| deep_chains | dependency chains, depth, materialized hops, transient hops, chain pressure |
| wide_fanout_nodes | fan-out degree, child spread, estimated fan-out pressure |
| heavy_paths | memory weight, time weight, combined pressure score |

M4 proposal priority is locked to the low-risk global order:

```text
m4_cse_expand_repeated_subgraphs
-> m4_fuse_deep_operator_chains
-> m4_eliminate_materialized_intermediates
-> m4_batch_wide_fanout_nodes
-> m4_rewrite_heavy_execution_path
```

The report may still mark a different dominant bottleneck class, but it does not
automatically reorder the first executable candidate. M4 keeps the same
proposal/executable discipline as M3: proposals are queued and explained; only a
candidate with an independent A/B knob can be benchmarked and scored.

## M4.2 First Executable: Expanded CSE

The first M4 executable candidate is:

```text
m4_cse_expand_repeated_subgraphs
```

Knob:

```text
planner_cse_mode = baseline | expanded_repeated_family
```

Selected family:

```yaml
m4_2_selected_family:
  family_name: rolling_neutral_add_input
  selection_reason:
    - high_occurrence
    - high_helper_bytes
    - localizable
    - auditable
```

Baseline identity rule:

```text
rolling call identity keeps the full first-argument subtree
```

Expanded identity rule:

```text
for ts_rank/ts_mean only:
  first argument var + 0 or 0 + var canonicalizes to var
```

Why baseline misses this family:

```text
neutral pointwise add creates a distinct child identity, even though the numeric
value fed into the rolling operator is equivalent.
```

Why expanded can safely merge it:

```text
x + 0 and 0 + x are value-preserving for the numeric rolling inputs in this
selected family. The rule is deliberately limited to ts_rank/ts_mean and does
not apply to arbitrary subgraphs.
```

M4.2 outputs:

```text
m4_cse_audit.json
m4_cse_candidate_report.md
m4_2_cse_decision.md
m4_history.json
```

The runner uses M2-frozen execution settings:

```text
dag_cse = true
lifecycle_mode = first_wave
helper_lifecycle_mode = second_wave_nested
```

It evaluates only executable candidates. Proposals are written to
`proposal_queue` in `summary.json` and the markdown report.

## Benchmark Set

Each executable candidate runs the same workload set:

```text
synthetic_small
synthetic_large
real_workload
pure_nested_chain
mixed_pattern
```

The runner records:

```text
summary.json
optimization_history.json
m3_auto_pipeline_report.md
```

## Scoring

All M3 and future M4 executable candidates use one score:

```text
score =
    0.5 * memory_reduction
  + 0.3 * frame_width_reduction
  - 0.2 * time_increase
```

Decision:

```text
ACCEPT iff score > 0
REJECT iff score <= 0
```

Accepted and rejected executable candidates are both written to history.
Proposal candidates are not written as scored history rows.

## Stagnation And Bridge

M3 can bridge to M4 only after executable M3 space has stopped paying.

Bridge trigger:

```text
last 3 executable candidates have score <= 0
AND memory_improvement < 2%
AND frame_improvement < 2%
AND executable space is exhausted
AND proposal queue is empty
```

When triggered, the runner analyzes profiling output and generates a bottleneck
report:

```yaml
bottleneck_report:
  high_memory_nodes: [...]
  repeated_patterns: [...]
  deep_chains: [...]
  wide_nodes: [...]
  compute_hotspots: [...]
```

Then it emits M4 proposal candidates:

| kind | candidate |
| --- | --- |
| CSE expansion | `m4_cse_expand_repeated_subgraphs` |
| execution route rewrite | `m4_rewrite_heavy_execution_path` |
| node fusion | `m4_fuse_deep_operator_chains` |
| batching / segmentation | `m4_batch_wide_fanout_nodes` |
| materialization elimination | `m4_eliminate_materialized_intermediates` |

M4 candidates start as proposals. They must later be promoted into executable
candidates with a real knob before they can be scored.

## M4 Executable Results

Artifact:

```text
benchmarks/m3_auto_pipeline_1m
```

M4.2 CSE expansion:

```yaml
candidate: m4_cse_expand_repeated_subgraphs
selected_family: rolling_neutral_add_input
decision: ACCEPT
score: 1.556
matched_groups: 2
reused_groups: 2
estimated_helper_bytes_saved: 16000000
guardrails:
  correctness: true
  audit_explainability: true
  isolation: true
```

M4.3 unary-chain fusion:

```yaml
candidate: m4_fuse_deep_operator_chains
selected_family: rolling_unary_chain_ts_mean_into_ts_rank
decision: ACCEPT
score: 2.743
memory_reduction: 2.840
frame_width_reduction: 0.000
time_increase: -6.612
matched_chains: 2
nodes_reduced: 2
estimated_intermediate_eliminated: 16000000
guardrails:
  correctness: true
  audit_explainability: true
  isolation: true
```

M4 freeze readiness:

```yaml
accepted_candidates:
  - m4_cse_expand_repeated_subgraphs
  - m4_fuse_deep_operator_chains
rejected_candidates: []
dominant_bottleneck_class: wide_fanout
required_candidate_classes_tested: true
structure_is_primary_bottleneck: true
optimization_space_exhausted: true
freeze_path: strong_success
safe_to_consider_freeze: true
safe_to_freeze: true
m4_frozen: true
```

The M4 conclusion is deliberately bounded: the structure layer has proven value
through two accepted local candidates. Further structural work should require a
new freeze review rather than continuing the open-ended M4 queue.

## M4 Freeze Decision

M4 is frozen under the strong-success path.

Strategy conclusion:

> M4 has demonstrated repeatable, auditable structural gains through localized
> CSE expansion and minimal unary-chain fusion. Current evidence is sufficient
> to freeze M4 under the strong-success path. Remaining structural classes,
> especially wide-fanout batching and heavy-path rewrite, are intentionally
> deferred to avoid over-expansion beyond the demonstrated value boundary.

Final value summary:

1. M3 closed because attach/projection/materialization-threshold candidates did
   not show durable positive value at the 1M scale.
2. M4 succeeded because two localized structural candidates produced positive,
   benchmarked, guardrailed results.
3. The remaining dominant residual class is `wide_fanout`.
4. M4 stops now because the strong-success freeze path is satisfied; continuing
   into elimination, batching, or heavy-path rewrite would expand risk faster
   than it improves certainty.

Current-cycle freeze rules:

- no new M4 proposal is introduced in the current cycle
- no materialized-intermediate elimination in the current freeze window
- no wide-fanout batching in the current freeze window
- no heavy-path rewrite in the current freeze window
- accepted knobs are retained:
  - `planner_cse_mode=expanded_repeated_family`
  - `fusion_mode=unary_chain_fusion`
- untested high-risk structural classes remain deferred, not failed work

M4 may only be reopened when at least one of these entry conditions is met:

- a new workload shows materially larger wide-fanout pressure than the freeze
  workload
- either accepted candidate becomes unstable on real data
- a refreshed structural report identifies a new dominant family
- a deliberate new M4+ cycle is opened with its own proposal/executable/score
  contract

`wide_fanout` remains the dominant residual bottleneck class, but that is not an
authorization to continue batching work inside this frozen M4 cycle.

## Boundary

M2 remains frozen:

- no first-wave change
- no second-wave expansion
- no native-heavy lifecycle
- no execution route rewrite during M3

The bridge is only a candidate generator for M4. It does not implement M4
optimizations.

## Current Smoke Results

Artifact:

```text
benchmarks/m3_auto_pipeline_smoke
```

Round 1 smoke:

```yaml
candidate: m3_delayed_output_attach_finalize_select
status: executable
accepted: true
score: 2.024
memory_reduction: -0.288
frame_width_reduction: 0.0
time_increase: -10.839
bridge_triggered: false
proposal_candidates_queued: 3
```

The candidate is accepted by the shared score contract because the runtime
improvement outweighs the small smoke-level memory increase. This is a smoke
result only; larger data runs remain the authority for M3 value confirmation.

Round 2 smoke:

```yaml
candidate: m3_projection_dependency_driven
status: executable
accepted: true
score: 1.985
memory_reduction: -0.426
frame_width_reduction: 0.0
time_increase: -10.991
bridge_triggered: false
proposal_candidates_queued: 2
```

Round 3 smoke:

```yaml
candidate: m3_materialization_reuse_ge_3
status: executable
accepted: false
score: -7.199
memory_reduction: -0.561
frame_width_reduction: 0.0
time_increase: 34.591
recompute_delta: 0.0
bridge_triggered: false
proposal_candidates_queued: 1
```

## Current 1M Results

Artifact:

```text
benchmarks/m3_auto_pipeline_1m
```

Round 1 1M:

```yaml
candidate: m3_delayed_output_attach_finalize_select
status: executable
accepted: false
score: -1.781
memory_reduction: -2.510
frame_width_reduction: 0.0
time_increase: 2.631
bridge_triggered: false
proposal_candidates_queued: 3
```

The 1M result rejects delayed output attach as a default-promoted M3
optimization. The engine knob remains available for future experiments, but the
candidate is not promoted by the scoring contract.

Second 1M round:

```yaml
candidate: m3_projection_dependency_driven
status: executable
accepted: false
score: -0.649
memory_reduction: -1.222
frame_width_reduction: 0.0
time_increase: 0.193
bridge_triggered: false
proposal_candidates_queued: 2
```

The projection candidate is rejected by the same score contract. It remains an
experimental knob and does not change default behavior.

Third 1M round:

```yaml
candidate: m3_materialization_reuse_ge_3
status: executable
accepted: false
score: -2.240
memory_reduction: -0.003
frame_width_reduction: 0.0
time_increase: 11.194
recompute_delta: 0.0
bridge_triggered: false
proposal_candidates_queued: 1
```

The recomputation guardrail holds: no recomputation expansion is observed. The
candidate is still rejected because runtime regresses and memory/frame width do
not improve.
