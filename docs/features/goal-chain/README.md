---
feature: goal-chain
phase: discovery
owner: ajitta
created: 2026-10-20
updated: 2026-10-20
related: ../intent-command/
---

# One prompt from intent to done

Can a user type only the intent and have the whole Large chain (`/sc:intent` → … → `/sc:reflect`) run to the end in one prompt? Tested headless in a scratch repo, with Claude Code's `/goal` and with a plain prompt listing the steps. The result is the README recipe under Workflows → "One prompt from intent to done" and the matching block on the Pages site (`docs/index.html`, #commands).

## Documents

- [06-run-record.md](./06-run-record.md): setup, the prompts, per-run results, the evaluator failure mode and the wording that fixed it
