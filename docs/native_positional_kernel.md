# Native Positional Kernel

P1 covers the native execution path for grouped positional rolling:

- `argmax(x, n)`
- `argmin(x, n)`

The kernel preserves the existing DSL contract:

- output is distance to the current row
- current row is `0`, previous row is `1`, and so on
- equal extrema choose the nearest occurrence
- null values do not participate
- all-null windows return null
- groups are scanned independently in the already prepared `[code, time]` order

## Current Status

The P1 series is now implemented as:

- Rust/PyO3 native grouped monotonic-deque scan
- low-copy Polars buffer ingress for `Float64` value input
- native nullable `Int64` output buffer construction
- optional group-level parallel scan
- Python fallback when native loading or native execution fails
- positional phase profiling fields that identify the active path

The bridge deliberately stays narrow and local to positional `argmax/argmin`. It does not change planner routing, lifecycle policy, or other rolling families.

## Build Prerequisites

Install:

- Rust toolchain with `rustc` and `cargo`
- `maturin`
- Windows MSVC / `link.exe`
- Python virtual environment dependencies

PyO3 is configured with `abi3-py313`, so the installed module can be loaded by Python 3.13+.

Build from the repository root:

```powershell
$env:PATH="$env:USERPROFILE\.cargo\bin;$env:PATH"
$env:CARGO_TARGET_DIR="$env:USERPROFILE\.cargo-target\factor_engine_native"
cd native\factor_engine_native
C:\Users\yuyix\Desktop\factor-engine\.venv\Scripts\maturin.exe develop --release
cd ..\..
```

If Cargo build scripts are blocked by Windows application control in a fresh target directory, reuse the target directory above or ask an administrator to allow Cargo build-script execution.

## Runtime Flags

Enable native positional execution:

```powershell
$env:FACTOR_ENGINE_POSITIONAL_KERNEL="native"
```

Enable or disable group-level parallel scan:

```powershell
$env:FACTOR_ENGINE_POSITIONAL_PARALLEL="1"  # default: enabled
$env:FACTOR_ENGINE_POSITIONAL_PARALLEL="0"  # force serial native scan
```

Disable native entirely by unsetting `FACTOR_ENGINE_POSITIONAL_KERNEL` or setting it to a value other than `native` / `auto`.

## Benchmark Command

Run a representative positional phase benchmark:

```powershell
$env:PYTHONPATH="src;.venv\Lib\site-packages"
$env:FACTOR_ENGINE_POSITIONAL_KERNEL="native"
$env:FACTOR_ENGINE_POSITIONAL_PARALLEL="1"
python examples\benchmark_positional_phases.py --data data\minute_2026_03.parquet --rows 500000 --expr-counts 1,8,16,20 --code-col ths_code --lifecycle --output benchmarks\positional_phases_native_lowcopy_parallel_500k
```

The report should show:

- `python=False`
- `native=True`
- `low-copy=True`
- `parallel=True` when parallel is enabled
- lower `positional_group_scan_time_ms` than the Python kernel path

## Profiling Fields

`latest_positional_phase_details.jsonl` records:

- `python_kernel_used`
- `native_kernel_used`
- `native_low_copy_bridge_used`
- `python_object_bridge_used`
- `native_parallel_used`
- `group_parallelism_level`
- `positional_to_list_time_ms`
- `positional_group_scan_time_ms`
- `result_attach_time_ms`

For the current low-copy path, `positional_to_list_time_ms` is best read as bridge/metadata time. It includes group-length metadata and native buffer handoff overhead, not full value `Series.to_list()` materialization.

## Fallback Behavior

The Python bridge tries the low-copy native path first. If that fails, it tries the older native object bridge. If native import or execution fails, the executor safely falls back to the Python grouped scan.

Fallback is visible in profiling:

- native low-copy path: `native_kernel_used=True`, `native_low_copy_bridge_used=True`, `python_object_bridge_used=False`
- native object bridge fallback: `native_kernel_used=True`, `native_low_copy_bridge_used=False`, `python_object_bridge_used=True`
- Python fallback: `python_kernel_used=True`, `native_kernel_used=False`

## Known Limits

The low-copy bridge uses Polars private Python buffer APIs (`_get_buffers`, `_get_buffer_info`, `_from_buffer`, `_from_buffers`). This keeps the implementation local and avoids reintroducing a heavy plugin build chain, but it means future Polars upgrades should run the native positional tests and phase benchmark before being accepted.

Group-level parallelism is useful for multi-expression or larger group workloads. For very small workloads or a single expression, thread scheduling overhead can outweigh the benefit, so serial native mode remains available.
