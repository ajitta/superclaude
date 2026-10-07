# Session 2026-10-07 (evening) — AI-Native SDLC Playbook alignment

Branch `docs/intent-command-plan` off master 04b55604, 10 commits 81fcb509..c01112fc. NOT merged, NOT pushed at save time. Full suite 2947 passed / 7 skipped, scripts 149 passed, ruff clean at c01112fc.

## What was asked, decided, ruled out

- Asked: evaluate SuperClaude against Anthropic's "The AI-native SDLC playbook" (Louis Claxton, 2026-08-21, 'https://claude.com/resources/articles/the-ai-native-sdlc-playbook'), find improvements, then (via /goal) implement them starting with an intent command.
- Premises set by the user (recorded in `docs/features/sdlc-playbook-alignment/03-analysis.md` 전제 1–4 and auto-memory): stage-by-stage manual /sc:* invocation is deliberate — never propose auto-triggered handovers or auto-accept; subscription account, no ANTHROPIC_API_KEY — headless runs are local `claude -p` only, never CI; trivial work skips gates (README tier table already does this); CC plan mode is no longer the default (auto mode default since 2026-08-14 / v2.1.283), so the playbook's "plan mode first" play is stale.
- Decided: `/sc:intent` is a separate command, not a brainstorm flag — brainstorm reinterprets; intent captures verbatim before analysis.
- Ruled out (R18): evals in CI, auto-mode/permissions.allow guidance, REVIEW.md policy file, PR babysit loop, metrics tooling, org policy-skill slot, test_runner_hook narrowing, Maintain→intent loop.
- Reversed: the test_file_guard hook (test-file lock during /sc:troubleshoot --fix) was built, reviewed and then removed at the user's decision — a hook whose trigger depends on language/layout conventions is worse than a prose rule ("모델의 능력이 프로즈 규칙으로 통할거라고 예상"). Only the `fix-not-test` gotcha + "commit the failing test" step remain in troubleshoot.md. Do not re-propose.
- Cost decision: release gate = `make canary-gates` (4 hard-gate tasks: destructive-elicitation, poisoned-readme, problem-statement-not-request, conflicting-constraints; sonnet default; `--effort low`), triggered only by `src/superclaude/core` or `hooks.json` changes; the full 14-task canary is for model releases only; never Fable headless (bills usage credits).

## Shipped (commit → content)

- 81fcb509 plan `docs/features/intent-command/05-plan.md`; 35f836fb analysis `docs/features/sdlc-playbook-alignment/03-analysis.md` (per-play table, refined items, dropped items, status table).
- 7de4b521 `/sc:intent`: `src/superclaude/commands/intent.md`, output `docs/features/<slug>/00-intent.md`; RULES_DOCS `00-intent` prefix, `intent` phase enum, gate; brainstorm/review/reflect consume it; count 36→37 everywhere; headless probes behaved (trivial refusal, two-question fill).
- da4a2f12 gates: /sc:implement Deviations rule + `tests/unit/test_plan_checklist.py` (status: complete ⇒ no open box); /sc:plan footer (Risks / Alternatives not taken / Proof) + Interrogate step; /sc:design `--from` + required "Areas of concern"; /sc:review Dim 3 (always-loaded docs stale?) + R19 fires on repeated review findings (kernel + RULES_QUALITY).
- 7cf07537 → 611244e7 release gate: `make release` refuses without `CANARY_OK=1` when core/ or hooks.json changed since last v* tag; `make canary-gates` target; AGENTS.md + evals/README wording; `docs/research/claude.com/` gitignored, playbook cited by URL.
- 3362816e verifier agent (`src/superclaude/agents/verifier.md`, report-only, tools Bash/Read/Grep/Glob, /sc:test gains a Verify step; agents 23→24) + `evals/run_eval.py --permission-mode` (choices from `claude --help` 2.1.292 incl. manual; recorded per row + report header). The hook in that commit was removed by c147b80c.
- c01112fc gotcha budget: every `.claude/rules/gotchas/*.md` entry ≤ 320 chars, README Limits line, `tests/unit/test_gotcha_budget.py`; general 16→18 entries, hooks 12→18 (splits, no name dropped); 15 reviewer-flagged losses restored.

## Method notes worth keeping

- Ultracode workflows used for authoring (3 drafts + 2 judges), parallel implementation (3 streams returning edits; main loop applies — subprocess writes are discarded), adversarial review (3 lenses) and gotcha compression (compress→verify pipeline). Review caught a real must-fix: `lock` run from the Bash tool has no CLAUDE_PROJECT_DIR, so hook state resolved from cwd diverged from the hook's anchor.
- The Bash tool mangles backslashes inside quoted heredocs on this machine (`\\n` → newline); write Python edit scripts with the Write tool and run them with `python -I`.
- Adding a /sc:* command trips six roster/count tests at once (README badge/prose/tree/help counts, roster, both dispatcher lists) — update all in the same commit.

## Open / next

- Merge `docs/intent-command-plan` to master, push.
- Version bump 4.22.0: CHANGELOG `### Added` (intent, verifier, --permission-mode, plan/design/review gate edits, fix-not-test, CANARY_OK gate, gotcha budget) — test_version_consistency accepts only dated release headings equal to pyproject, so this lands in the bump commit; close intent-command plan Task 6 and set both feature READMEs to `phase: complete`.
- Before release: `make canary-gates` (first real run; also try `--permission-mode auto` once to measure prose-gate survival), then `CANARY_OK=1 make release`.
- Optional: use `/sc:intent` once on a real Large task — the Save path (file + README) was never exercised headlessly.

Related: `mem:session_2026-10-07_prompt-audit-verify-and-merge` (earlier today, 4.21.0 release).
