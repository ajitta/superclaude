---
feature: docs-ssot-audit
phase: plan
status: implementing
created: 2026-10-19
revised: 2026-10-19
---

# 05. Plan — fix groups, guard tests, owner questions

Findings: [03-findings.md](./03-findings.md). Phases 0–3 stopped here (00 §Rules); the owner's rulings below opened the fix round.

## Owner rulings (2026-10-19)

> Owner ruling: Q1–Q10 all as recommended (Q1 a, Q2 a, Q3 b, Q4 a, Q5 a, Q6 a, Q7 a, Q8 a, Q9 a, Q10 a).

| Q | Decision |
|---|---|
| Q1 | (a) fix S2 and S3 in one round on `fix/docs-ssot`, groups G1–G5, one commit each |
| Q2 | (a) hand-edit `PROJECT_INDEX.md`, add it to T2/T3/T6 |
| Q3 | (b) all seven guards, T2's phrase table capped at ten entries |
| Q4 | (a) dated research and analysis docs stay as records |
| Q5 | (a) the two draft plans become `status: deprecated` under `docs/archive/plans/` |
| Q6 | (a) delete README's unsupported research numbers; depth table at the config's columns |
| Q7 | (a) `core/README.md` drops the token figure and class list, points at RULES.md and `TestCoreLiteSplit` |
| Q8 | (a) rewrite the three CLI/pyproject self-description strings |
| Q9 | (a) codex guides: fix D-08, D-09, D-12, D-13 only, bump `last_verified` |
| Q10 | (a) fix `evals/README.md` arms and matrix-task wording in the same round |

Round rules from the ruling: guard tests first and seen red; area tests per commit; full suite, `make format`, `make lint`, `make typecheck` clean at the end; push and dispatch the Tests workflow on the branch; no merge, no version bump, no release; an independent verifier reviews afterwards.

## Owner summary

- **Question:** which docs contradict the SSOT, and what would have caught them?
- **Found:** 25 (0 S1, 7 S2, 18 S3). The S2s: a help text naming the wrong git file (D-01), a navigation doc naming a branch that does not exist (D-02), PRD's CI claim (D-03), README research numbers nothing defines (D-04), README crediting `/sc:reflect` and `/sc:load` with insight writes they do not make (D-05), two docs disagreeing on the kernel (D-06), a hooks README missing a registration (D-07).
- **Pattern:** every S2 is a sentence that could become false with nobody editing it (a copied number, a mechanism restated, a list of registrations). The durability rule (`content-quality.md` §5) already names the cure; the guards below make it mechanical where a copy is worth keeping.
- **Decide:** Q1 fix policy, Q3 which guards, Q6 the README research numbers, Q7 core/README's kernel line, Q9 the codex guides; the rest confirm a default.

## Progress

- [x] P1 Owner answers Q1–Q10 (rulings above)
- [x] P2 Guard tests T1–T7 (per Q3), red first against the current text — `tests/unit/test_docs_ssot_guards.py` plus the T6 extension of `test_version_consistency.py`; 19 red at ff947b33 (17 guards + 2 no-expiry)
- [x] P3 Fix round on `fix/docs-ssot` (groups G1–G5 below, per Q1), one commit per group — G1 e85dfc45, G2 ee614358, G3 8b0adbb6, G4 9d86be84, G5 5ce02050
- [ ] P4 Full suite, `make format`, `make lint`, `make typecheck` clean; push; Tests workflow dispatched on the branch and green
- [ ] P5 Independent verification, then merge and one release (owner; not this round)

## Deviations

- **Beyond the findings, caught by the guards while red:** `docs/PRD.md:29` said "gitignored" (T2, same family as D-24) and was reworded; codex `08:351` named a removed `make build-plugin` target (make-target check) and now says "the former `build-plugin` target"; codex `08:103` kept its record of `test_skill_structure.py:163-168` as a dated observation, with the current file named beside it, so the test-path check no longer reads it as a live path.
- **D-04 shape:** README's "Quality Scoring" block became "Evidence Rules", restating RESEARCH_CONFIG's source-count, credibility-tier and replan rules, rather than being deleted outright; the depth table keeps a "Best For" column (allowed by T4) and drops Time and Confidence target.
- **D-06 scope:** only `core/README.md` lost its token figure (Q7 a). `ARCHITECTURE.md:31` still says "~1.5k-token kernel … five rule classes"; it is correct today (6,136 bytes) and dated to the 2026-10-17 rule, and T2's token-figure row is scoped to `core/README.md`, so this one copy remains unguarded.
- **T1's second half** is narrower than §2 proposed: a `scripts/README.md` row is checked only when it names at least one hook event, and then must name all of that script's events; rows that name none (context_loader, the guards) are not forced to.
- **T3** checks `tests/…/*.py` paths, the two docs/ layouts and `.claude/rules/*.md` names; bare `test_x.py` names are not checked (codex 04 writes a probe file under such a name).
- **T6** matches version lists only with dots (`3.10/3.11/3.12`), so RESEARCH_CONFIG's `10/1/1` profile triples and dates never hit.
- The deprecated plans keep their original filenames under `docs/archive/plans/` (the archive's dated files use another shape, but renaming would break the audit's own references).

