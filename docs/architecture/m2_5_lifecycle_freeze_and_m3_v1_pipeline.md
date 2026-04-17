# M2.5 Lifecycle Freeze And M3.v1 Pipeline

## Goal

The memory optimization path now has an automatic validation gate before any new materialization work proceeds:

```text
M2.5 freeze -> M3.v1 materialization discipline -> automatic score gate
```

The purpose is to stop lifecycle expansion from drifting and to make the next phase optimize fewer created columns, not merely drop columns after the fact.

## M2.5 Freeze Runner

Runner:

```text
examples/benchmark_m2_5_lifecycle_freeze.py
```

It runs two validation groups.

### Value Confirmation

Each workload is run in three modes:

```text
off
first_wave
second_wave_nested
```

Mode mapping:

| mode | node lifecycle | helper lifecycle |
| --- | --- | --- |
| `off` | `off` | `off` |
| `first_wave` | `first_wave` | `first_wave` |
| `second_wave_nested` | `first_wave` | `second_wave_nested` |

Measured fields:

- `sec`
- `peak_live_bytes`
- `helper_bytes`
- `frame_width`
- `nested_helper_dropped_count`
- `helper_dropped_count`
- helper/nested miss counts

### Rejection Audit

The runner validates these out-of-scope patterns:

| pattern | expected |
| --- | --- |
| `shared_inner` | miss |
| `non_helper_downstream` | miss |
| `output_pinned` | miss |
| `native_heavy` | miss |
| `multi_child` | miss |

Each rejection must satisfy:

```text
nested_helper_dropped_count == 0
nested_helper_drop_missed_count >= 1
trace contains a standardized reason
```

Standardized reasons:

```text
not_nested
unsupported_shape
has_blocker
output_pinned
native_pinned
non_helper_consumer
children_not_ended
safe_step_mismatch
not_in_frame
live_consumer_detected
already_dropped
mode_disabled
```

## Automatic Decision

The runner writes:

```text
summary.json
decision.yaml
m2_5_lifecycle_freeze_report.md
```

Decision shape:

```yaml
lifecycle_status:
  first_wave_stable: true
  second_wave_nested_v1: true
  rejection_audit_complete: true
  regression_detected: false
  safe_to_freeze: true

lifecycle_value:
  peak_memory_reduction: X
  performance_delta: X
  effective: true
  second_wave_decision: KEEP
```

Decision rules:

```text
effective = nested_helper_dropped_count > 0

KEEP if peak_memory_reduction >= 5%
KEEP if peak_memory_reduction >= 2% and sec_increase <= 5%
otherwise LOW_PRIORITY

safe_to_freeze =
    no result regression
    and rejection audit passes
    and off/first_wave remain valid
```

## Full-Data Result

Artifact:

```text
benchmarks/m2_5_lifecycle_freeze_full
```

Decision:

```yaml
lifecycle_status:
  first_wave_stable: true
  second_wave_nested_v1: true
  rejection_audit_complete: true
  regression_detected: false
  safe_to_freeze: true
lifecycle_value:
  peak_memory_reduction: 100.0
  performance_delta: -1.784
  effective: true
  second_wave_decision: KEEP
```

Value confirmation on `data.parquet` full data (`29,048,679` rows):

| workload | mode | sec | helper bytes | frame width | nested dropped |
| --- | --- | ---: | ---: | ---: | ---: |
| `repeated_heavy` | `off` | 8.804452 | 232,389,432 | 11 | 0 |
| `repeated_heavy` | `first_wave` | 9.691438 | 0 | 10 | 0 |
| `repeated_heavy` | `second_wave_nested` | 10.103838 | 0 | 10 | 0 |
| `multi_shared_nodes` | `off` | 12.332148 | 464,778,864 | 12 | 0 |
| `multi_shared_nodes` | `first_wave` | 11.520097 | 0 | 10 | 0 |
| `multi_shared_nodes` | `second_wave_nested` | 10.284009 | 0 | 10 | 0 |
| `partial_reuse` | `off` | 11.396046 | 232,389,432 | 12 | 0 |
| `partial_reuse` | `first_wave` | 10.693783 | 0 | 11 | 0 |
| `partial_reuse` | `second_wave_nested` | 10.321631 | 0 | 11 | 0 |
| `pure_nested_chain` | `off` | 10.820073 | 464,778,864 | 12 | 0 |
| `pure_nested_chain` | `first_wave` | 10.137857 | 464,778,864 | 12 | 0 |
| `pure_nested_chain` | `second_wave_nested` | 9.956977 | 0 | 10 | 2 |

Rejection audit:

| case | passed | dropped | missed | reasons |
| --- | --- | ---: | ---: | --- |
| `shared_inner` | true | 0 | 1 | `not_nested` |
| `non_helper_downstream` | true | 0 | 1 | `not_nested` |
| `output_pinned` | true | 0 | 2 | `has_blocker,output_pinned` |
| `native_heavy` | true | 0 | 1 | `native_pinned` |
| `multi_child` | true | 0 | 3 | `not_nested,unsupported_shape` |

Smoke artifact retained:

```text
benchmarks/m2_5_lifecycle_freeze_smoke
```

## M3.v1 Score Gate

M3.v1 optimizations must be scored before acceptance:

```text
score =
    0.5 * memory_reduction
  + 0.3 * frame_width_reduction
  - 0.2 * time_increase
```

Acceptance rule:

```text
ACCEPT iff score > 0
```

This gate is intentionally simple. It is a rollback trigger, not a full cost model.

## M3.v1 Scope

M3.v1 may evaluate:

- delayed output attach
- helper materialization tightening
- frame width discipline

M3.v1 must not:

- change M1 profiling semantics
- change `first_wave` behavior
- change `second_wave_nested` validated boundaries
- skip benchmark + automatic decision output

## Current Freeze Conclusion

M2 is safe to freeze at the current boundary:

- first-wave remains stable
- second-wave nested v1 remains effective for pure nested chain
- out-of-scope rejection is audited
- native-heavy remains denied
- multi-child and shared-inner remain outside the active helper drop subset

The next workstream can start M3.v1 materialization discipline behind the score gate.
