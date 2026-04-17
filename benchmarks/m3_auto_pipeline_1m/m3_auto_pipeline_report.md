# M3 Auto Optimization Pipeline

## Status

```yaml
m3_status:
  delayed_attach_executable: true
  materialization_control: executable_guarded
  frame_width_control: executable
  auto_optimization_enabled: true
  safe_to_freeze: true
  m4_structural_observability_complete: true
m3_value:
  total_memory_reduction: 2.84
  total_frame_width_reduction: 0.0
  total_time_delta: -6.612
  optimization_rounds: 6
  executable_candidates_this_round: 1
  proposal_candidates_queued: 0
```

## Candidate Evaluations

| candidate | status | kind | supported | score | accepted | memory reduction | frame reduction | time increase | recompute delta |
| --- | --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| `m4_fuse_deep_operator_chains` | `executable` | `node_fusion` | True | 2.743 | True | 2.840 | 0.000 | -6.612 | 0.000 |

## Proposal Queue

| proposal | kind | rationale |
| --- | --- | --- |

## Bridge

```yaml
triggered: false
stagnation_detected: false
bottleneck_detected: true
executable_space_exhausted: true
candidate_space_exhausted: true
```

## M4 Status

```yaml
structural_observability_complete: true
proposal_space_defined: true
first_executable_candidate: m4_cse_expand_repeated_subgraphs
high_value_candidate_classes_tested: true
no_new_positive_candidate_trend: false
safe_to_consider_freeze: true
```

## M4 Candidates

| candidate | kind | rationale |
| --- | --- | --- |
