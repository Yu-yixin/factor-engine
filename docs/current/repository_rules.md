# Repository Rules

Git should represent source code, necessary documentation, small examples, and reproducible configuration.

Git should not represent runtime outputs, large local data, caches, native build targets, virtual environments, or temporary profiling dumps.

## Can Be Committed

- Core source under `src/` and native source under `native/**/src/`.
- Tests, small deterministic fixtures, and small example inputs when they are documented.
- Documentation under `README.md`, `docs/`, and selected benchmark summaries.
- Project configuration such as `pyproject.toml`, `Cargo.toml`, and lock files that are intentionally part of builds.
- Small, sanitized example data only when it is necessary to run examples or tests.

## Must Not Be Committed

- Virtual environments such as `.venv/`, `venv/`, or `env/`.
- Python, pytest, ruff, mypy, or coverage caches.
- Native build output such as `native/**/target/`, `.dll`, `.pdb`, `.rlib`, `.rmeta`, `.so`, and `.dylib`.
- Runtime outputs under `outputs/` or `artifacts/`.
- Large parquet, csv, jsonl, sqlite, or database files.
- `latest_*`, `history.csv`, and detailed profiling JSONL outputs from benchmark runs.
- Secrets, `.env` files, credentials, or local machine configuration.

## Large File Strategy

Large files are external artifacts by default. Do not add large parquet/csv/db/jsonl files to Git. If a large file is required to reproduce a benchmark, document its expected location, schema, and acquisition path instead of committing it.

## Local Data Strategy

Local or real data belongs under `artifacts/local_data/` by default. Tests should use generated data or small sanitized fixtures. Benchmark scripts may accept local data paths but must not require large data to be present in Git.

## Outputs Strategy

Generated results belong under `artifacts/outputs/` or another ignored runtime directory. `outputs/` is ignored going forward and should not be treated as a durable source directory.

## Native Build Artifact Strategy

Native source may be committed. Native build products must not be committed. Rebuild them locally using the documented native setup.

## Benchmark Output Strategy

Benchmark scripts and selected summary reports may be committed. Full run directories, `latest_*`, `history.csv`, JSONL traces, and temporary profiling dumps belong under ignored artifact locations.

## Cache And Temporary Strategy

Caches and temporary directories must be ignored. Temporary test directories should be clearly named and safe to recreate. Do not make cleanup depend on deleting tracked files during Phase 1.

## AI Coding Agent Rules

- Read `docs/current/` before changing behavior.
- Do not refactor core execution paths during repository cleanup tasks.
- Do not delete large files, historical documents, benchmark history, or generated artifacts unless the task explicitly says to do so.
- Do not change `evaluate`, `evaluate_many`, planner, executor, lifecycle, or native behavior when the task is documentation or hygiene only.
- Report tracked artifacts separately instead of silently removing them.

