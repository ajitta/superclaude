branch: fix/prompt-content-audit @23350fc1+ (base master @0c63688d, not pushed, no upstream)

# Session 2026-10-15 — fix/prompt-content-audit (prompt-content audit, rounds 1–3)

## Where it stands
- Static audit of shipped markdown/XML content for Opus 5.5 / Sonnet 5.5 / Fable 5.1: does the model read it as intended. Code behavior out of scope. Audited independently of the installed superclaude (isolated sub-agents; no installed `~/.claude` or `.claude/superclaude` content read as reference)
- Feature folder `docs/features/prompt-content-audit/` (README `phase: implementing`) is the record: README → 03 (round 1 summary; §4 P0/P1/P2 all marked done) → 03a–03f (round 1 areas) → 03g–03i (round 2) → 08/08a/08b implementation → 09/09a/09b independent reviews
- Round 3 (08b, 09b) closed the remaining P1/P2 items and the 08a deferred list
- Last full run: `uv run pytest` 3539 passed / 3 skipped; `tests/unit/scripts` 149 passed; `make lint` clean. Worktree clean
- NOT done: `make canary-gates`; merge to master; `make sync-local` (local `.claude/` install still has the old content — not tracked by git)

## What changed (commits, oldest first)
- aa5b0e87, 42f9045e: round 1 P0 — superclaude-only gotchas made conditional, example↔rule conflicts, PRINCIPLES R12 reversibility branch
- 9a247cb6, 72445b09, 3d1475ce, ce239738, 3a1f6285, 17204cb6, f2da52b1: round 2 — core/rules modules, `.claude/rules/` + gotchas, loader `--structured`, commands + output style
- 3286c3f8: `tests/unit/test_frontmatter_yaml.py` (YAML-invalid frontmatter passed every structure test)
- 25c1ceea: 23 agent descriptions rewritten ("Use proactively" removed from 21; "Not for … — <neighbor>" gates); RULES_DOCS phase mapping
- bed08fdb: command-authoring tier rule (research is the explicit auto exception)
- df0b8738 core: FLAGS observable conditions, mode text is not a trigger, one 60% ctx point, R-ID legend in RULES, both install paths, docs-only inspection, 🔴 security-only; loader injects RULES_DOCS on a write verb + CLAUDE.md/AGENTS.md/.claude/rules (English/Korean)
- 1172b4fb modes · 61b4d570 agents (pinned Ask First subagent sentence + no R-ID tags, both tested) · ae4b42ac commands + agent-authoring · 8b3eb320 mcp + sc-prompt · b79567ca sc-author · 5bf1f22e independent-review fixes · 23350fc1 docs

## Decisions
- Phase mapping (delegated): README `phase:` = furthest stage reached, never backward
- research stays auto-tier as an exception; reflect auto (writes only after consent)
- Round 3 (orchestrator, recorded in 08b): parent task text confirms only a reversible action named with its target; destructive/irreversible needs the user's quoted approval. Kernel keeps R-ID tags with a legend. /sc:research picks its strategy by query clarity (was: unified default — behavior change). sc-prompt carried earlier-model rows are reported as candidates, never applied (behavior change)

## Problems hit
- Every fix round introduced Medium/High defects only the independent review caught (round 3: Ask First sentence let a parent authorize destructive ops; sc-prompt carry-over exception reopened its own ban) → keep fix-then-independent-review
- 6 parallel workers were all interrupted at ~13 min (provider stall + concurrent full-suite runs); re-dispatched with "resume the draft in git diff", area tests only, orchestrator runs the full suite
- Python `\b` between `.md` and Hangul is no boundary (both word chars) — no trailing `\b` before a Korean suffix
- Hermes execute_code kernel state resets between calls: keep helpers in a scratch module and import

## Next actions
- [ ] Decide: Opus 5 `reasoning_extraction` (sc-prompt SKILL.md:49, utils/__init__.py:308-310, evals/run_eval.py:316-318 say Opus 5 lacks it; the Opus 5.5 migration guide reads otherwise)
- [ ] `make canary-gates` (inside Claude Code add `EVAL_ARGS="--runs-dir <dir outside ~/.claude>"`) plus sc-author-* tasks; watch Ask First stops, research strategy, RULES_INTERACTION menus, plan/review gates. Delete runs dirs afterwards (they copy `.credentials.json`)
- [ ] Merge to master when canary is green (version bump only at release)
- [ ] Low leftovers (08b): commands abbreviations (help/implement/init), pm description Direct strategy, author-check X1 single root for memory files (code), FLAGS `Scope:` ordering meaning
