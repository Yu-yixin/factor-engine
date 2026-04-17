# AI State

- `.ai_state/current.yaml` is the only current truth source.
- `.ai_state/current.yaml` is for active agent handoff and current engineering status.
- `.ai_state/history/commits/<git-sha>.yaml` stores append-only commit snapshots.
- Commit snapshots align one-to-one with Git commits.
