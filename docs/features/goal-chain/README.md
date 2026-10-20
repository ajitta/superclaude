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
- [06a-verify-intent-through.md](./06a-verify-intent-through.md): independent verification of `/sc:intent --through` (Korean): gates, one live run, canary mutation check, findings
- [06b-verify-applied.md](./06b-verify-applied.md): six more runs (opus, a multi-module task, a push request) and each review finding with what changed, plus the probe v2 mutation table
