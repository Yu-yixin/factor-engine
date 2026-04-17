# Stage Lifecycle V1/V2

## Scope

This lifecycle work is intentionally limited to explicit stages inside ordered batch execution.

It does not introduce global DAG/CSE, compiled-expression subtree extraction, route changes, positional-kernel redesign, or native kernels.

## Column Classes

- Base columns are original input columns plus ordered-shell helpers such as `__row_idx`. They are never lifecycle-managed stages.
- Stage columns are explicit intermediate columns created inside ordered batch execution. They are registered, consumed, profiled, and eligible for conservative drop.
- Output columns are user-requested result columns. They must survive until output restoration is complete and are not dropped as ordinary stages.
- Transient buffers are Python/kernel-local objects. V2 does not manage them as working-frame columns.

## V1 Profiling

`FactorEngine.evaluate_many(..., profiling=True, profile_output_dir=...)` records ordered-batch lifecycle data without changing execution semantics.

The profile output directory contains:

- `latest_run.json`
- `history.csv`
- `latest_batch_details.jsonl`
- `latest_stage_details.jsonl`
- `latest_stage_events.jsonl`
- `benchmark_report.md`

The event stream records:

- `stage_created`
- `stage_consumed`
- `stage_dropped` when lifecycle sweep is enabled
- `batch_end_stage_snapshot`

V1 records only explicit stages that are materialized as columns. It does not attempt to inspect implicit subtrees inside a compiled Polars expression.

## V2 Lifecycle

`FactorEngine.evaluate_many(..., lifecycle=True)` enables conservative stage sweeping inside ordered batch execution.

The stage registry tracks:

- stage identity
- stage kind
- producer route
- column name
- creation order
- consumer count estimate
- last-use order estimate
- alive/dropped status

The current V2 sweep is deliberately conservative. It sweeps after positional/materialized route items and again before ordered output restoration. This keeps frame/cache/registry state synchronized while avoiding aggressive per-consume deletion.

## Drop Conditions

A stage is eligible for drop only when:

- it is still alive
- it is not output-backed
- it is not a user output column
- its remaining consumer count is zero
- the sweep point is past observed consumption

When a stage is dropped, the working frame column is removed, matching cache entries are invalidated, registry state is marked dropped, and a `stage_dropped` event is emitted.

## Benchmark

Run:

```powershell
$env:PYTHONPATH="src;.venv\Lib\site-packages"
python examples\benchmark_stage_lifecycle.py
```

This writes:

- `benchmarks/stage_lifecycle.md`
- per-workload V1/V2 profile directories under `benchmarks/stage_lifecycle/`

The benchmark currently compares profiling-only V1 against lifecycle-enabled V2 for:

- stage accumulation workload
- long-lived stage workload

## Validation Layers

The lifecycle optimization is validated in four layers:

- Unit tests lock the `StageRegistry` state machine: register, consume, planned remaining consumers, output protection, and drop state.
- Integration tests compare `evaluate_many` outputs with profiling off, profiling on, and lifecycle on. They also verify route selection is unchanged.
- Event consistency tests compare `latest_stage_events.jsonl`, `latest_stage_details.jsonl`, `latest_batch_details.jsonl`, and `latest_run.json` so create/consume/drop/snapshot counts cannot drift silently.
- Benchmark regression tests run fixed synthetic workloads and assert V2 does not worsen `peak_frame_col_count` or `peak_live_stage_count_estimate`, while reducing or eliminating `alive_stage_at_batch_end_count`.

Run the focused validation package:

```powershell
$env:PYTHONPATH="src;.venv\Lib\site-packages"
python -m pytest tests\test_stage_lifecycle.py -q
```

For real minute parquet smoke comparison:

```powershell
$env:PYTHONPATH="src;.venv\Lib\site-packages"
python examples\benchmark_stage_lifecycle_real_smoke.py --data data\minute_2026_03.parquet --rows 500000 --code-col ths_code
```

The real smoke script writes:

- `benchmarks/stage_lifecycle_real_smoke/v1/*`
- `benchmarks/stage_lifecycle_real_smoke/v2/*`
- `benchmarks/stage_lifecycle_real_smoke/latest_real_smoke_comparison.json`
- `benchmarks/stage_lifecycle_real_smoke/real_smoke_report.md`

## Positional Phase Profiling

Profiling also writes positional phase details for `argmax` / `argmin`:

- `latest_positional_phase_details.jsonl`

Each row splits the positional path into child expression time, Python ingestion time, grouped deque scan time, result attach time, restore time, group size metadata, and whether the Python kernel was used.

Run the dedicated phase benchmark:

```powershell
$env:PYTHONPATH="src;.venv\Lib\site-packages"
python examples\benchmark_positional_phases.py --data data\minute_2026_03.parquet --rows 500000 --expr-counts 1,8,16,20 --code-col ths_code
```

Use `--rows 0` for a full parquet run. This is the P0 baseline for any future native/GIL-free positional kernel.

## Planned Lifecycle

Lifecycle sweep now uses planned consumer counts for explicit ordered stages when the batch plan can identify reusable materialized stages. A stage with future planned consumers is kept alive until its remaining planned consumers reach zero. This preserves existing batch reuse while still dropping stages before batch end when safe.

P2.1 profiling records planned/actual lifecycle fields:

- stage-level: planned consumer count, planned last use, actual consume count, recomputed-after-drop, kept-alive-for-planned-reuse, dropped-after-planned-last-use
- batch/run-level: planned reusable stages, avoided recomputation, recomputed stages, late-alive stages
- events: `planned_stage_registered`, `planned_stage_reused`, `planned_last_use_reached`, `recomputed_stage_detected`
