# Phase 2 content-value classification — agents (first half) — part 2 of 3

> Continuation of [part 1](./03c-analysis-agents-first-1.md) (split by size; content unchanged).

## 2. Classification table (continued)

| File | Section | Class | Reason | Failure (B) | Mechanism / exhortation (B) | Quote | ~Bytes |
|---|---|---|---|---|---|---|---|
| git-workflow | memory_guide | D | 12x identical header; 'verify against current state' is an A2 exhortation with no mechanism; category labels are weak C; 'Related:' cross-refs unused |  |  | "verify against current state before acting on them" | 507 |
| git-workflow | examples | D | restates Ask First and pr_integration |  |  | "asks to confirm (as a delegated subagent: returns the message" | 533 |
| git-workflow | gotchas (new-commit-not-amend, default-branch-warn) | A | Claude Code already creates new commits and warns on main; confident |  |  | "always create new commits — never amend unless" | 300 |
| git-workflow | gotchas (staged-secret-scan) | D | models usually check; file-glob list is project policy; not confident A |  |  | "Never stage `.env`, `.env.*`, `credentials.json`" | 230 |
| git-workflow | gotchas (stash-before-worktree-delete) | C | non-obvious git fact the model may not raise |  |  | "a worktree delete strands them" | 133 |
| git-workflow | bounds | C | <fallback> routing to sibling agents is project knowledge; <does> duplicates mission (D ~120 B); 'ask the user when >N' thresholds unmeasurable (D) |  |  | "escalate to system-architect for branching-strategy questions" | 433 |
| git-workflow | handoff | C | routing to next /sc: command; model cannot know the catalogue |  |  | "handoff next=" | 47 |
| insight-analyst | frontmatter | C | `description` is what CC auto-delegation routes on; name/memory/color/disallowedTools are config |  |  | "find and present relevant past insights from `.claude/insights.jsonl`" | 424 |
| insight-analyst | role | D | mission repeats the description; mindset is persona/exhortation a model needs no telling |  |  | "Semantic relevance beats keyword matching" | 263 |
| insight-analyst | focus | D | restates actions; 'semantic beats keyword' is an exhortation |  |  | "Semantic relevance beats keyword matching" | 326 |
| insight-analyst | actions | C | jq over a named file, `superclaude insight append --json` with required fields `type`/`insight`/`ref_ts` |  |  | "superclaude insight append --json" | 856 |
| insight-analyst | outputs | A | deliverable list a model produces for this task type unprompted |  |  | "Results: formatted insight list with relevance reasoning" | 227 |
| insight-analyst | tool_guidance (Ask First thresholds) | D | thresholds unmeasurable or judgement calls; gate itself is C-ish but values are arbitrary (backend: '>2 tables' here vs '>3 services' in bounds) |  |  | "the user must confirm each relevance link" | 80 |
| insight-analyst | tool_guidance (Proceed/Fallback/Never) | C | jq-on-file, python fallback, never-modify-entries are project facts |  |  | "if `jq` is unavailable, use a Python one-liner" | 526 |
| insight-analyst | tool_guidance (subagent-cannot-ask boilerplate) | D | identical 330-byte paragraph in all 12 files; a real stop-and-return gate, but one copy in the loader would do — 11 copies are duplicate |  |  | "As a delegated subagent Claude cannot ask mid-task" | 330 |
| insight-analyst | checklist | C | no-duplicate-annotation-per-ref_ts and ref-must-exist are data-model facts (also in gotchas) |  |  | "No duplicate annotations exist for the same `ref_ts` target" | 288 |
| insight-analyst | memory_guide | D | 12x identical header; 'verify against current state' is an A2 exhortation with no mechanism; category labels are weak C; 'Related:' cross-refs unused |  |  | "verify against current state before acting on them" | 539 |
| insight-analyst | examples | D | restates actions |  |  | "runs `jq` over insights.jsonl by topic" | 401 |
| insight-analyst | gotchas | C | orphaned ref_ts, --stats exclusion, exact tz match are data-format facts |  |  | "inconsistent timezone-offset formats (+09:00 vs +0900) break links" | 434 |
| insight-analyst | bounds | C | <fallback> routing to sibling agents is project knowledge; <does> duplicates mission (D ~120 B); 'ask the user when >N' thresholds unmeasurable (D) |  |  | "insight capture (that is /sc:insight's job)" | 385 |
| insight-analyst | handoff | C | routing to next /sc: command; model cannot know the catalogue |  |  | "handoff next=" | 50 |
| learning-guide | frontmatter | C | `description` is what CC auto-delegation routes on; name/memory/color/disallowedTools are config |  |  | "Use when the user wants to learn a concept" | 430 |
| learning-guide | role | D | mission repeats the description; mindset is persona/exhortation a model needs no telling |  |  | "Teach understanding, not memorization" | 391 |
| learning-guide | focus | A | pedagogy vocabulary; model teaches progressively unprompted |  |  | "step-by-step pacing, prerequisite mapping, difficulty gradient" | 406 |
| learning-guide | actions | A | assess level → chunk → demo → exercise → verify; subagent single-reply note is C (~150 B) |  |  | "Assess the learner's current skill" | 646 |
| learning-guide | outputs | A | deliverable list a model produces for this task type unprompted |  |  | "Tutorials: step-by-step guides with examples and exercises" | 289 |
| learning-guide | tool_guidance (Ask First thresholds) | D | thresholds unmeasurable or judgement calls; gate itself is C-ish but values are arbitrary (backend: '>2 tables' here vs '>3 services' in bounds) |  |  | "fix a long learning path or skill-assessment criteria as final" | 80 |
| learning-guide | tool_guidance (Proceed/Never) | A | lists ordinary actions and obvious prohibitions (no prod migrations, no fabricated sources, no secrets) |  |  | "Never: complete homework directly" | 259 |
| learning-guide | tool_guidance (Symbolic-First) | D | generic read-strategy preference repeated in 9 files; models already grep before reading; belongs in one shared place if kept |  |  | "query overview → definition → references before whole-file Read" | 200 |
| learning-guide | tool_guidance (subagent-cannot-ask boilerplate) | D | identical 330-byte paragraph in all 12 files; a real stop-and-return gate, but one copy in the loader would do — 11 copies are duplicate |  |  | "As a delegated subagent Claude cannot ask mid-task" | 330 |
| learning-guide | checklist | D | A except the 'example was run / marked unverified' honesty gate (off-list) |  |  | "an example that was not run is marked unverified" | 322 |
| learning-guide | memory_guide | D | 12x identical header; 'verify against current state' is an A2 exhortation with no mechanism; category labels are weak C; 'Related:' cross-refs unused |  |  | "verify against current state before acting on them" | 506 |
| learning-guide | examples | A | trigger→behavior pairs a model would produce anyway |  |  | "walks Promise → async/await with runnable snippets" | 426 |
| learning-guide | gotchas (answer-not-lecture) | A | models answer the question asked; also a frame-lock reinforcer |  |  | "do not expand it into a full tutorial unless" | 129 |
| learning-guide | gotchas (level-mismatch) | C | where to find the learner's level (MEMORY.md / task context) — short C |  |  | "check the agent's MEMORY.md or the context passed in the task" | 180 |
| learning-guide | bounds | C | <fallback> routing to sibling agents is project knowledge; <does> duplicates mission (D ~120 B); 'ask the user when >N' thresholds unmeasurable (D) |  |  | "escalate to socratic-mentor for guided discovery" | 424 |
| learning-guide | handoff | C | routing to next /sc: command; model cannot know the catalogue |  |  | "handoff next=" | 56 |
| performance-engineer | frontmatter | C | `description` is what CC auto-delegation routes on; name/memory/color/disallowedTools are config |  |  | "Use when latency, throughput or memory is measured" | 359 |
| performance-engineer | role | D | mission repeats the description; mindset is persona/exhortation a model needs no telling |  |  | "Measure first, optimize second" | 242 |
| performance-engineer | focus | A | generic perf domains |  |  | "Core Web Vitals, bundle size, asset delivery" | 370 |
| performance-engineer | actions | A | baseline → profile → fix → paired measurement; model does this; 'not intuition' is an A1 exhortation |  |  | "Find the real bottleneck through profiling, not intuition" | 324 |
| performance-engineer | outputs | A | deliverable list a model produces for this task type unprompted |  |  | "Reports: before/after metrics and the strategy used" | 292 |
| performance-engineer | tool_guidance (Ask First thresholds) | D | thresholds unmeasurable or judgement calls; gate itself is C-ish but values are arbitrary (backend: '>2 tables' here vs '>3 services' in bounds) |  |  | "caching strategies, query rewrites, critical-path changes" | 80 |
| performance-engineer | tool_guidance (Proceed/Never) | A | lists ordinary actions and obvious prohibitions (no prod migrations, no fabricated sources, no secrets) |  |  | "Never: optimize without baseline, skip validation" | 315 |
| performance-engineer | tool_guidance (Symbolic-First) | D | generic read-strategy preference repeated in 9 files; models already grep before reading; belongs in one shared place if kept |  |  | "query overview → definition → references before whole-file Read" | 200 |
| performance-engineer | tool_guidance (subagent-cannot-ask boilerplate) | D | identical 330-byte paragraph in all 12 files; a real stop-and-return gate, but one copy in the loader would do — 11 copies are duplicate |  |  | "As a delegated subagent Claude cannot ask mid-task" | 330 |
| performance-engineer | checklist | D | restates actions; 'with its value and source' honesty gate is off-list |  |  | "a metric that was not measured is marked unverified" | 445 |
| performance-engineer | memory_guide | D | 12x identical header; 'verify against current state' is an A2 exhortation with no mechanism; category labels are weak C; 'Related:' cross-refs unused |  |  | "verify against current state before acting on them" | 536 |
| performance-engineer | examples | A | trigger→behavior pairs a model would produce anyway |  |  | "profile representative endpoints, surface N+1 and slow queries" | 388 |
| performance-engineer | gotchas (benchmark-or-stop) | A | third statement of 'no claim without measurement' |  |  | "intuition is not evidence" | 110 |
| performance-engineer | gotchas (scope-discipline) | D | ANTI-remedy: 'only what was asked' reinforces I0/R2 frame lock |  |  | "profiling one endpoint is no license to refactor adjacent paths" | 130 |
| performance-engineer | gotchas (status-check) | B | ordering: confirm the premise (bottleneck exists) before optimizing — the only A1/R1 check in scope | R1 (A1) | mechanism (ordering) — narrow; nothing says to doubt the user's named cause | "search the current code to confirm the bottleneck still exists" | 110 |
| performance-engineer | bounds | C | <fallback> routing to sibling agents is project knowledge; <does> duplicates mission (D ~120 B); 'ask the user when >N' thresholds unmeasurable (D) |  |  | "escalate to backend-architect for query/API restructuring" | 434 |
| performance-engineer | handoff | C | routing to next /sc: command; model cannot know the catalogue |  |  | "handoff next=" | 52 |
| project-initializer | frontmatter | C | `description` is what CC auto-delegation routes on; name/memory/color/disallowedTools are config |  |  | "Use when the user asks to set up a repository" | 349 |
| project-initializer | role | D | mission repeats the description; mindset is persona/exhortation a model needs no telling |  |  | "Detect what exists, propose what is missing" | 259 |
| project-initializer | focus | D | restates <tasks>; duplicate |  |  | "CLAUDE.md generation, dependency install, test baseline capture" | 389 |
| project-initializer | tasks | C | task names, idempotency contract and dependency edges |  |  | "depends on structure-analysis; enhance, never overwrite" | 919 |
| project-initializer | execution_plan | C | batch shape from deps; the 'add dependency-check?' question is a real gate but on a data dependency, not an anchor |  |  | "Dependencies must be installed before running tests. Add dependency-check?" | 585 |
| project-initializer | task_details (detection heuristics) | A | pyproject/package.json/Cargo detection, lint-config names, test runners — model knows |  |  | "detects pyproject.toml, package.json, Cargo.toml, go.mod, or pom.xml" | 1319 |
| project-initializer | task_details (memory routing) | C | main-session auto memory vs agent memory, what to skip, delegated-return rule — the model cannot know this |  |  | "Project memory is the main session's auto memory folder, never this agent's own" | 900 |
| project-initializer | actions | C | menu + selection protocol is the project's design — but 'recommended preset' bakes in an R3 starred default |  |  | "returns the menu with a recommended preset and stops" | 745 |
| project-initializer | outputs | C | artefact locations per task (docs/reports/PROJECT_INDEX.md, project memory) |  |  | "Index: docs/reports/PROJECT_INDEX.md from structure-analysis" | 551 |
| project-initializer | tool_guidance (Ask First thresholds) | D | thresholds unmeasurable or judgement calls; gate itself is C-ish but values are arbitrary (backend: '>2 tables' here vs '>3 services' in bounds) |  |  | "install deps (dependency-check), modify existing CLAUDE.md" | 80 |
| project-initializer | tool_guidance (Proceed/Never) | A | lists ordinary actions and obvious prohibitions (no prod migrations, no fabricated sources, no secrets) |  |  | "Never: delete existing files, overwrite CLAUDE.md without a diff" | 390 |
| project-initializer | tool_guidance (Symbolic-First) | D | generic read-strategy preference repeated in 9 files; models already grep before reading; belongs in one shared place if kept |  |  | "query overview → definition → references before whole-file Read" | 200 |
| project-initializer | tool_guidance (subagent-cannot-ask boilerplate) | D | identical 330-byte paragraph in all 12 files; a real stop-and-return gate, but one copy in the loader would do — 11 copies are duplicate |  |  | "As a delegated subagent Claude cannot ask mid-task" | 330 |
| project-initializer | checklist | D | restates actions |  |  | "Interactive menu presented and the user's selection captured" | 343 |
| project-initializer | memory_guide | D | 12x identical header; 'verify against current state' is an A2 exhortation with no mechanism; category labels are weak C; 'Related:' cross-refs unused |  |  | "verify against current state before acting on them" | 496 |
| project-initializer | examples | D | restates actions; second row pre-selects tasks — an R3 starred default built into the example |  |  | "structure-analysis, claude-md, conventions-learning, memory-init preselected" | 490 |
| project-initializer | gotchas (check-existing) | A | models check before overwriting |  |  | "never overwrite user work" | 110 |
| project-initializer | gotchas (make-deploy, uv-not-pip) | D | repo-only leak (valid only in superclaude's own repo) |  |  | "use `make deploy` to install, not npm/pip install" | 396 |
| project-initializer | bounds | C | <fallback> routing to sibling agents is project knowledge; <does> duplicates mission (D ~120 B); 'ask the user when >N' thresholds unmeasurable (D) |  |  | "escalate to system-architect for architecture questions" | 568 |
| project-initializer | handoff | C | routing to next /sc: command; model cannot know the catalogue |  |  | "handoff next=" | 55 |
| project-manager | frontmatter | C | `description` is what CC auto-delegation routes on; name/memory/color/disallowedTools are config |  |  | "Use when asked to record a pattern" | 452 |
| project-manager | role | D | mission repeats the description; mindset is persona/exhortation a model needs no telling |  |  | "Experience becomes knowledge through immediate documentation" | 306 |
| project-manager | focus (paths) | C | where patterns/mistakes live is a project fact |  |  | "docs/memory/patterns/, mistakes → docs/memory/mistakes/" | 130 |
| project-manager | focus (rest) | D | lifecycle restated in <lifecycle>; 'never retry without understanding' restated in <self_correction> |  |  | "keep docs minimal, dated, referenced and deduplicated" | 272 |
| project-manager | lifecycle | C | memory keys, file names, slug rule, main-vs-delegated split |  |  | "session_[date]_[branch-slug]" | 1302 |
| project-manager | self_correction | B | failure-triggered re-plan: stop, investigate, document cause, choose a DIFFERENT approach — the only re-plan rule outside deep-researcher | A3 | mechanism (trigger = command failure) — covers failures only, not evidence that invalidates a plan; no compaction re-entry | "never re-runs a failed command without understanding why" | 364 |
| project-manager | actions | C | which artefact each trigger writes and that CLAUDE.md edits are Ask First |  |  | "write them to docs/memory/patterns/" | 433 |
| project-manager | quality | A | dated/minimal/deduplicated docs — generic hygiene |  |  | "drops outdated, verbose, abstract, unused (>6mo), or duplicate entries" | 239 |
| project-manager | outputs | C | file paths for patterns/mistakes/sessions |  |  | "Sessions: session summaries persisted to `.claude/memories/`" | 247 |
| project-manager | tool_guidance (Ask First thresholds) | D | thresholds unmeasurable or judgement calls; gate itself is C-ish but values are arbitrary (backend: '>2 tables' here vs '>3 services' in bounds) |  |  | "delete memories, modify CLAUDE.md" | 80 |
| project-manager | tool_guidance (Proceed/Never) | A | lists ordinary actions and obvious prohibitions (no prod migrations, no fabricated sources, no secrets) |  |  | "Never: run implementations directly, skip documentation" | 260 |
| project-manager | tool_guidance (Symbolic-First) | D | generic read-strategy preference repeated in 9 files; models already grep before reading; belongs in one shared place if kept |  |  | "query overview → definition → references before whole-file Read" | 200 |
| project-manager | tool_guidance (subagent-cannot-ask boilerplate) | D | identical 330-byte paragraph in all 12 files; a real stop-and-return gate, but one copy in the loader would do — 11 copies are duplicate |  |  | "As a delegated subagent Claude cannot ask mid-task" | 330 |
| project-manager | checklist | D | 'TaskCreate for >=3 steps' is a C tool fact (~60 B); rest duplicates lifecycle |  |  | "TaskCreate used for tasks of >=3 steps" | 268 |
| project-manager | memory_guide | D | 12x identical header; 'verify against current state' is an A2 exhortation with no mechanism; category labels are weak C; 'Related:' cross-refs unused |  |  | "verify against current state before acting on them" | 634 |
| project-manager | examples | D | restates lifecycle; '## Next actions' heading is a C detail (~40 B) |  |  | "surface next-action candidates from the session record's `## Next actions`" | 498 |
| project-manager | gotchas (delegation-check) | C | 'only the main session can spawn' subagents is a runtime fact; threshold is arbitrary |  |  | "reserve sub-agents for >=3 independent parallel streams" | 190 |
| project-manager | gotchas (intent-confirm) | D | exhortation; I0 near-miss |  |  | "restate the user's intent before non-trivial work" | 140 |
| project-manager | gotchas (root-cause-not-symptom) | A | model distinguishes cause from symptom when asked to document a mistake |  |  | "must explain why the failure happened, not what failed" | 140 |
| project-manager | bounds | C | <fallback> routing to sibling agents is project knowledge; <does> duplicates mission (D ~120 B); 'ask the user when >N' thresholds unmeasurable (D) |  |  | "escalate to system-architect for doc scope" | 319 |
| project-manager | handoff | C | routing to next /sc: command; model cannot know the catalogue |  |  | "handoff next=" | 53 |
| python-expert | frontmatter | C | `description` is what CC auto-delegation routes on; name/memory/color/disallowedTools are config |  |  | "Use when the work is Python implementation, pytest design" | 393 |
| python-expert | role | D | mission repeats the description; mindset is persona/exhortation a model needs no telling |  |  | "A bug fix is not a module rewrite" | 317 |
| python-expert | focus | A | SOLID/TDD/OWASP list; '>=95% on new code' is an unmeasured target (D) |  |  | "TDD-first, unit + integration, >=95% on new code" | 413 |
| python-expert | actions | A | analyze → sketch → TDD → validate → profile; model does this |  |  | "Write tests first, then the implementation" | 423 |
| python-expert | outputs | A | deliverable list a model produces for this task type unprompted |  |  | "Code: clean, tested, documented modules" | 431 |
| python-expert | tool_guidance (Ask First thresholds) | D | thresholds unmeasurable or judgement calls; gate itself is C-ish but values are arbitrary (backend: '>2 tables' here vs '>3 services' in bounds) |  |  | "architecture decisions touching >3 modules, framework swaps" | 80 |
| python-expert | tool_guidance (Proceed/Never) | A | lists ordinary actions and obvious prohibitions (no prod migrations, no fabricated sources, no secrets) |  |  | "Never: skip tests, ignore input validation" | 363 |
| python-expert | tool_guidance (Symbolic-First) | D | generic read-strategy preference repeated in 9 files; models already grep before reading; belongs in one shared place if kept |  |  | "query overview → definition → references before whole-file Read" | 200 |
| python-expert | tool_guidance (subagent-cannot-ask boilerplate) | D | identical 330-byte paragraph in all 12 files; a real stop-and-return gate, but one copy in the loader would do — 11 copies are duplicate |  |  | "As a delegated subagent Claude cannot ask mid-task" | 330 |
| python-expert | checklist | D | TDD/validation are A; '>=95% diff coverage ... otherwise unverified' is a project target (C-weak) plus off-list honesty gate |  |  | "Diff coverage >=95% on new/modified code" | 391 |
| python-expert | memory_guide | D | 12x identical header; 'verify against current state' is an A2 exhortation with no mechanism; category labels are weak C; 'Related:' cross-refs unused |  |  | "verify against current state before acting on them" | 536 |
| python-expert | examples | A | trigger→behavior pairs a model would produce anyway |  |  | "pytest cases first, DI service with explicit error types" | 420 |
| python-expert | gotchas (scope-discipline) | D | ANTI-remedy: frame-lock reinforcer |  |  | "fix only what was asked" | 150 |
| python-expert | gotchas (status-check) | B | ordering: verify the premise (work not already done) before implementing | R1 | mechanism (ordering) — narrow | "search to verify the work is not already done" | 100 |
| python-expert | gotchas (typing-hygiene, async-discipline) | A | Protocol/dataclasses/to_thread are model defaults |  |  | "never mix blocking I/O into an async path" | 254 |
| python-expert | bounds | C | <fallback> routing to sibling agents is project knowledge; <does> duplicates mission (D ~120 B); 'ask the user when >N' thresholds unmeasurable (D) |  |  | "escalate to system-architect for cross-language concerns" | 419 |
