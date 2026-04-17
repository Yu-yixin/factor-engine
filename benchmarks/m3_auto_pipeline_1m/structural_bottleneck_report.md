# M4 Structural Bottleneck Report

## Summary

- dominant bottleneck class: `wide_fanout`
- structural observability complete: `True`
- proposal priority: `m4_cse_expand_repeated_subgraphs, m4_fuse_deep_operator_chains, m4_eliminate_materialized_intermediates, m4_batch_wide_fanout_nodes, m4_rewrite_heavy_execution_path`

## Repeated Subgraphs

| signature | occurrences | nodes | helper bytes | compute weight |
| --- | ---: | --- | ---: | ---: |
| `('call', 'ts_rank', ('function_context', 'time_series', 'rolling', True, 'time', True, 'ths_code` | 8 | `n3,n5` | 64000000 | 447.923 |
| `('call', 'ts_mean', ('function_context', 'time_series', 'rolling', True, 'time', True, 'ths_code` | 6 | `n3,n7` | 48000000 | 149.623 |
| `('call', 'ts_rank', ('function_context', 'time_series', 'rolling', True, 'time', True, 'ths_code` | 6 | `n4,n6` | 48000000 | 500.442 |
| `('call', 'ts_rank', ('function_context', 'time_series', 'rolling', True, 'time', True, 'ths_code` | 2 | `n6` | 16000000 | 90.320 |

## Deep Chains

| chain | depth | materialized hops | transient hops | pressure |
| --- | ---: | ---: | ---: | ---: |
| `n5->n6` | 2 | 2 | 0 | 32000000 |
| `n1->n3->n4` | 3 | 2 | 1 | 32000000 |
| `n1->n3->n6` | 3 | 2 | 1 | 32000000 |
| `n1->n3->n5` | 3 | 2 | 1 | 32000000 |
| `n1->n3->n7` | 3 | 2 | 1 | 32000000 |

## Wide Fan-Out Nodes

| node | occurrences | fanout | children | pressure |
| --- | ---: | ---: | --- | ---: |
| `n3` | 8 | 2 | `` | 256000000 |
| `n3` | 6 | 3 | `` | 224000000 |
| `n4` | 6 | 2 | `__dag_node` | 192000000 |
| `n6` | 2 | 2 | `` | 64000000 |

## Heavy Paths

| path | memory weight | time weight | pressure score |
| --- | ---: | ---: | ---: |
| `n1->n3->n6` | 16000000 | 139.824 | 157.824 |
| `n1->n3->n4` | 16000000 | 112.984 | 130.984 |
| `n1->n3->n4` | 16000000 | 105.519 | 123.519 |
| `n1->n3` | 16000000 | 63.807 | 81.807 |
| `n1->n3` | 16000000 | 62.307 | 80.307 |
