# M4 Structural Bottleneck Report

## Summary

- dominant bottleneck class: `wide_fanout`
- structural observability complete: `True`
- proposal priority: `m4_cse_expand_repeated_subgraphs, m4_fuse_deep_operator_chains, m4_eliminate_materialized_intermediates, m4_batch_wide_fanout_nodes, m4_rewrite_heavy_execution_path`

## Repeated Subgraphs

| signature | occurrences | nodes | helper bytes | compute weight |
| --- | ---: | --- | ---: | ---: |
| `('call', 'ts_rank', ('function_context', 'time_series', 'rolling', True, 'time', True, 'ths_code` | 8 | `n3,n5` | 64000 | 8.570 |
| `('call', 'ts_mean', ('function_context', 'time_series', 'rolling', True, 'time', True, 'ths_code` | 6 | `n3,n7` | 48000 | 5.421 |
| `('call', 'ts_rank', ('function_context', 'time_series', 'rolling', True, 'time', True, 'ths_code` | 6 | `n4,n6` | 48000 | 8.431 |
| `('call', 'ts_rank', ('function_context', 'time_series', 'rolling', True, 'time', True, 'ths_code` | 2 | `n6` | 16000 | 1.893 |

## Deep Chains

| chain | depth | materialized hops | transient hops | pressure |
| --- | ---: | ---: | ---: | ---: |
| `n5->n6` | 2 | 2 | 0 | 32000 |
| `n1->n3->n4` | 3 | 2 | 1 | 32000 |
| `n1->n3->n6` | 3 | 2 | 1 | 32000 |
| `n1->n3->n5` | 3 | 2 | 1 | 32000 |
| `n1->n3->n7` | 3 | 2 | 1 | 32000 |

## Wide Fan-Out Nodes

| node | occurrences | fanout | children | pressure |
| --- | ---: | ---: | --- | ---: |
| `n3` | 8 | 2 | `` | 256000 |
| `n3` | 6 | 3 | `` | 224000 |
| `n4` | 6 | 2 | `__dag_node` | 192000 |
| `n6` | 2 | 2 | `` | 64000 |

## Heavy Paths

| path | memory weight | time weight | pressure score |
| --- | ---: | ---: | ---: |
| `n1->n3->n4` | 16000 | 2.956 | 4.972 |
| `n1->n3` | 16000 | 0.911 | 3.927 |
| `n1->n3` | 16000 | 0.795 | 3.811 |
| `n1->n3->n4` | 16000 | 1.793 | 3.809 |
| `n1->n3` | 16000 | 1.525 | 3.541 |
