branch: fix/prompt-content-audit @bed08fdb (base master @0c63688d, 15 commits ahead, not pushed, no upstream)

# Session 2026-10-15 — fix/prompt-content-audit (prompt-content audit, rounds 1–2)

## Where it stands
- Static audit of shipped markdown/XML content for Opus 5.5 / Sonnet 5.5 / Fable 5.1: does the model read it as intended. Code behavior out of scope. Audited independently of the installed superclaude (isolated sub-agents; no installed `~/.claude` or `.claude/superclaude` content read as reference)
- Feature folder `docs/features/prompt-content-audit/` (README `phase: implementing`) is the record: README → 03 (round 1 summary) → 03a–03f (round 1 areas) → 03g–03i (round 2: core/rules, `.claude/rules`, commands + output style) → 08/08a implementation → 09/09a independent reviews
- Last full run: `uv run pytest` 3490 passed / 3 skipped; `tests/unit/scripts` 149 passed; `make lint` clean. Worktree clean
- NOT done: `make canary-gates` (core, commands and agent routing changed); merge to master; `make sync-local` (local `.claude/` install still has the old content — not tracked by git)

## What changed (commits, oldest first)
- aa5b0e87, 42f9045e: round 1 P0 — superclaude-only gotchas made conditional (security/backend/frontend), example↔rule conflicts, PRINCIPLES R12 reversibility branch
- 9a247cb6: core/rules RULES_{QUALITY,INTERACTION,DELEGATION,DOCS} — contradictions, dangling refs, unmeasurable gates, repo history leaks (03g)
- 72445b09, 3d1475ce, ce239738: `.claude/rules/` authoring rules + gotchas (general.md 21→14 entries); grammar restored from the b196673b telegraphic style (03h)
- 3a1f6285: loader — `--structured` loads BUSINESS_SYMBOLS only under `/sc:business-panel`
- 17204cb6, f2da52b1: commands + plain-language output style (03i, 09a). `/sc:review` owns the brainstorm→plan spec gate (`approved-for-plan` + Iteration Log)
- 3286c3f8: `tests/unit/test_frontmatter_yaml.py` — `md_helpers.parse_frontmatter` splits on the first colon, so YAML-invalid frontmatter (`: ` in a description) passed every structure test
- 25c1ceea: 23 agent descriptions rewritten ("Use proactively" removed from 21; only security-engineer keeps "Use immediately after <event>"; every one has "Not for … — <neighbor>"). RULES_DOCS phase mapping; implement sets plan `status: implementing` + README phase; promote-feature derives phase from moved docs
- bed08fdb: command-authoring tier rule — on-request when a command writes committed artifacts by default; research is the explicit auto exception

## Decisions (user)
- Phase mapping delegated to the agent: README `phase:` = furthest stage reached, never backward (00→intent, 01→discovery, 04→design, 05→planning, first plan box→implementing, plan complete→complete; 02/03/06+/deprecated never move it; abandoned only on user word)
- research stays auto-tier as an exception; reflect stays auto by the rule (writes only after user consent) — user was told and may still want on-request
- Agent descriptions cleaned now rather than in a separate branch

## Problems hit
- Output-style and plan fixes introduced new defects that only the independent review caught (emoji ban blocked `--introspect` markers and the R21 `⚠ failed:` record; plan's draft check reopened the review gate) → keep the fix-then-independent-review loop
- Grammar-only pass drifted meaning in 4 sentences (2 reverted) and a gotcha figure (~20%) got misattributed → reviewers must diff meaning, not just wording
- Hermes execute_code kernel state resets between calls sometimes: helper functions (ap/apply) had to be redefined

## Next actions
- [ ] `make canary-gates` (inside Claude Code add `EVAL_ARGS="--runs-dir <dir outside ~/.claude>"`); watch agent routing, RULES_INTERACTION menus, R12/R21, plan/review gates. Delete runs dirs afterwards (they copy `.credentials.json`)
- [ ] Optional independent review of 25c1ceea agent descriptions (neighbor gates, behavior removed by dropping "proactively": project-manager, quality-engineer, insight-analyst, repo-index, project-initializer)
- [ ] Merge to master when canary is green (version bump only at release)
- [ ] Remaining P1 (03-analysis §4): 5 subagent run-rule line in all agents; 7 R-ID tags in agent bodies + kernel; 8 FLAGS unmeasurable conditions / one ctx threshold; 9 FLAGS mode flags + RULES.md:34 user-scope path; 11 sc-prompt mirror/Fable block, sc-author checker on unapproved files, VS template ambiguity; 12 area Med items
- [ ] Deferred from round 2 (08a): RULES_DOCS not injected when editing CLAUDE.md (TRIGGER_MAP design); agent/pm/task "Not for" gates; agent template count quotas; remaining telegraphic prose; DELEGATION ">20K tokens"/"under 30s"; cleanup R1 check now depends only on R3
- [ ] P2: 🔴 meaning split, sc-author legacy conventions, low-confidence facts (03f)