## 1. Fix groups

| Group | Findings | Shape of the edit | Files |
|---|---|---|---|
| G1 CLI and Makefile help | D-01, D-15, D-16, D-17, D-24 | one-line rewrites of docstrings and `##` comments; no behaviour change | `cli/main.py`, `pyproject.toml` description, `Makefile`, `CLAUDE.md` |
| G2 README behaviour claims | D-04, D-05, D-16, D-17, D-21, D-22 | delete unsupported numbers; route the insight sentence to `/sc:insight`; add `skills/` and `templates/` rows; complete or delegate the two lists; name AGENTS.md | `README.md` |
| G3 Shipped READMEs and ARCHITECTURE | D-06, D-07, D-18, D-19, D-20 | add the Stop registration; drop the kernel figure; reword two script rows; `sc-prompt` in the skills rows; fix the two pointers | `src/superclaude/{core,hooks,scripts}/README.md`, `ARCHITECTURE.md` |
| G4 Working docs | D-02, D-03, D-08, D-09, D-10, D-11, D-12, D-13 | restate the branch model; cite `test.yml` instead of its numbers; "the arms in `ARMS`"; real test names; real dirs; drop pytest-cov and `make verify` | `docs/PRD.md`, `docs/README.md`, `docs/reports/PROJECT_INDEX.md`, `docs/codex/…/{04,05,06,08}` |
| G5 Records | D-14, D-23, D-25 | delete two UI-guide lines; two hook names in CHANGELOG 4.29.0; the two draft plans per Q5; research docs untouched | `docs/UI-GUIDE.md`, `CHANGELOG.md`, `docs/plans/` |

Effort: G1–G3 about 1.5 h with their tests; G4–G5 1 h. 0 headless sessions; the `independent-reviewer` subagent on the diff is enough (prose only).

## 2. Guard tests to add

Each is a small parametrized test in `tests/unit/`, written red against today's text, then green with the fix. None duplicates 01 §3.

| ID | Test | Catches | Cost |
|---|---|---|---|
| T1 | `test_hooks_readme_lists_every_registration`: every `command` in `hooks.json` appears verbatim in `hooks/README.md` "Current Hooks", and each event heading there is an event in the json; `scripts/README.md` names every event a script is registered on | D-07, D-18 | 20 lines |
| T2 | `test_docs_name_no_retired_term`: a forbidden-phrase table over README, AGENTS, CLAUDE, PROJECT_INDEX, docs/README, PRD, the CLI help text (captured through `CliRunner`) and the Makefile: `.gitignore block`, `gitignored` (local scope), `` `integration` `` branch, `pytest-cov`, `make verify`, `PM Agent`, a token figure for RULES.md, `superclaude hook <x>` with `x ∉ HOOKS`, `make <t>` with `t ∉ .PHONY`; plus "every `RETIRED_FLAGS` key appears in README's retired list, or the list is a pointer" | D-01, D-02, D-03, D-06, D-12, D-13, D-15, D-17, D-21, D-23, D-24 | 60 lines; the phrase table is the thing to keep short (Q3) |
| T3 | `test_doc_paths_exist`: every `tests/…/*.py` path, `docs/<dir>/` entry in a Layout table, and `.claude/rules/*.md` name cited in README, AGENTS, CLAUDE, `docs/{README,PRD,UI-GUIDE}.md`, `docs/reports/*.md`, `docs/codex/prompting_session_raw/0[1-8]*.md`, `.claude/rules/**` exists (placeholders skipped) | D-09, D-11 | 40 lines; the resolver in `tools/extract_refs.py` is the draft |
| T4 | `test_readme_research_table_matches_config`: README's depth table rows equal RESEARCH_CONFIG's `<depth_profiles>` rows (profile, sources, hops) and carry no column the config lacks | D-04 | 25 lines; moot if Q6 = (a) and the table is cut to the config's columns |
| T5 | `test_readme_command_claims_resolve`: a README sentence of the form "`/sc:<x>` writes/reads `<file>`" requires `<file>` to appear in `commands/<x>.md` | D-05 | 20 lines; regex over the two workflow tables |
| T6 | extend `test_version_consistency._no_expiry_docs` with `docs/PRD.md`, `docs/README.md`, `docs/UI-GUIDE.md`, `docs/reports/*.md`, and the regex with `\b\d+(\.\d+)?/\d+(\.\d+)?/\d+(\.\d+)?\b` version lists and `\d+-arm × \d+-task` | D-03, D-08 | 10 lines |
| T7 | `test_install_surfaces_name_every_component`: README "What gets installed" and the `install`/`uninstall` docstrings name every `COMPONENTS` target directory | D-16 | 15 lines |

