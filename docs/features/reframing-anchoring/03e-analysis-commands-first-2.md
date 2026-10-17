# 03e — Phase 2 content value classification: commands (first half) — part 2 of 3

> Continuation of [part 1](./03e-analysis-commands-first-1.md) (split by size; content unchanged).

## 2. Classification table (continued)

| File | Section | Class | ~Bytes | Reason | Failure (B) | Mechanism/exhortation (B) | Quote |
|---|---|---|---|---|---|---|---|
| explain | syntax | C | 131 | Flags |  |  | `[--level basic\|intermediate\|advanced]` |
| explain | flow | A | 202 | Analyze/assess/structure/generate/validate: default |  |  | `Structure: Progressive complexity` |
| explain | flags | C | 493 | interactive format definition is the only non-obvious fact |  |  | `one comprehension question between steps` |
| explain | tools | A | 152 | Trivial |  |  | `Agent: Complex explain delegate` |
| explain | examples | D | 658 | Illustrations; 'C7 patterns' is unexplained jargon |  |  | ``react-hooks --level intermediate --context react` \| C7 patterns` |
| explain | gotchas | D | 231 | symbolic-first and 'check memory for expertise' are generic |  |  | `Check user context/memory for expertise level` |
| explain | bounds | D | 198 | Boilerplate |  |  | `reveals sensitive information` |
| explain | handoff | C | 56 | Routing |  |  | `/sc:implement /sc:improve /sc:document` |
| git | description | C | 302 | Routing + which ops need confirmation |  |  | `push --force, reset --hard and rebase each still need their own confirmation` |
| git | role/mission | D | 121 | Duplicate |  |  | `smart commit messages and workflow guidance` |
| git | syntax | C | 110 | Flags |  |  | `[--pr-status] [--from-pr PR#\|URL]` |
| git | flow | A | 289 | Analyze state/validate/execute/report: default |  |  | `read the repo state and pending changes` |
| git | flags | C | 566 | --from-pr procedure incl. stash question |  |  | `with uncommitted changes, first ask whether to stash them or stop` |
| git | tools | A | 119 | Trivial |  |  | `Bash: run git and gh commands` |
| git | pr_status_integration | C | 496 | gh json fields; state→dot mapping is D tone. Shorten to the command line |  |  | `gh pr view --json state,reviewDecision,isDraft` |
| git | from_pr | C | 444 | 'claude --from-pr is a start-up option; never run from Bash' is the one fact; rest duplicates flags |  |  | `never run it from Bash` |
| git | examples | A | 603 | Force-push to main refusal is default Claude Code behaviour |  |  | `force-pushing main/master destroys teammates' work` |
| git | gotchas | A | 374 | never amend / retest after merge / confirm base branch: default |  |  | `make new commits; never amend unless asked` |
| git | bounds | D | 282 | Boilerplate |  |  | `resolves complex merges that need manual review` |
| git | safety_rules | C | 273 | Which ops skip the second confirm (project policy); partially duplicates description |  |  | `the op the user typed into /sc:git; no second confirm` |
| git | handoff | C | 36 | Routing |  |  | `/sc:test /sc:build` |
| help | description | C | 179 | Routing |  |  | `Not for "help me" with a task` |
| help | role/mission | D | 103 | Duplicate |  |  | `List all /sc commands` |
| help | syntax | C | 50 | Flags |  |  | `/sc:help [command-name] [--flags]` |
| help | flow | C | 264 | What to display per argument |  |  | `a command-name → that command's syntax, its flags, and the "Not for" line` |
| help | flags | C | 232 | Where flags live; effort levels native |  |  | `Effort levels are Claude Code native, not managed by superclaude` |
| help | commands | C | 1945 | The deliverable itself: 35-line routing list |  |  | `intent: capture a request in the requester's own words before analysis` |
| help | scope_map | C | 620 | Disambiguation between overlapping commands — highest-value routing text in scope |  |  | `analyze (static quality metrics) \| review (PR/diff-level) \| reflect (post-impl self-check)` |
| help | examples | A | 301 | 'help does not execute' is obvious |  |  | `help reference-only. Shows info, no exec` |
| help | gotchas | D | 185 | stale-list refers to commands/sc/ (install path, fine) but is self-doubt; flag-docs duplicates flags |  |  | `cmd list may go stale` |
| help | bounds | D | 207 | Boilerplate |  |  | `executes commands, creates files, activates modes` |
| help | handoff | C | 45 | Routing |  |  | `/sc:recommend /sc:[command]` |
| implement | description | C | 254 | Routing |  |  | `Not for a routine function, bug fix or single-file edit` |
| implement | role/mission | D | 137 | Duplicate |  |  | `agent delegation and MCP integration` |
| implement | syntax | C | 159 | Flags |  |  | `[--plan docs/plans/...] [--safe] [--with-tests]` |
| implement | flow 1 Load | C | 300 | Split-plan index/phase file reading order |  |  | `a split plan's index is read here and each phase file it links when that phase starts` |
| implement | flow 2 Plan | D | 180 | 'verify simplest viable approach' is exhortation; 'follow the plan's task order exactly' HARDENS A3 (prior plan becomes law before any evidence check) | (A3 — anti-pattern) | exhortation / anchor-hardening | `with --plan, follow the plan's task order exactly` |
| implement | flow 3 Checkpoint | C | 280 | >3-file approval gate and 'plan invocation is the approval' — project policy; 'ask only before departing from the plan' is the only re-plan permission |  |  | `ask only before departing from the plan` |
| implement | flow 4 Execute | A | 150 | Write code following conventions |  |  | `write the code following the framework's conventions` |
| implement | flow 5 Phase Gate | B | 190 | Re-plan trigger after each phase: build+run, then ask whether the next phase is already solved. Only explicit re-evaluation of a prior plan against evidence in scope. Narrow (only 'skip', never 'change') | A3 (re-plan trigger) | mechanism — checkpoint after each phase | `"Does this already solve the next phase's problem?" If yes, skip with reason` |
| implement | flow 6 Validate | A | 90 | Run checks and verify commands |  |  | `run each task's verify command` |
| implement | flow 7 Integrate | C | 680 | Deviations heading, checkbox/status semantics, README phase: — project conventions. Dense; could be a table |  |  | ``status: complete` with an open box is a defect` |
| implement | flags | C | 804 | Flag semantics incl. collision with global --plan and --safe-mode |  |  | `unrelated to the global --plan, whose 5-line-plan directive does not apply` |
| implement | tools | A | 159 | Trivial |  |  | `Write/Edit: Code gen` |
| implement | examples table | D | 330 | Illustrations; 'C7 Vue patterns' jargon |  |  | ``dashboard widget --framework vue` \| C7 Vue patterns` |
| implement | examples scope-creep | A | 430 | Not refactoring adjacent code is default |  |  | `"Add logout button" does not authorize refactoring adjacent code` |
| implement | gotchas status-check / scope-discipline | D | 200 | [R02] pointer to a rule elsewhere; scope discipline is A |  |  | `Run [R02 Status Check] pre-impl` |
| implement | gotchas workflow-fanout | C | 209 | Subagent writes discarded; main loop applies and runs checkpoint |  |  | `fan-out subagents RETURN code/results — subprocess writes discarded` |
| implement | bounds | D | 219 | Boilerplate |  |  | `conflicts with security, or overrides safety` |
| implement | handoff | C | 36 | Routing |  |  | `/sc:test /sc:build` |
| improve | description | C | 261 | Routing |  |  | `Not for one function or a small refactor` |
| improve | role/mission | D | 141 | Duplicate |  |  | `systematic improvements to code quality` |
| improve | syntax | C | 113 | Flags |  |  | `[--type quality\|performance\|maintainability\|style]` |
| improve | flow | A | 241 | Analyze/plan/execute/validate/document: default |  |  | `Validate: Functionality preserved` |
| improve | flags --type performance baseline | B | 200 | Hard stop: no performance work without a measured baseline; routes to /sc:analyze. Gate that keeps a prompt-supplied 'it is slow because X' from being acted on before measurement | A1/R1 (suspected cause in prompt) | mechanism — stop + reroute (performance type only) | `performance needs a measured baseline first, else stop` |
| improve | flags --safe / --interactive | C | 282 | Flag semantics |  |  | `changes to exported functions, config files or shared modules are listed as proposals` |
| improve | examples | D | 273 | Illustrations; row 3 duplicates the baseline flag |  |  | `Error: run /sc:analyze --focus perf first` |
| improve | gotchas | D | 408 | R18 pointer + exhortation; halo-improvement is scope discipline (A) |  |  | `"safer/better" alone insufficient justification` |
| improve | bounds | D | 268 | Boilerplate; fallback 'ask when scope exceeds target' is A |  |  | `Ask user when improvement scope exceeds target boundary` |
| improve | handoff | C | 38 | Routing |  |  | `/sc:test /sc:analyze` |
| index | description | C | 237 | Routing |  |  | `Not for documenting one file — use /sc:document` |
| index | role/mission | D | 131 | Duplicate |  |  | `knowledge base under docs/reports/` |
| index | syntax | C | 94 | Flags |  |  | `[--type docs\|api\|structure\|readme] [--format md\|json\|yaml]` |
| index | flow | A | 333 | Generic; step 5 MANUAL-marker preservation is a C fact (~60 B) |  |  | `preserve sections marked <!-- MANUAL -->` |
| index | flags | C | 265 | Format semantics |  |  | `json or yaml writes the same stem with that extension` |
| index | outputs | C | 554 | Output files, in-place update rules, metrics |  |  | `in an existing README edit only the install, usage and api sections` |
| index | distinction | C | 196 | Routing vs index-repo |  |  | `index-repo: Minimal index (~3KB), token-efficient` |
| index | tools | A | 274 | Trivial |  |  | `Write: Doc creation + cross-referencing` |
| index | examples | D | 598 | Illustrations; monorepo example routes to index-repo (duplicate of distinction) |  |  | `Indexing entire large monorepo in one pass exhausts context` |
| index | gotchas | D | 193 | living-doc duplicates outputs; token-budget is A |  |  | `Use structural reading, not full file reads` |
| index | bounds | D | 230 | Boilerplate |  |  | `override manual docs, generate without analysis, bypass standards` |
| index | handoff | C | 43 | Routing |  |  | `/sc:implement /sc:improve` |
| index-repo | description | C | 232 | Routing |  |  | `Not for a routine code lookup — use Glob or Grep` |
| index-repo | role/mission | D | 125 | Duplicate |  |  | `compact repo index (~3KB)` |
| index-repo | syntax | C | 58 | Modes |  |  | `[mode=create\|update\|quick]` |
| index-repo | flow | C | 453 | Output paths and 5KB validation |  |  | `confirm both files exist and each is under 5KB` |
| index-repo | tools | A | 217 | Trivial; 'files changed since last index' is a small C fact |  |  | `files changed since the last index (mode=update)` |
| index-repo | patterns | D | 482 | Entry-file globs the model knows; output lines duplicate flow |  |  | `Entry: pyproject.toml \| package.json \| Cargo.toml` |
| index-repo | examples | D | 462 | Illustrations; 'needs a git repo' restates tools |  |  | `the repo index needs a git repo` |
| index-repo | gotchas | C | 237 | structure-only (no file content) is a real output constraint; token-target duplicates flow |  |  | `output the file structure and each file's role, not file content` |
| index-repo | bounds | D | 217 | Boilerplate |  |  | `writes an index file over 5KB` |
| index-repo | handoff | C | 39 | Routing |  |  | `/sc:analyze /sc:index` |
| init | description | C | 244 | Routing |  |  | `Not for "set this up" on entering a repo — ask what to set up` |
| init | role/mission | D | 152 | Duplicate |  |  | `selectable init tasks for first-session onboarding` |
| init | syntax | C | 52 | Flags |  |  | `/sc:init [tasks] [--quick] [--full]` |
| init | flow | C | 698 | Menu-driven procedure; dependency batching; 'not saved' reporting when auto memory off |  |  | `memory entries stored (or listed as not saved when auto memory is off)` |
| init | flags | D | 157 | Two lines pointing elsewhere |  |  | `preset, defined in the Select step and the menu section` |
| init | menu | C | 1026 | Task letters, dependencies, presets — the UI |  |  | `Presets: --quick (a,b) \| --full (a,b,c,d,e,f,g,h,i)` |
| init | dependency_graph | C | 212 | Batch order; partially duplicates menu '(requires a)' |  |  | `Batch 2 (wait for prereq): b←a, d←c, g←a` |
| init | task_outputs | C | 635 | Artifact locations per task |  |  | `adr/0001-*.md, UI-GUIDE.md \| docs/ (project root)` |
| init | safety_rules | C | 1571 | Template source path, memory layout, auto-memory-off rule, idempotence. 'show diff before editing CLAUDE.md' and 'confirm before install' are A (~250 B) |  |  | `from ~/.claude/superclaude/templates/docs-scaffold/` |
| init | outputs | D | 323 | Duplicates task_outputs |  |  | `PROJECT_INDEX.md \| Project structure map (task a)` |
| init | tools | A | 268 | Trivial; Agent(repo-index) routing is C (~40 B) |  |  | `Agent(repo-index): Delegate structure analysis for task (a)` |
| init | examples | D | 868 | Six usage rows + missing-prerequisite example restating dependency_graph |  |  | `Task (d) requires (c). Add dependency check?` |
| init | gotchas | A | 129 | Do not overwrite user config: default |  |  | `Verify files do not already exist before creating` |
| init | bounds | D | 430 | Restates flow and safety_rules |  |  | `auto-executes tasks the user did not select` |
| init | handoff | C | 49 | Routing |  |  | `/sc:load /sc:implement /sc:test` |
| insight | description | C | 258 | Routing |  |  | `Not for "let me note this" in passing — write no entry` |
| insight | role/mission | D | 146 | Duplicate |  |  | `per-project JSONL for human and tool analysis` |
| insight | syntax | C | 85 | Flags |  |  | `[--list] [--query key=value] [--stats] [--review]` |
| insight | flow | C | 1189 | Modes, dedup command, CLI-only append, review/promote/discard procedure |  |  | `run `superclaude insight list --limit 20` to check recent entries` |
| insight | flags | D | 255 | Four lines pointing back to flow |  |  | `read mode, defined in the Read modes step` |
| insight | outputs | C | 344 | Per-mode output |  |  | ``--list` \| Formatted recent insights (last 20)` |
| insight | storage files + memory link | C | 400 | File paths; memory vs insight distinction |  |  | `Memory = LLM read. Insight = human/tool query` |
| insight | storage Auto-produce / Auto-harvest | D | 1313 | Hook internals (Stop fingerprint, SessionEnd/PreCompact harvest, sidechain skip, ledger). The command executor never runs these; repo/maintainer leak |  |  | `the gate compare a `SessionStart` tree fingerprint against the current one` |
| insight | schema | C | 881 | Required/optional fields, type taxonomy |  |  | `annotation: relevance link to existing insight (need ref_ts` |
| insight | tools | C | 157 | All I/O through the CLI |  |  | `All file I/O on insights.jsonl go through this CLI` |
| insight | script_reference | C | 774 | CLI invocations; ~40% duplicates flow |  |  | `superclaude insight discard --index 0,1,2      # one call, indices no shift` |
| insight | examples | D | 590 | Illustrations duplicating flow/outputs |  |  | ``/sc:insight --stats` \| Type counts` |
| insight | gotchas | C | 1301 | never-bare-python, discard-is-final + batch indices, promote-descending-indices are real facts; script-only-writes and review-requires-classification duplicate flow (~450 B D) |  |  | `go highest index first (`cmd_promote` pop by index)` |
| insight | bounds | D | 365 | Restates flow |  |  | `hand-edits insights.jsonl` |
| insight | handoff | C | 38 | Routing |  |  | `/sc:save /sc:analyze` |

