# M2.5 Lifecycle Freeze Validation

- data: `data.parquet`
- rows: `29048679`

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
  performance_delta: -1.784
  effective: true
  second_wave_decision: KEEP
```

## Value Confirmation

| workload | mode | sec | peak live bytes | helper bytes | frame width | nested dropped | helper dropped | helper misses | nested misses |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| repeated_heavy | off | 8.804452 | 232389432 | 232389432 | 11 | 0 | 0 | 0 | 1 |
| repeated_heavy | first_wave | 9.691438 | 0 | 0 | 10 | 0 | 1 | 0 | 0 |
| repeated_heavy | second_wave_nested | 10.103838 | 0 | 0 | 10 | 0 | 1 | 0 | 0 |
| multi_shared_nodes | off | 12.332148 | 464778864 | 464778864 | 12 | 0 | 0 | 0 | 2 |
| multi_shared_nodes | first_wave | 11.520097 | 0 | 0 | 10 | 0 | 2 | 0 | 0 |
| multi_shared_nodes | second_wave_nested | 10.284009 | 0 | 0 | 10 | 0 | 2 | 0 | 0 |
| partial_reuse | off | 11.396046 | 232389432 | 232389432 | 12 | 0 | 0 | 0 | 1 |
| partial_reuse | first_wave | 10.693783 | 0 | 0 | 11 | 0 | 1 | 0 | 0 |
| partial_reuse | second_wave_nested | 10.321631 | 0 | 0 | 11 | 0 | 1 | 0 | 0 |
| pure_nested_chain | off | 10.820073 | 464778864 | 464778864 | 12 | 0 | 0 | 0 | 2 |
| pure_nested_chain | first_wave | 10.137857 | 0 | 464778864 | 12 | 0 | 0 | 0 | 2 |
| pure_nested_chain | second_wave_nested | 9.956977 | 0 | 0 | 10 | 2 | 2 | 0 | 0 |

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
