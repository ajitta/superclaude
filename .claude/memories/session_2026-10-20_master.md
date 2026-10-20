branch: master @2dae9eb9 (== origin/master == stable == v4.32.2); worktree clean (untracked .hermes/, .ignore belong to other sessions)

# Session 2026-10-20 — master (pressure-probe readout, eval-arm isolation, agent roster audit → 4.32.0)

## Where it stands
- Pressure probes measured, vanilla vs sc-full, sonnet low (`docs/features/pressure-readout/`):
  - Hurry: sc-full 30/30 vs vanilla 20/30, one-sided Fisher p = 0.0004 (pre-registered rule 3, "SC helps under hurry"). All 10 vanilla misses were Edit, then DONE, with no run.
  - Control `probe-verify-claim`: 10/10 on both arms.
  - Dictated-fix and sunk-cost: both arms at ceiling.
- Harness faults fixed red-first:
  - Every arm loaded the claude.ai account's synced plugins (from the 2nd session), skills (often from the 1st) and connectors. Fixed with `--setting-sources project,local` + `ENABLE_CLAUDEAI_MCP_SERVERS=false`.
  - `sc-command-only` loaded the full core through `.claude/CLAUDE.md`. Fixed by removing that import with the installer's `remove_claude_md_import`.
  - `probe-verify-claim` now grades with the pressure-time-verify pattern.
- The verifier (headless opus high, `02-verify.md`) said PASS WITH FIXES; findings 1–7 applied. The purpose-generalization and purpose-opus 04 readouts carry a contamination caveat (no label flips).
- First isolated `make canary-gates`: 7/7 gates, 13/13 checks, 0 contaminated sessions.
- Full suite 4555 passed / 3 skipped; ruff, mypy clean. No release: nothing under `src/superclaude` changed, so the `[Unreleased]` entries go out with the next release.
- Master CI green on 8adfdbfc (run 39286058300, after GitHub Actions' degraded spell on 2026-10-20 queued it ~30 min).

## Agent roster audit (released as 4.32.0)
- Retired 19 of 24 agents. 10 were domain personas, 6 were jobs that must talk with the user (a subagent returns one summary), plus git-workflow, root-cause-analyst (→ /sc:troubleshoot) and simplicity-guide (→ RULES_QUALITY). Kept 5: deep-researcher, repo-index, business-panel-experts, self-review, verifier (`docs/features/agent-roster-audit/`).
- Basis: Anthropic's Skills post (2026-01-22, "stopped building specialized agents"), the sub-agents docs, and "How and when to use subagents" ("Most teams settle on a handful of well-scoped agents"). The repo's own record: 22/23 agents at zero invocations.
- Upgrade removes retired files by content digest (`RETIRED_AGENT_DIGESTS` regenerated from `gen_shipped_names.py`). An e2e run on a scratch CLAUDE_CONFIG_DIR at user, project and local scope found user-edited copies and agent-memory folders kept.
- Verifier (headless opus high, `02-verify.md`): PASS-with-fixes, 10 findings, all applied. Main one: current Claude Code lets a subagent spawn subagents up to 3 layers when `Agent` is in its tools. The old "subagents cannot spawn" text in agent-authoring was wrong; self-review dropped `Agent` so it stays read-only.
- Canary gates 7/7, Windows install/upgrade job green, released v4.32.0 (CANARY_OK=1: one RULES_QUALITY sentence).

## Decisions
- Agents: one stays only if its job needs its own context, restricted tools or a fresh reviewer. Domain checklists live in commands and rules, applied by the main session or `general-purpose` delegates. `/sc:load` no longer reads pm_context.
- Eval runs from before 2026-10-20 carry account content that varied from session to session and between arms. They are not pooled with isolated runs; no rerun now.
- Pressure-probe readouts use one-sided Fisher with rules written before the data. This prereg was committed 58 s into batch B; its corrections section records that.

## Problems hit
- `git checkout -- .`, run from the repo cwd during a scratch check, threw away an uncommitted fix. Commit before running scratch checks from the repo dir.
- The gotcha budget is 320 chars per entry (`test_gotcha_budget.py`).
- Reusing a Python variable name across kernel cells wrote the agents README text into a test file. Reverting the file and rebuilding the edit fixed it; use distinct names per edit.

## Next actions
(full list with options and ★: `docs/plans/remaining-work-ajitta-2026-10-20.md`; the 10-19 list is superseded)
- [ ] Dictated-fix / sunk-cost probes at ceiling: ★keep as regression guards; re-read at the next model canary
- [ ] Pressure probes on opus / auto mode: on hold
- [ ] `bugfix-scope-creep` (matrix task) still has the loose `pytest|python -m pytest` grader; align it when its comparability no longer matters
- [ ] Carried over from 2026-10-19: S3 C-16/C-17 on hold; axis B at the next model; split `docs-ssot-audit/06-verify.md` before a sizable addition; opus N2/N5 round and the "open the referenced file" wording trial on hold; `origin/fix/plain-language-structure` kept; Windows `0xC0000409` → `git revert 3e64dc82`

## Weakness audit → completion-proof (released as 4.32.1)
- An external weakness analysis + ECC-compared plan (docs/research, renamed to convention) was audited against the source (`superclaude-weakness-audit-ajitta-2026-10-20.md`). Diagnosis mostly right, prescription too heavy: the 3-state lifecycle was rejected (phase never moves back; reflect is an ungated step). The audit was verified by headless opus high: PASS WITH FIXES, 19 findings applied.
- Shipped: `/sc:implement --plan` closes a plan only after the Proof ran on the last code commit (`Result: <sha> — <output>` in a docs-only commit; a red re-run reopens the plan); a draft spec is always reviewed by the isolated reviewer with `00-intent.md` verbatim; decision-mode default (unclear → delegated, a label with a particle counts); README gates labelled model-followed; Large chain gains `/sc:review --scope branch`; `workflow_gates` updated.
- Probes `implement-proof-fail`, `plan-draft-spec-gate` (prereg first): ceiling on sonnet low, 10/10 before and after; gate 10/10. After the verifier's F1 the `Result:` sha was right in 10/10 (before the fix: 3 of 8). Verifier on the branch: PASS WITH FIXES, 12 findings applied (`docs/features/completion-proof/06-verify.md`).
- canary-gates 7/7 twice (CANARY_OK=1: RULES_DOCS lines), released v4.32.1.

## Next actions (added)
- [ ] Follow-ups of the weakness audit: `docs/plans/remaining-work-ajitta-2026-10-20.md` §4a (N4 effect probe, decision-mode probe, held RED clause; `origin/docs/superclaude-weakness-research` deleted after the owner confirmed)

## /sc:intent Done when line (released as 4.32.2)
- Compared with dialectic-skills dia-intent (a pre-work approval gate, no file) — different jobs, both kept. Borrowed one thing: a completion signal the user states goes under Proposed outcome as a quoted `Done when:` line; never inferred or asked for (gotcha invented-criterion). `/sc:reflect` compares against it when present. Full suite 3754 passed; CI green; no core change, so no canary.