## 3. Anchor-point map

| File | Moment | What arrives | B step before it? |
|---|---|---|---|
| agent | flow 1 Parse | task-description (action instruction) | none before Parse — 'identify the task type' frames first; task_protocol Phase 1 'Confirm scope, success criteria, blockers, acceptance tests' comes after and confirms with the user rather than inferring purpose |
| agent | flow 3 Monitor | delegate results | yes — gotchas: 'Judge the returned summary against the check written before dispatch' |
| agent | task_protocol Phase 4 | own Phase 2 plan | none — no re-plan trigger between Plan and Implement; 'escalate if stalled' only |
| analyze | flow 1-2 Discover/Scan | target + --focus (frame) + code comments/README read during scan | none — scan is 'per --focus'; evidence-fabrication gotcha is exhortation |
| analyze | rules_analysis | memory files with violated_rule tags (prior AI output) | none |
| auto-improve | flow 1 Parse | --eval-cmd / --metric (user-chosen objective = frame) | none — Phase 0 confirm is safety only; by design the metric is accepted as given |
| brainstorm | flow 1 Explore | topic (action instruction) | none — Socratic dialogue is where purpose could emerge, but no step says 'state the purpose and criterion' |
| brainstorm | flow 1 Explore | 00-intent.md (prior document) | partial — read first and mapped via coverage table (I0), but 'keep its wording as the anchor' forbids questioning it (R1 hardened) |
| brainstorm | flow 1-5 dialogue | user answers to option lists / ★ defaults | yes, post hoc — decision_modes: 'silent accept of ★' → delegated → mandatory audit. Nothing stops the ★ being offered |
| brainstorm | flow 5-6 Approve | own spec | yes — self_review: 'Claude does not review the spec itself in place of /sc:review' |
| build | flow 3 Execute | build error output | none (low anchor risk); error-path says stop and report |
| business-panel | flow 1-2 | market-analysis.md / pitch doc (document anchor; its premise) | none — experts apply frameworks to the doc as given; no premise check before Analyze |
| cleanup | flow 1 Analyze | target + --type (frame: user says 'dead code') | none |
| cleanup | flow 2 Plan → 3 Execute | own cleanup plan | none — no re-plan trigger; Validate is post hoc tests |
| design | flow 1 Analyze | --from / 01-discovery / 00-intent (document + prior plan) | none before; after: flow 6 'where the design cannot satisfy the intent' and flow 7 coverage table (post hoc B) |
| design | flow 2 Plan → 3 Design | own design approach | partial — flow 7 'a requirement no section covers goes under Areas of concern' re-checks after the fact |
| document | flow 1 Analyze | target + existing docs | none — flow 2 'name the audience and what it needs' is audience, not purpose/criterion |
| estimate | flow 1 Analyze | target, often with a prior number ('I think 2 days') — A1 | none — no step sizes before reading the user's number; relative-size gotcha only resists the unit (hours/days) |
| explain | flow 1-2 | target + --level | none (low stakes) |
| git | flow 1-3 | operation + --from-pr body/comments (document) | none — safety_rules gate destructive ops only; PR body is loaded as context with no check |
| help | flow 1 | command-name | n/a |
| implement | flow 1 Load | --plan doc (prior plan A3 + document A2) | none — and flow 2 'follow the plan's task order exactly' hardens it; flow 3 'ask only before departing from the plan' is the only exit |
| implement | flow 5 Phase Gate | own progress vs remaining plan | yes — 'Does this already solve the next phase's problem? If yes, skip with reason' (skip-only re-plan) |
| implement | flow 2 Plan (delegation) | subagent code/results | none — workflow-fanout says main loop applies; no pre-dispatch check like agent.md's |
| improve | flow 1 Analyze | target + --type (user's diagnosis: 'performance') | yes for performance only — 'performance needs a measured baseline first, else stop'; none for quality/maintainability/style |
| index | flow 1 Analyze | existing README/API.md | none (edits in place; MANUAL sections preserved — not an anchor issue) |
| index-repo | flow 1-3 | entry files | n/a |
| init | flow 1-2 | existing CLAUDE.md / config | none needed — safety_rules show diff before applying |
| insight | flow 7 Review | harvested INSIGHT: markers (prior AI/user output) | none — review-requires-classification only forces a type label, not a truth check |

**I0 check (purpose + success criterion stated before acting):**

- agent.md is the only file with a criterion gate: `Phase 1 - Clarify: Confirm scope, success criteria, blockers, acceptance tests` and `Phase 3 - Iterate: no implementation until Phase 1 scope, success criteria and acceptance checks are confirmed`. It asks the user to confirm a criterion; it does not make the model infer the unstated purpose or look beyond the named target, and flow step 1 (`identify the task type`) frames before it runs.
- brainstorm.md carries purpose only when a prior `00-intent.md` exists (`read it first and keep its wording as the anchor`), and then forbids questioning it.
- design.md checks intent only after the design exists (`where the design cannot satisfy the intent`).
- The other 16 files have no purpose or criterion step. implement, analyze, estimate, cleanup, improve, document, business-panel all begin by analyzing the named target inside the frame the request supplies.

## 4. Totals per class

| Class | Rows | ~Bytes | Share |
|---|---|---|---|
| A | 34 | 8204 | 10% |
| B | 12 | 3421 | 4% |
| C | 126 | 44557 | 55% |
| D | 82 | 25078 | 31% |
| Total classified | 252 | 81261 | 100% |

Notes on the totals:
- Mixed rows (`C/A`, `B/D`) were split half-and-half.
- C is inflated by internal duplication: paths and flag semantics are typically stated two or three times per file (flow step, `<flags>`, `<outputs>`, `<gotchas>`, `<examples>`). Reducing each C fact to one statement would cut C by roughly 30% (≈13 KB) without losing a fact.
- Every file carries ~0.5 KB of fixed boilerplate that is A or D: `<role>` (duplicate of description), `<tools>`, `<bounds>`, and the usage-example table. Across 19 files that is ≈10 KB.
- B is 11 rows / ≈3.4 KB (4%), concentrated in brainstorm (4), design (2), agent (2), implement (1), improve (1), estimate (1). None of them is a purpose-inference step; the closest is agent.md's user-confirmed success criterion.
