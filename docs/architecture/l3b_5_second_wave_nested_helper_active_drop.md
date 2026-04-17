# L3B.5 Second-Wave Nested Helper Active Drop

L3B.5 introduces the first active helper-column drop beyond the original first wave. The scope is deliberately narrow: only pure nested helper chains are eligible, and the existing first-wave semantics remain unchanged.

## Capability Mode

`helper_lifecycle_mode` now accepts:

- `off`
- `first_wave`
- `second_wave_nested`

`second_wave_nested` includes the existing first-wave behavior and adds a separate nested-chain candidate path. It does not alter the first-wave allowlist.

## Supported Shape

The only new supported shape is a pure nested helper chain:

```text
h2 = f(x)
h1 = g(h2)
final uses h1
```

Both helpers must be non-native `shared_intermediate` nodes with `materialization_eligibility = materialize_for_both`, no blocker, positive structural lag, and a stable drop safe step.

The first version is intentionally stricter than "any nested-looking pair": the batch must contain exactly the two helpers that form the pure nested chain. If extra materialized helpers appear in the same nested shape, the second-wave nested path rejects the shape.

## Explicit Denylist

The second-wave nested path rejects:

- shared-inner / multi-outer shapes
- multi-parent or multi-child helper shapes
- nested shapes with more than two materialized helpers
- helpers with non-helper downstream consumers
- output-pinned or final helper dependencies
- native-heavy helpers
- any helper with a blocker
- any helper whose safe step is before its structural dependency end

Unsupported shapes are not errors. They produce a miss with a standardized reason.

## Policy Split

The policy layer is split into separate predicates:

```text
is_first_wave_helper_candidate(...)
is_second_wave_nested_candidate(...)
collect_helper_drop_candidate_kind(...)
```

This keeps first-wave behavior isolated from second-wave evolution.

## Runtime Model

The runtime still uses the same three-stage model:

```text
candidate collection
→ executor revalidation
→ batch-safe projection drop
```

Nested helper columns are not dropped immediately at logical last use. Eligibility depends on the structural dependency end and the safe step. The executor revalidates the candidate at the batch-safe boundary before projecting the frame without the helper columns.

## Trace And Summary

Nested helper trace events:

- `nested_helper_candidate`
- `nested_helper_revalidate_pass`
- `nested_helper_revalidate_fail`
- `nested_helper_dropped`
- `nested_helper_drop_missed`

Nested summary fields:

- `nested_helper_dropped_count`
- `nested_helper_drop_missed_count`
- `nested_helper_peak_live_bytes_before_drop`
- `nested_helper_peak_live_bytes_after_drop`
- `nested_helper_frame_width_before_drop`
- `nested_helper_frame_width_after_drop`
- `nested_helper_lifecycle_effective`

`nested_helper_lifecycle_effective` is true only when `helper_lifecycle_mode = second_wave_nested` and at least one nested helper is actually dropped.

## Smoke Result

Artifact:

- `benchmarks/l3b5_nested_second_wave_smoke`

Smoke workload summary:

| workload | cse | nested dropped | nested miss | helper before bytes | helper after bytes | helper frame before | helper frame after |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `nested_probe_a` | true | 2 | 0 | 16,000 | 0 | 12 | 10 |
| `nested_probe_c` | true | 0 | 1 | 8,000 | 8,000 | 11 | 11 |

Interpretation:

- `nested_probe_a` is the pure nested chain and is dropped in `second_wave_nested`.
- `nested_probe_c` is a shared-inner shape and remains outside this first nested active-drop subset; it is recorded as a nested miss for rejection audit purposes.

## Test Coverage

Positive:

- pure nested chain drops safely and preserves output semantics

Negative:

- first-wave mode still denies nested helpers
- shared-inner shape does not become a nested candidate
- non-helper downstream consumer misses
- output-pinned/final helper dependency misses

Full suite status:

```text
417 passed
```

## Current Boundary

L3B.5 is still not native-heavy lifecycle, not shared-inner lifecycle, not generalized nested DAG lifecycle, and not allocator-level memory management. It is a bounded second-wave implementation for a pure nested helper chain only.
