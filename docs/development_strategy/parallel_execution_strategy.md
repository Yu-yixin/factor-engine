# Parallel Execution Strategy

Parallelism is a throughput tool, not a license to increase residency or hide
execution paths. Future CPU parallel work must stay planner-visible and
profiling-visible.

## Current Parallel Baseline

The current engine has group-level parallelism for appropriate ordered/native
work. It has already shown that parallelism can improve time while leaving
memory pressure unsolved or even more visible. Therefore, future parallel work
must be evaluated with both compute and residency metrics.

## Safe Parallelism Layers

### Layer 1: Partition Parallelism

Preferred first layer.

Examples:

- independent `code` groups in rolling kernels;
- independent groups in native positional kernels;
- independent segments where segment state is isolated.

Acceptance requirements:

- partition boundaries are planner-visible;
- output ordering is restored deterministically;
- per-worker buffers are counted;
- peak buffer estimate is exposed.

### Layer 2: Batch-Level Parallelism

Useful when independent outputs or node groups can be computed without inflating
live helper/native buffers.

Acceptance requirements:

- planner can identify independent regions;
- result-store writes are isolated;
- live residency does not grow beyond benchmark guardrails;
- profiling reports worker count and buffer estimate.

### Layer 3: Intra-Kernel Parallelism

Highest-risk layer. It belongs mostly in native kernels.

Acceptance requirements:

- native kernel exposes internal worker count;
- scratch and output buffers are accounted;
- determinism and numerical stability are tested;
- fallback serial mode exists for debugging.

## Parallelism Anti-Patterns

Do not accept:

- parallelism hidden inside an executor special case;
- parallel map over Python objects;
- parallel execution that bypasses DAG/CSE materialization policy;
- parallelism that improves time while making native buffers opaque;
- uncontrolled expression-level parallelism without live-residency estimates.

## Evaluation Metrics

Any new parallel capability must report:

```yaml
parallel_metrics:
  parallel_enabled: true/false
  worker_count: N
  total_time_delta: ...
  compute_time_delta: ...
  peak_rss_delta: ...
  peak_frame_width_delta: ...
  native_buffer_peak_delta: ...
  result_store_peak_delta: ...
```

Parallel work is accepted only if the score improves without violating memory
or audit guardrails.

## Relationship To DAG/CSE

DAG/CSE decides what should be computed once. Parallelism decides where safe
independent work can run concurrently. Future parallel execution must consume
planner/DAG decisions rather than rediscovering dependencies inside the
executor.

In practice:

- shared nodes compute once even under parallel execution;
- materialized nodes have synchronized store writes;
- helper drop and node-store drop remain correct under worker scheduling;
- trace must remain replayable.

