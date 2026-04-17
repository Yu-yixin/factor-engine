# Native Runtime Strategy

Future engine development should move expensive operator families toward a
Rust/C++ or backend-native runtime. The goal is not "native for speed" in the
abstract. The goal is native execution that is planner-visible, identity-stable,
memory-accounted, and lifecycle-auditable.

## Current Native Baseline

The engine already has native positional execution and low-copy bridge work for
the accepted positional path. That work establishes important principles:

- native kernels must have explicit input ordering and partitioning;
- native output buffers must be profiled;
- native buffer attach/release must be visible;
- Python hot paths should not own the main compute loop;
- native behavior must be testable against reference semantics.

## Native Kernel Acceptance Criteria

A new native kernel family is acceptable only if all criteria are met.

| criterion | requirement |
| --- | --- |
| semantic contract | Function semantics, null behavior, tie-breaks, window bounds, and output type are documented. |
| route contract | Planner route or route reuse is explicit; no executor-only hidden path. |
| identity contract | DAG/CSE identity includes all semantic options and route-sensitive properties. |
| memory contract | Input buffers, scratch buffers, output buffers, and ownership transfer are described. |
| lifecycle contract | Buffer and helper lifetime can be observed before active release is attempted. |
| fallback contract | Python fallback is either absent or explicitly designated as test/reference only. |
| benchmark contract | Native path has correctness, profiling, and performance comparison tests. |

## Kernel Family Shape

Native kernels should be grouped by state shape, not by individual function
name. This prevents one-off native kernels from becoming maintenance debt.

### Rolling Reducer Kernel

Examples:

- `product`
- `geometric_mean`
- compound return reducers

Required state:

- per-partition rolling state;
- fixed-size or bounded reducer state;
- null counter / valid counter;
- current output slot.

### Weighted Rolling Kernel

Examples:

- `decay_linear`
- weighted mean / weighted rank
- EWM variants

Required state:

- weight specification or decay parameter;
- window/state buffer;
- normalization strategy;
- scratch allocation model.

### Order-Statistic Kernel

Examples:

- rolling quantile;
- percentile rank;
- rolling winsorize.

Required state:

- exact or approximate selection strategy;
- scratch buffer ownership;
- deterministic null and tie behavior.

### Rolling Model Kernel

Examples:

- rolling beta;
- rolling OLS;
- rolling residual.

Required state:

- multi-input window state;
- matrix/vector scratch;
- numeric stability policy;
- optional multi-output schema.

## Native ABI Principles

The native ABI should expose enough metadata for profiling and lifecycle:

```text
kernel_id
input_column_count
partition_count
row_count
state_bytes_estimate
scratch_bytes_estimate
output_bytes_estimate
parallel_worker_count
created_step
attached_step
released_step
```

The ABI should not hide large temporary allocations from the Python-side
profiler. If the engine cannot estimate native residency, active lifecycle work
on that family should remain blocked.

## CPU Parallelism And Native Kernels

Native kernels should be parallelized by planner-visible partitions first:

1. group/code partition parallelism;
2. independent expression batch parallelism only when memory residency is safe;
3. intra-kernel parallelism only after buffer accounting exists.

Parallel speedup is not enough. A native kernel is not acceptable if it improves
CPU time while making peak residency or buffer lifetime opaque.

## Reference Implementation Rule

Reference implementations are allowed for tests and smoke comparisons, but they
must not become production paths for accepted operators if they rely on:

- Python row loops;
- Python window callbacks;
- `map_elements`;
- `map_groups`;
- NumPy/list round trips for core execution.

If no native or backend-vectorized implementation exists, the operator stays in
the roadmap.

