# Development Setup

This file describes the current expected local setup. It does not require large data files to be committed to Git.

## Windows PowerShell

Create and activate a Python environment:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install polars pytest ruff
```

Set the source path before running examples or tests:

```powershell
$env:PYTHONPATH="src"
```

Run tests:

```powershell
py -m pytest -q
```

Run lint:

```powershell
.venv\Scripts\python -m ruff check
```

## Unix-Like Shell

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install polars pytest ruff
PYTHONPATH=src python -m pytest -q
python -m ruff check
```

## Native Extension

The optional native extension lives under `native/factor_engine_native/`.

Native build instructions and environment switches are documented in `docs/native_positional_kernel.md`. Native build output such as `native/**/target/`, `.dll`, `.pdb`, `.rlib`, `.rmeta`, `.so`, and `.dylib` must not be committed.

The Python fallback path must remain usable when the native extension is absent.

## Data Files

Large data files are not maintained in Git going forward. Local benchmark and real-data runs should use files supplied externally, preferably under `artifacts/local_data/`.

Small committed fixtures must be small, sanitized, and documented.