Not proposed: a generic "every backticked path resolves" lint over `docs/` (216 candidates, three quarters false positives; it would be ignored within a week), and any check over `docs/research/`, `docs/analysis/`, dated plans or `docs/archive/`.

## 3. Owner questions

1. **Q1 Fix policy.** (a) Fix S2 and S3 in one `fix/docs-ssot` round, G1–G5, each group one commit; (b) S2 only, S3 to the backlog; (c) findings only, no fix round. **★ (a)**: 25 one-line edits, no behaviour change, and every S3 sits in a file an S2 already touches.
2. **Q2 `PROJECT_INDEX.md`.** (a) Hand-edit the four stale lines (D-02, D-11, D-12) and add it to T2/T3/T6; (b) regenerate it with `/sc:init a` and re-audit; (c) delete it, since README, AGENTS and ARCHITECTURE cover its content. **★ (a)**: regeneration re-copies whatever the generator knows today, which is how the `integration` line got in; deletion loses the "Counting things" section that other docs cite.
3. **Q3 Guards.** (a) T1, T3, T6, T7 (shape-based, no phrase table); (b) all seven, T2's phrase table capped at ten entries and reviewed when a release retires something; (c) none, rely on the durability rule. **★ (b)**: T2 is the only guard that catches a restated mechanism (D-01, D-24, D-13), the class behind most S2s; capped, it stays readable.
4. **Q4 Dated research and analysis docs (D-25).** (a) Leave them as records, no edit; (b) prepend a one-line "written against vX; `/sc:prompt`, `/sc:sc` since retired" note; (c) move the ones naming retired artifacts to `docs/archive/`. **★ (a)**: RULES_DOCS keeps pre-convention docs in place; the extractor's class filter (02 §3) already tells a future round to skip them.
5. **Q5 The two open draft plans** (`harness-expose-more` 2026-05-06, `doctor-unapplied-cleanup` 2026-08-23). (a) Set `status: deprecated` and move to `docs/archive/plans/`; (b) leave with `status: draft`; (c) ask their author. **★ (a)**: both name artifacts that were never built or since removed (`diff_exposer.py`, `MCP_Context7.md`); `test_plan_checklist.py` ignores drafts, so they cost nothing but mislead `/sc:load`.
6. **Q6 README research numbers (D-04).** (a) Delete the confidence targets, minute figures and the min/target thresholds; keep the depth table at the config's columns (sources, hops); (b) define them in `RESEARCH_CONFIG.md` so README is backed; (c) leave. **★ (a)**: the shipped content never implemented them, so adding them to the config is a behaviour change with no measurement behind it (`content-quality.md` Improvement Workflow step 1).
7. **Q7 `core/README.md` kernel line (D-06).** (a) Drop the token figure and the class list; point at `RULES.md` and `TestCoreLiteSplit` for the budget; (b) update to "~1.5k, five classes"; (c) delete the row's description. **★ (a)**: (b) is stale at the next rule; the test owns the number.
8. **Q8 CLI self-description (D-15).** (a) `superclaude --help` and `pyproject.description`: "A Claude Code content framework: a CLI that installs commands, agents, modes, rules and hooks, plus a pytest plugin"; `update --help`: "Re-install every component where an install exists"; (b) leave. **★ (a)**: three strings, and `pm-agent` is retired.
9. **Q9 Codex guides** (`last_verified: 2026-08-22`). (a) Fix only D-08, D-09, D-12, D-13 in them and bump `last_verified`; (b) a full re-verification pass of 01–08 (half a day); (c) archive 01–08 beside 09–10. **★ (a)**: the set is self-aware (its README says re-measure when `git log <measured_at>..HEAD -- src/` is non-empty); nothing in this round showed a wrong principle, only dead names.
10. **Q10 `evals/README.md`** (outside the brief's doc scope, but it is the SSOT doc the PRD cites). (a) Fix "4-arm" and "7 matrix tasks" in the same round, or replace them with "the arms in `run_eval.py` `ARMS`" and "tasks without `canary_only`"; (b) leave for the next eval round. **★ (a)**: PRD will point at it after D-08.

## 4. Risks and do-not-do

- No doc edit in this round: the branch holds this folder and `tools/` only.
- Prose-only fixes still run the full suite before merge (`test_version_consistency` reads README, CLAUDE, AGENTS and the shipped READMEs; `test_install_docs` reads README's install sections).
- `make release`'s canary gate watches `src/superclaude/core` and `hooks.json`; neither is in G1–G5 (the `cli/main.py` edits are docstrings), so no canary run is needed.
- Do not "fix" a dated research doc, a CHANGELOG entry about a past release, or an external claim (03 §Out of scope).
- Do not add a lint whose false-positive rate was measured above zero in 02 §3 without the class filter that removed it.
