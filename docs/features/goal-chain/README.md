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
- [06c-verify-round2.md](./06c-verify-round2.md): second independent verification of `v4.33.0..HEAD` (Korean): the 4.33.1 fixes, probe v2, the command release gate and `make canary-commands`, mutation check of the new tests
- [06d-followups-applied.md](./06d-followups-applied.md): the interactive run, the design-status and release-gate changes, and each second-review finding with what changed
- [06e-ask-checkpoint.md](./06e-ask-checkpoint.md): `--through --ask`: why one checkpoint, what it does, six runs (four interactive on sonnet and opus with answers against ★, two headless)
- [06f-verify-ask.md](./06f-verify-ask.md): independent verification of `--through --ask` (Korean): gates, one headless fallback run, the 06e numbers against the record, findings
- [06g-ask-review-applied.md](./06g-ask-review-applied.md): each finding of the third review (06f) with what changed, and the new `intent-through-ask-headless` probe
- [06h-other-answers-reviewer-memory.md](./06h-other-answers-reviewer-memory.md): the two follow-ups after 4.34.0: an answer in the user's own words counts as `confirmed`; `self-review` and `verifier` keep no memory, and the `--through` probes check for a memory folder
- [06i-verify-followups.md](./06i-verify-followups.md): independent verification of 06h (Korean): gates, mutation checks, upgrade and scope-conflict runs in a sandbox, findings on the own-words and ★ wording
