# Stage Lifecycle Benchmark Report

- run_id: `d3c3451f62ed41159394d610de8ff255`
- benchmark: `m2_5_pure_nested_chain_off`
- dataset: `data.parquet`
- rows: `1000`
- groups: `1000`
- expressions: `1`
- total_time_sec: `0.016226`
- peak_rss_mb: `68.99`

## Batch Details

| batch | route | exprs | stages | dropped | peak cols | peak stage cols | peak output cols | final cols | alive stages | alive outputs | native buffer peak bytes | peak rss mb |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d3c3451f62ed41159394d610de8ff255:batch:1` | `ordered_batch` | 1 | 2 | 0 | 12 | 2 | 0 | 11 | 2 | 1 | 0 | 68.99 |

## DAG / CSE

| batch | ast nodes | dag nodes | dedup nodes | shared nodes | materialized nodes | expensive nodes | est unshared computes | total computes | node-store computes | compiled heavy occurrences | store reads | reuse consumers | hit rate | node-store compute ms | compiled eval ms | restore assemble ms | append ms | finalize ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d3c3451f62ed41159394d610de8ff255:batch:1` | 11 | 5 | 4 | 4 | 2 | 2 | 4 | 2 | 2 | 0 | 3 | 2 | 0.600 | 2.191 | 0.202 | 0.480 | 0.078 | 0.559 |

## L1 Lifecycle Observability

| batch | mode | effective | candidates | releasable | peak live nodes | before-drop bytes | after-drop bytes | dropped | drop misses | drop order | nested order | partial safety | batch end step | avg structural lag | max structural lag | avg finalize lag | max finalize lag | bytes-step savings | L2 first-wave candidates |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `d3c3451f62ed41159394d610de8ff255:batch:1` | `off` | False | 2 | 2 | 2 | 16000 | 16000 | 0 | 0 | `` | True | True | 10 | 5.000 | 6 | 4.000 | 5 | 80000 | 2 |

## L3B Helper Column Lifecycle Observability

| batch | mode | effective | helper columns | releasable | blocked | helper live bytes | before-drop bytes | after-drop bytes | dropped | misses | frame width before | frame width after | drop delay avg | potential bytes-step savings | blocker reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `d3c3451f62ed41159394d610de8ff255:batch:1` | `off` | False | 2 | 2 | 0 | 16000 | 16000 | 16000 | 0 | 0 | 12 | 12 | 0.000 | 64000 | `` |

## Top Releasable Nodes By Bytes-Step Savings

| node | batch | class | reason | eligibility | bytes | structural lag | bytes-step savings |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `n3` | `d3c3451f62ed41159394d610de8ff255:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000 | 6 | 48000 |
| `n4` | `d3c3451f62ed41159394d610de8ff255:batch:1` | `shared_heavy` | `shared_reuse_and_path_normalization` | `materialize_for_both` | 8000 | 4 | 32000 |

## Drop Candidates

| stage | kind | column | consumers | alive at end | dropped |
| --- | --- | --- | ---: | --- | --- |
| `d3c3451f62ed41159394d610de8ff255:batch:1:stage:1` | `dag_shared_intermediate` | `__dag_node` | 0 | True | False |
| `d3c3451f62ed41159394d610de8ff255:batch:1:stage:2` | `dag_shared_intermediate` | `___dag_node` | 0 | True | False |

## Planned Lifecycle

| batch | planned reusable | avoided recompute | recomputed | late alive |
| --- | ---: | ---: | ---: | ---: |
| `d3c3451f62ed41159394d610de8ff255:batch:1` | 0 | 0 | 0 | 0 |

## Output Retention

| output | source | created | attached | last required | late alive | working-frame attach |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pure_nested_chain` | `None` | 1 | 4 | 4 | False | False |
