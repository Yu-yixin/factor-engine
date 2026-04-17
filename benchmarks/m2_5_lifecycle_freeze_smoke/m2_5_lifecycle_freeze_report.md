# M2.5 Lifecycle Freeze Validation

- data: `data.parquet`
- rows: `1000`

## Lifecycle Status

```yaml
lifecycle_status:
  first_wave_stable: true
  second_wave_nested_v1: true
  rejection_audit_complete: true
  regression_detected: false
  safe_to_freeze: true
lifecycle_value:
  peak_memory_reduction: 100.0
  performance_delta: -12.078
  effective: true
  second_wave_decision: KEEP
```

## Value Confirmation

| workload | mode | sec | peak live bytes | helper bytes | frame width | nested dropped | helper dropped | helper misses | nested misses |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| repeated_heavy | off | 0.016406 | 8000 | 8000 | 11 | 0 | 0 | 0 | 1 |
| repeated_heavy | first_wave | 0.011507 | 0 | 0 | 10 | 0 | 1 | 0 | 0 |
| repeated_heavy | second_wave_nested | 0.011250 | 0 | 0 | 10 | 0 | 1 | 0 | 0 |
| multi_shared_nodes | off | 0.015185 | 16000 | 16000 | 12 | 0 | 0 | 0 | 2 |
| multi_shared_nodes | first_wave | 0.016829 | 0 | 0 | 10 | 0 | 2 | 0 | 0 |
| multi_shared_nodes | second_wave_nested | 0.015785 | 0 | 0 | 10 | 0 | 2 | 0 | 0 |
| partial_reuse | off | 0.015627 | 8000 | 8000 | 12 | 0 | 0 | 0 | 1 |
| partial_reuse | first_wave | 0.014747 | 0 | 0 | 11 | 0 | 1 | 0 | 0 |
| partial_reuse | second_wave_nested | 0.014500 | 0 | 0 | 11 | 0 | 1 | 0 | 0 |
| pure_nested_chain | off | 0.016226 | 16000 | 16000 | 12 | 0 | 0 | 0 | 2 |
| pure_nested_chain | first_wave | 0.015072 | 0 | 16000 | 12 | 0 | 0 | 0 | 2 |
| pure_nested_chain | second_wave_nested | 0.013252 | 0 | 0 | 10 | 2 | 2 | 0 | 0 |

## Rejection Audit

| case | expected | passed | dropped | missed | reasons |
| --- | --- | --- | ---: | ---: | --- |
| shared_inner | miss | True | 0 | 1 | `not_nested` |
| non_helper_downstream | miss | True | 0 | 1 | `not_nested` |
| output_pinned | miss | True | 0 | 2 | `has_blocker,output_pinned` |
| native_heavy | miss | True | 0 | 1 | `native_pinned` |
| multi_child | miss | True | 0 | 3 | `not_nested,unsupported_shape` |

## M3.v1 Scoring Contract

```text
score = 0.5 * memory_reduction + 0.3 * frame_width_reduction - 0.2 * time_increase
ACCEPT iff score > 0
```
