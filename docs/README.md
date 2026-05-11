# Documentation

`docs/` is layered so new readers can distinguish current rules from historical context.

## Layout

- `current/`: current truth source for architecture, invariants, repository rules, setup, and cleanup plans.
- `history/`: architecture evolution notes, planner version notes, and phase records that explain how the project got here.
- `archive/`: old references kept for preservation when they no longer fit current or history.
- `benchmark/`: benchmark methodology, profiling attribution notes, and performance interpretation guidance.
- `strategy/`: future direction and capability planning.

Start with `docs/current/README.md` when making code changes. Historical documents are background unless their rules are repeated in `docs/current/`.
