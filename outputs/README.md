# Outputs

`outputs/` is a local runtime output directory.

Generated result files are ignored by default and should not be committed. Large outputs should go under `artifacts/outputs/` or another external artifact location.

If a result needs to be preserved in Git, convert it to a small human-readable summary that explains the context instead of committing full generated data.

