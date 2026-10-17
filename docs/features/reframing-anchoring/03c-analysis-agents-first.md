# Phase 2 content-value classification — agents (first half)

Branch `feature/reframing-anchoring`. Judged only from the text of the 12 files below plus `src/superclaude/ARCHITECTURE.md` (delivery: agents are CC-native subagents, auto-selected on the `description` frontmatter). Byte figures are per-section measurements; split rows are estimates.

## 1. Scope and files read

| File | Bytes |
|---|---|
| src/superclaude/agents/backend-architect.md | 5056 |
| src/superclaude/agents/business-panel-experts.md | 6212 |
| src/superclaude/agents/deep-researcher.md | 7353 |
| src/superclaude/agents/devops-architect.md | 4852 |
| src/superclaude/agents/frontend-architect.md | 6284 |
| src/superclaude/agents/git-workflow.md | 6192 |
| src/superclaude/agents/insight-analyst.md | 5234 |
| src/superclaude/agents/learning-guide.md | 5178 |
| src/superclaude/agents/performance-engineer.md | 4827 |
| src/superclaude/agents/project-initializer.md | 9595 |
| src/superclaude/agents/project-manager.md | 6974 |
| src/superclaude/agents/python-expert.md | 5375 |
| **Total** | **73132** |

Shared skeleton in all 12 files: frontmatter, `<role>`, `<focus>`, `<actions>`, `<outputs>`, `<tool_guidance>`, `<checklist>`, `<memory_guide>`, `<examples>`, `<gotchas>`, `<bounds>`, `<handoff>`. Three identical boilerplate blocks recur in every file: the 330-byte 'As a delegated subagent Claude cannot ask mid-task…' paragraph, the `memory_guide` header, and (9 files) the `Symbolic-First` read rule.

## 2. Classification table

Class key: A = model already does it; B = structural remedy (failure named); C = project fact; D = other (exhortation, unmeasurable, persona, duplicate, repo-only leak, uncertain A). 'ANTI' in a reason marks text that works against the restructure principle.

| File | Section | Class | Reason | Failure (B) | Mechanism / exhortation (B) | Quote | ~Bytes |
|---|---|---|---|---|---|---|---|
| backend-architect | frontmatter | C | `description` is what CC auto-delegation routes on; name/memory/color/disallowedTools are config |  |  | "Use when a change sets an API contract" | 419 |
| backend-architect | role | D | mission repeats the description; mindset is persona/exhortation a model needs no telling |  |  | "Invariants beat handlers; explicit beats implicit" | 298 |
| backend-architect | focus | A | textbook backend concerns the model already applies |  |  | "strong vs eventual, transaction boundaries, idempotency" | 356 |
| backend-architect | actions | D | step 1 restates only what 'the user named' — anchors to the stated frame, never infers unstated purpose (I0 near-miss); steps 2-5 are A |  |  | "success criteria the user named" | 418 |
| backend-architect | outputs | A | deliverable list a model produces for this task type unprompted |  |  | "Api-Spec: endpoints, request/response models, error contract" | 318 |
| backend-architect | tool_guidance (Ask First thresholds) | D | thresholds unmeasurable or judgement calls; gate itself is C-ish but values are arbitrary (backend: '>2 tables' here vs '>3 services' in bounds) |  |  | "migrations touching >2 tables or shared across services" | 80 |
| backend-architect | tool_guidance (Proceed/Never) | A | lists ordinary actions and obvious prohibitions (no prod migrations, no fabricated sources, no secrets) |  |  | "Never: execute DB migrations, alter prod configs" | 361 |
| backend-architect | tool_guidance (Symbolic-First) | D | generic read-strategy preference repeated in 9 files; models already grep before reading; belongs in one shared place if kept |  |  | "query overview → definition → references before whole-file Read" | 200 |
| backend-architect | tool_guidance (subagent-cannot-ask boilerplate) | D | identical 330-byte paragraph in all 12 files; a real stop-and-return gate, but one copy in the loader would do — 11 copies are duplicate |  |  | "As a delegated subagent Claude cannot ask mid-task" | 330 |
| backend-architect | checklist | A | restates outputs as tick boxes |  |  | "Authz paths specified, not implied" | 250 |
| backend-architect | memory_guide | D | 12x identical header; 'verify against current state' is an A2 exhortation with no mechanism; category labels are weak C; 'Related:' cross-refs unused |  |  | "verify against current state before acting on them" | 491 |
| backend-architect | examples | A | trigger→behavior pairs a model would produce anyway |  |  | "OpenAPI sketch: resource shape, error codes, idempotency keys" | 352 |
| backend-architect | gotchas (content-not-service, cli-simplicity) | D | repo-only leak: only true inside superclaude's own repo yet shipped to every project |  |  | "superclaude is a content framework rather than a web service" | 480 |
| backend-architect | gotchas (invariant-first) | A | ordering preference a model follows; exhortation |  |  | "write the invariants before the endpoints" | 150 |
| backend-architect | bounds | C | <fallback> routing to sibling agents is project knowledge; <does> duplicates mission (D ~120 B); 'ask the user when >N' thresholds unmeasurable (D) |  |  | "escalate to system-architect for cross-system topology" | 395 |
| backend-architect | handoff | C | routing to next /sc: command; model cannot know the catalogue |  |  | "handoff next=" | 51 |
| business-panel-experts | frontmatter | C | `description` is what CC auto-delegation routes on; name/memory/color/disallowedTools are config |  |  | "Use when a business or product-strategy decision" | 416 |
| business-panel-experts | role | D | mission repeats the description; mindset is persona/exhortation a model needs no telling |  |  | "Each expert is an analytic lens, not an impersonation" | 257 |
| business-panel-experts | focus (lens roster) | C | WHICH nine frameworks this panel uses is a project choice |  |  | "Christensen: Disruptive Innovation + JTBD" | 300 |
| business-panel-experts | focus (per-lens blurbs) | A | one-line summaries of Porter/Drucker/Taleb etc. — model knows these |  |  | "strongest forces, sustainable advantage, value creation vs capture" | 720 |
| business-panel-experts | modes | C | three project-defined modes and the one-mode rule; Debate's forced opposed positions are a weak adversarial structure (A1/R1) but both sides share one context |  |  | "lenses taking opposed positions surface assumptions" | 756 |
| business-panel-experts | actions | D | 'the decision the user needs' is the closest thing to a purpose step in scope but is a restatement, not an inference; rest A |  |  | "the decision the user needs" | 391 |
| business-panel-experts | quality | D | post-hoc self-questions; 'the decision actually needed' is the right idea placed AFTER the analysis, as an exhortation |  |  | "does it answer the decision actually needed" | 184 |
| business-panel-experts | outputs | B | output-shape rule: per-option pros/cons + conditional triggers, no single verdict — counters yes/no compression | R3 | mechanism (output shape) — weak: nothing forbids a headline default | "Trade-Off-Map: pros, cons, conditional triggers per option" | 304 |
| business-panel-experts | tool_guidance (Ask First thresholds) | D | thresholds unmeasurable or judgement calls; gate itself is C-ish but values are arbitrary (backend: '>2 tables' here vs '>3 services' in bounds) |  |  | "widen the analysis beyond the question asked" | 80 |
| business-panel-experts | tool_guidance (Proceed/Never) | A | lists ordinary actions and obvious prohibitions (no prod migrations, no fabricated sources, no secrets) |  |  | "Never: make definitive business decisions" | 244 |
| business-panel-experts | tool_guidance (subagent-cannot-ask boilerplate) | D | identical 330-byte paragraph in all 12 files; a real stop-and-return gate, but one copy in the loader would do — 11 copies are duplicate |  |  | "As a delegated subagent Claude cannot ask mid-task" | 330 |
| business-panel-experts | checklist | D | duplicates outputs/modes; 'Recommendations conditional + testable' repeats the R3 shape rule |  |  | "Recommendations conditional + testable" | 269 |
| business-panel-experts | memory_guide | D | 12x identical header; 'verify against current state' is an A2 exhortation with no mechanism; category labels are weak C; 'Related:' cross-refs unused |  |  | "verify against current state before acting on them" | 516 |
| business-panel-experts | examples | D | restates modes/outputs; 'conditions that would flip the answer' is the R3 shape already in outputs |  |  | "converges with the conditions that would flip the answer" | 458 |
| business-panel-experts | gotchas (intent-confirm) | D | exhortation; restating intent is not inferring purpose (I0 near-miss) |  |  | "restate the user's intent before a non-trivial analysis" | 130 |
| business-panel-experts | gotchas (lens-not-impersonation) | A | model does not fabricate quotes unprompted |  |  | "never fabricate quotes or attribute novel claims" | 146 |
| business-panel-experts | gotchas (scope-anchoring) | D | ANTI-remedy: forbids looking outside the stated question — reinforces R2/I0 frame lock |  |  | "analyze only the question asked; do not expand into adjacent domains" | 140 |
| business-panel-experts | bounds | C | <fallback> routing to sibling agents is project knowledge; <does> duplicates mission (D ~120 B); 'ask the user when >N' thresholds unmeasurable (D) |  |  | "escalate to requirements-analyst for spec gaps" | 395 |
| business-panel-experts | handoff | C | routing to next /sc: command; model cannot know the catalogue |  |  | "handoff next=" | 56 |
| deep-researcher | frontmatter | C | `description` is what CC auto-delegation routes on; name/memory/color/disallowedTools are config |  |  | "Use when the answer lies outside the repo" | 445 |
| deep-researcher | role | D | mission repeats the description; mindset is persona/exhortation a model needs no telling |  |  | "Research scientist plus investigative journalist" | 322 |
| deep-researcher | focus (Evidence/Provenance/Synthesis/Hop) | D | restates <evidence>, <hop_patterns> and checklist; duplicate |  |  | ">=2 independent sources, except a claim settled by one primary" | 528 |
| deep-researcher | focus (Replan-Triggers) | B | names concrete conditions that force a re-plan — the trigger A3 says is missing | A3 | mechanism (trigger conditions) — but no re-entry rule after compaction | "sources disagree on a load-bearing claim, a hop dead-ends" | 150 |
| deep-researcher | actions (rest) | D | steps 3-4 duplicate Replan-Triggers and <evidence>; step 2/5 are A |  |  | "re-plan when a trigger fires" | 609 |
| deep-researcher | actions (step 1 grep-first) | C | ordering rule: repo before web — project preference the model would not default to |  |  | "Grep the repo before any external search" | 80 |
| deep-researcher | depth_behavior | C | project-defined depth levels and the 'subagents do not spawn subagents' runtime fact |  |  | "subagents do not spawn subagents" | 543 |
| deep-researcher | hop_patterns | A | entity/temporal/conceptual/causal chains — model plans these |  |  | "observation → proximate cause → root cause → options" | 308 |
| deep-researcher | evidence | B | gate: a claim with one source is labelled single-source and sources get a tier; disagreement must be explained not averaged — stops a single document from carrying a conclusion | A2 | mechanism (labelling gate + output shape) — real, but restated 4x in the file | "a claim with only one is labeled single-source" | 417 |
| deep-researcher | tools | C | Tavily skill/MCP routing, Context7, fallback order, parallel vs sequential rules |  |  | "tavily-search → broad parallel queries" | 703 |
| deep-researcher | outputs | D | Sources-Table with tier duplicates <evidence>; rest A |  |  | "Sources-Table: URL, title, date, credibility tier" | 275 |
| deep-researcher | tool_guidance (Ask First thresholds) | D | thresholds unmeasurable or judgement calls; gate itself is C-ish but values are arbitrary (backend: '>2 tables' here vs '>3 services' in bounds) |  |  | "scope shifts beyond the question asked" | 80 |
| deep-researcher | tool_guidance (Proceed/Never) | A | lists ordinary actions and obvious prohibitions (no prod migrations, no fabricated sources, no secrets) |  |  | "Never: bypass paywalls, access private data, fabricate sources" | 255 |
| deep-researcher | tool_guidance (subagent-cannot-ask boilerplate) | D | identical 330-byte paragraph in all 12 files; a real stop-and-return gate, but one copy in the loader would do — 11 copies are duplicate |  |  | "As a delegated subagent Claude cannot ask mid-task" | 330 |
| deep-researcher | checklist | D | third/fourth restatement of the evidence gate and hop summarization |  |  | "Contradictions explained, not averaged" | 474 |
| deep-researcher | memory_guide | D | 12x identical header; 'verify against current state' is an A2 exhortation with no mechanism; category labels are weak C; 'Related:' cross-refs unused |  |  | "verify against current state before acting on them" | 505 |
| deep-researcher | examples | A | trigger→behavior pairs a model would produce anyway |  |  | "primary benchmarks with dates, credibility tiers, version caveats" | 462 |
| deep-researcher | gotchas | A | cite inline / match depth — model does both |  |  | "always cite inline" | 231 |
| deep-researcher | bounds | C | <fallback> routing to sibling agents is project knowledge; <does> duplicates mission (D ~120 B); 'ask the user when >N' thresholds unmeasurable (D) |  |  | "escalate to requirements-analyst for scope clarity" | 458 |
| deep-researcher | handoff | C | routing to next /sc: command; model cannot know the catalogue |  |  | "handoff next=" | 57 |
| devops-architect | frontmatter | C | `description` is what CC auto-delegation routes on; name/memory/color/disallowedTools are config |  |  | "Use when the work is CI/CD, IaC" | 378 |
| devops-architect | role | D | mission repeats the description; mindset is persona/exhortation a model needs no telling |  |  | "Automate everything that repeats" | 306 |
| devops-architect | focus | A | generic CI/CD, IaC, observability vocabulary |  |  | "version-controlled, reproducible infra as the source of truth" | 370 |
| devops-architect | actions | A | standard pipeline/IaC/monitoring sequence; no step before acting |  |  | "Spot automation opportunities and reliability gaps" | 378 |
| devops-architect | outputs | A | deliverable list a model produces for this task type unprompted |  |  | "Runbooks: incident response + troubleshooting playbooks" | 342 |
| devops-architect | tool_guidance (Ask First thresholds) | D | thresholds unmeasurable or judgement calls; gate itself is C-ish but values are arbitrary (backend: '>2 tables' here vs '>3 services' in bounds) |  |  | "deploy-strategy shifts touching more than one environment" | 80 |
| devops-architect | tool_guidance (Proceed/Never) | A | lists ordinary actions and obvious prohibitions (no prod migrations, no fabricated sources, no secrets) |  |  | "Never: apply infra changes without review" | 269 |
| devops-architect | tool_guidance (Symbolic-First) | D | generic read-strategy preference repeated in 9 files; models already grep before reading; belongs in one shared place if kept |  |  | "query overview → definition → references before whole-file Read" | 200 |
| devops-architect | tool_guidance (subagent-cannot-ask boilerplate) | D | identical 330-byte paragraph in all 12 files; a real stop-and-return gate, but one copy in the loader would do — 11 copies are duplicate |  |  | "As a delegated subagent Claude cannot ask mid-task" | 330 |
| devops-architect | checklist | D | first three are A; the 'rehearsal reported only with evidence, otherwise unrehearsed' honesty gate is useful but addresses none of I0/A/R |  |  | "otherwise the procedure is marked unrehearsed" | 367 |
| devops-architect | memory_guide | D | 12x identical header; 'verify against current state' is an A2 exhortation with no mechanism; category labels are weak C; 'Related:' cross-refs unused |  |  | "verify against current state before acting on them" | 521 |
| devops-architect | examples | A | trigger→behavior pairs a model would produce anyway |  |  | "GitHub Actions with test/build/deploy stages" | 392 |
| devops-architect | gotchas (scope-discipline) | D | ANTI-remedy: forbids widening beyond what was asked — reinforces I0/R2 frame lock |  |  | "configure only what was asked" | 130 |
| devops-architect | gotchas (secrets-out-of-iac) | A | model never commits secrets into IaC unprompted |  |  | "never commit secrets into Terraform variables" | 141 |
| devops-architect | gotchas (status-check) | B | ordering: verify the premise (infra not already provisioned) before acting | R1 | mechanism (ordering) — narrow: checks existence only, not purpose | "search to confirm the infra is not already provisioned" | 110 |
| devops-architect | bounds | C | <fallback> routing to sibling agents is project knowledge; <does> duplicates mission (D ~120 B); 'ask the user when >N' thresholds unmeasurable (D) |  |  | "escalate to security-engineer for secrets and compliance" | 381 |
| devops-architect | handoff | C | routing to next /sc: command; model cannot know the catalogue |  |  | "handoff next=" | 50 |
| frontend-architect | frontmatter | C | `description` is what CC auto-delegation routes on; name/memory/color/disallowedTools are config |  |  | "Use when the work is component architecture, WCAG" | 370 |
| frontend-architect | role | D | mission repeats the description; mindset is persona/exhortation a model needs no telling |  |  | "Accessibility is fundamental, not an afterthought" | 235 |
| frontend-architect | focus | A | WCAG/CWV/mobile-first list the model already holds |  |  | "WCAG 2.2 AA, keyboard nav, screen-reader semantics" | 387 |
| frontend-architect | actions | A | standard a11y/perf implementation steps; 'measuring before and after' is A |  |  | "Translate UI requirements into a11y and perf implications" | 369 |
| frontend-architect | aesthetics (4 directions before building) | B | ordering + option shape: when the brief is ambiguous, produce 4 directions and stop instead of building the default | R3 | mechanism (options before action) — weak: no rule against marking one as recommended | "proposes 4 distinct visual directions ... before building" | 250 |
| frontend-architect | aesthetics (house-style bans) | D | style policy about the model's own defaults (cream/serif/terracotta, Inter, 01/02 labels); tone/taste, not a measured failure |  |  | "Claude never auto-applies it" | 810 |
| frontend-architect | outputs | A | deliverable list a model produces for this task type unprompted |  |  | "A11y-Reports: WCAG findings paired with concrete fixes" | 316 |
| frontend-architect | tool_guidance (Ask First thresholds) | D | thresholds unmeasurable or judgement calls; gate itself is C-ish but values are arbitrary (backend: '>2 tables' here vs '>3 services' in bounds) |  |  | "design-system-wide changes, framework migrations" | 80 |
| frontend-architect | tool_guidance (Proceed/Never) | A | lists ordinary actions and obvious prohibitions (no prod migrations, no fabricated sources, no secrets) |  |  | "Never: skip a11y testing, ignore Core Web Vitals" | 381 |
| frontend-architect | tool_guidance (Symbolic-First) | D | generic read-strategy preference repeated in 9 files; models already grep before reading; belongs in one shared place if kept |  |  | "query overview → definition → references before whole-file Read" | 200 |
| frontend-architect | tool_guidance (subagent-cannot-ask boilerplate) | D | identical 330-byte paragraph in all 12 files; a real stop-and-return gate, but one copy in the loader would do — 11 copies are duplicate |  |  | "As a delegated subagent Claude cannot ask mid-task" | 330 |
| frontend-architect | checklist | D | CWV targets are A (model knows 2.5s/200ms/0.1); 'marked unverified' is an off-list honesty gate; keep only if measured |  |  | "a metric not measured is marked unverified" | 582 |
| frontend-architect | memory_guide | D | 12x identical header; 'verify against current state' is an A2 exhortation with no mechanism; category labels are weak C; 'Related:' cross-refs unused |  |  | "verify against current state before acting on them" | 520 |
| frontend-architect | examples | A | trigger→behavior pairs a model would produce anyway |  |  | "accessible form with semantic labels, keyboard-friendly validation" | 374 |
| frontend-architect | gotchas (no-frontend-on-sc, plain-cli-output) | D | repo-only leak |  |  | "has no UI components; its markdown content is not frontend work" | 400 |
| frontend-architect | gotchas (vitals-or-it-didnt-happen) | A | no perf claim without measurement — model default |  |  | "never claim a perf improvement without a measured before/after" | 109 |
| frontend-architect | bounds | C | <fallback> routing to sibling agents is project knowledge; <does> duplicates mission (D ~120 B); 'ask the user when >N' thresholds unmeasurable (D) |  |  | "escalate to backend-architect for API contracts" | 407 |
| frontend-architect | handoff | C | routing to next /sc: command; model cannot know the catalogue |  |  | "handoff next=" | 52 |
| git-workflow | frontmatter | C | `description` is what CC auto-delegation routes on; name/memory/color/disallowedTools are config |  |  | "Use when asked to draft conventional commits" | 384 |
| git-workflow | role | D | mission repeats the description; mindset is persona/exhortation a model needs no telling |  |  | "The agent operates on git state, never on source code" | 310 |
| git-workflow | focus (naming + gh) | C | branch naming convention and PR-context commands are project choices |  |  | "feature/*, fix/*, docs/*" | 150 |
| git-workflow | focus (rest) | A | conventional commits, stash, reflog — model knows |  |  | "conflict-resolution guidance, stash management, reflog navigation" | 301 |
| git-workflow | actions | A | status/log/diff → classify → commit → report; model does this |  |  | "Inspect the repo state — status, log, diff" | 315 |
| git-workflow | pr_integration | C | gh json fields, review states, and that `--from-pr` belongs to /sc:git not gh |  |  | "`--from-pr` is an option of `/sc:git` and of the `claude` start-up command" | 507 |
| git-workflow | outputs | A | deliverable list a model produces for this task type unprompted |  |  | "Commits: conventional commit messages from staged changes" | 325 |
| git-workflow | tool_guidance (Ask First thresholds) | D | thresholds unmeasurable or judgement calls; gate itself is C-ish but values are arbitrary (backend: '>2 tables' here vs '>3 services' in bounds) |  |  | "add, push, merge, rebase, commit, checkout" | 80 |
| git-workflow | tool_guidance (Proceed/Fallback/Never) | C | which git ops count as read-only, gh-auth fallback, 'never modify source files' role boundary |  |  | "if `gh auth status` fails, tell the user to run `gh auth login`" | 882 |
| git-workflow | tool_guidance (subagent-cannot-ask boilerplate) | D | identical 330-byte paragraph in all 12 files; a real stop-and-return gate, but one copy in the loader would do — 11 copies are duplicate |  |  | "As a delegated subagent Claude cannot ask mid-task" | 330 |
| git-workflow | checklist | D | duplicates Ask First and actions |  |  | "Every write operation confirmed first" | 319 |
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
| python-expert | handoff | C | routing to next /sc: command; model cannot know the catalogue |  |  | "handoff next=" | 52 |

## 3. Anchor-point map

| File | Moment | What arrives | B step before it? |
|---|---|---|---|
| backend-architect | task text arrives (actions step 1) | action instruction from user/command | none — step 1 restates 'success criteria the user named' (stated frame only) |
| backend-architect | MEMORY.md loaded (memory_guide) | prior lessons document (A2/A3 anchor) | exhortation only: 'verify against current state before acting on them' |
| backend-architect | schemas/APIs read (tool_guidance Proceed) | existing code + docs (A2) | none |
| business-panel-experts | task text arrives (actions step 1) | action instruction from user/command | none — step 1 restates 'the decision the user needs' (stated, not inferred) |
| business-panel-experts | MEMORY.md loaded (memory_guide) | prior lessons document (A2/A3 anchor) | exhortation only: 'verify against current state before acting on them' |
| business-panel-experts | business context / prior estimate in the question (A1, R1) | user's framing of the decision | partial: Debate mode 'lenses taking opposed positions surface assumptions' — same context, no isolation; 'scope-anchoring' forbids reframing |
| business-panel-experts | recommendation delivered (R3) | option list / yes-no question | B: 'Trade-Off-Map: pros, cons, conditional triggers per option'; 'Recommendations conditional + testable' |
| deep-researcher | task text arrives (actions step 1) | action instruction from user/command | none — 'Restate the question and assess its complexity and ambiguity' |
| deep-researcher | MEMORY.md loaded (memory_guide) | prior lessons document (A2/A3 anchor) | exhortation only: 'verify against current state before acting on them' |
| deep-researcher | web sources arrive (step 3-4) | external documents (A2) | B: 'Cross-check each load-bearing claim against >=2 independent sources'; tier 1-4; 'never average' |
| deep-researcher | plan set (step 2) then evidence conflicts (A3) | own prior plan | B: 'Replan-Triggers: sources disagree ... a hop dead-ends, or scope drifts ... → re-plan' |
| deep-researcher | sub-investigation subagent returns (depth_behavior) | delegate result | none — only 'inter-hop summarization'; no rule on trusting/verifying the delegate's claims |
| devops-architect | task text arrives (actions step 1) | action instruction from user/command | none — step 1 is already action: 'Spot automation opportunities' |
| devops-architect | MEMORY.md loaded (memory_guide) | prior lessons document (A2/A3 anchor) | exhortation only: 'verify against current state before acting on them' |
| devops-architect | current pipeline inspected | existing configs/README (A2) | B-lite: 'search to confirm the infra is not already provisioned' (existence only) |
| frontend-architect | task text arrives (actions step 1) | action instruction from user/command | none — 'Translate UI requirements into a11y and perf implications' |
| frontend-architect | MEMORY.md loaded (memory_guide) | prior lessons document (A2/A3 anchor) | exhortation only: 'verify against current state before acting on them' |
| frontend-architect | ambiguous brief (aesthetics) | action instruction with no spec | B-lite: 'proposes 4 distinct visual directions ... before building' |
| frontend-architect | existing design system read | document anchor (A2) | none — 'an existing design system or user choice wins' (accepts it) |
| git-workflow | task text arrives (actions step 1) | action instruction from user/command | none — 'Inspect the repo state — status, log, diff' |
| git-workflow | MEMORY.md loaded (memory_guide) | prior lessons document (A2/A3 anchor) | exhortation only: 'verify against current state before acting on them' |
| git-workflow | PR body/comments read (pr_integration) | author rationale (A4) and prior AI output | none — reads title,body,comments,files with no isolation rule |
| git-workflow | diff read (actions step 1) | code change to classify | none (not an anchor risk; agent does not review) |
| insight-analyst | task text arrives (actions step 1) | action instruction from user/command | none — 'Parse the user query for topic, timeframe, author and type filters' |
| insight-analyst | MEMORY.md loaded (memory_guide) | prior lessons document (A2/A3 anchor) | exhortation only: 'verify against current state before acting on them' |
| insight-analyst | insights.jsonl entries read | prior AI-written insights (A2/A3) | none — entries are presented, never checked against current state |
| learning-guide | task text arrives (actions step 1) | action instruction from user/command | none — 'Assess the learner's current skill' |
| learning-guide | MEMORY.md loaded (memory_guide) | prior lessons document (A2/A3 anchor) | exhortation only: 'verify against current state before acting on them' |
| learning-guide | learner level from MEMORY.md/task (gotchas) | prior assessment document (A2) | none — level taken as given |
| performance-engineer | task text arrives (actions step 1) | action instruction from user/command | none — 'Capture baseline metrics tied to the UX in question' (closest: ties work to UX, purpose still unstated) |
| performance-engineer | MEMORY.md loaded (memory_guide) | prior lessons document (A2/A3 anchor) | exhortation only: 'verify against current state before acting on them' |
| performance-engineer | user names a suspected cause ('API latency is climbing') | prompt-embedded anchor (A1) | B-lite: 'status-check: confirm the bottleneck still exists'; 'profiling, not intuition' is an exhortation |
| project-initializer | task text arrives (actions step 1) | action instruction from user/command | none — 'Present the interactive task menu' |
| project-initializer | MEMORY.md loaded (memory_guide) | prior lessons document (A2/A3 anchor) | exhortation only: 'verify against current state before acting on them' |
| project-initializer | existing CLAUDE.md / configs read (task_details) | document anchor (A2) | none — 'analyzes gaps and proposes additions' accepts existing content |
| project-initializer | menu presented (actions step 2) | option list (R3) | ANTI: 'returns the menu with a recommended preset'; example has tasks 'preselected' |
| project-initializer | batch results come back (execution_plan) | delegate/parallel results | none |
| project-manager | task text arrives (actions step 1) | action instruction from user/command | none — actions start at 'Post-implementation: spot patterns' |
| project-manager | MEMORY.md loaded (memory_guide) | prior lessons document (A2/A3 anchor) | exhortation only: 'verify against current state before acting on them' |
| project-manager | prior context loaded (lifecycle) | pm_context + session record (A3 prior plan) | none — 'read prior context ... report status'; no check that the prior plan still holds |
| project-manager | sub-agent reports arrive (mission: orchestrate sub-agents) | delegate results (A4-like) | none — no rule on what to do with a delegate's rationale |
| project-manager | command fails (self_correction) | invalidating evidence (A3) | B: 'stop, investigate ... document the hypothesized root cause, pick a different approach' |
| project-manager | mistake reported by user ('a mistake just happened') | user's problem definition (R1) | none — 'root-cause-not-symptom' is about the write-up, not the premise |
| python-expert | task text arrives (actions step 1) | action instruction from user/command | none — 'Analyze scope, edge cases and security implications' |
| python-expert | MEMORY.md loaded (memory_guide) | prior lessons document (A2/A3 anchor) | exhortation only: 'verify against current state before acting on them' |
| python-expert | existing module/docstrings read | document anchor (A2) | B-lite: 'search to verify the work is not already done' (existence only) |

**I0 check (purpose stated + success criterion derived BEFORE acting):** no file in scope has such a step. The three nearest lines all restate the *stated* request rather than infer the unstated purpose:

- backend-architect actions 1: "Restate the requirements, constraints and success criteria the user named."
- business-panel-experts actions 1: "Restate the question, context, constraints and the decision the user needs." (and, post-hoc, quality: "does it answer the decision actually needed")
- deep-researcher actions 1: "Restate the question and assess its complexity and ambiguity."

Nine of twelve agents start acting at step 1 with no restatement at all. No file tells the model to look beyond the file/object named in the task; six files tell it NOT to (see finding 2).

## 4. Totals per class

| Class | Rows | ~Bytes | Share |
|---|---|---|---|
| A | 54 | 18165 | 25% |
| B | 8 | 1805 | 2% |
| C | 60 | 22808 | 31% |
| D | 91 | 29021 | 40% |
| total | 213 | 71799 | |

Of the D bytes, roughly 7.9 KB is literal 12x/9x duplication (subagent paragraph 3,960; Symbolic-First 1,800; memory_guide header ~1,900; `<does>` restating mission ~1,400) and ~1.3 KB is repo-only leaks. Of the C bytes, the heaviest keepers are insight-analyst, project-initializer (tasks/plan/memory routing), project-manager lifecycle, git-workflow pr_integration, deep-researcher tools/depth.

## 5. Top 10 findings (ranked)

1. **No I0 step anywhere (biggest B gap).** 12/12 agents receive the task text and act; none states the purpose behind the request or derives its own success criterion first. The three 'restate' steps lock onto what 'the user named'. A single ordered step before `actions 1` — infer purpose → own criterion → then read the named artefact — is missing in every file.
2. **Six files actively reinforce frame lock (ANTI-I0/R2).** `scope-discipline` (performance-engineer, devops-architect, python-expert), `scope-anchoring` and 'Ask First: widen the analysis beyond the question asked' (business-panel-experts), 'scope shifts beyond the question asked' (deep-researcher), `answer-not-lecture` (learning-guide). Together ~1 KB telling the model to stay inside the named frame — the exact behaviour the fixtures showed failing. Delete or invert into 'name what lies one layer out, then stay in scope'.
3. **project-initializer bakes in an R3 starred default.** actions 2: 'returns the menu with a recommended preset'; example: tasks 'preselected'. This is the measured accept-the-starred-option failure, written into the design.
4. **~7.9 KB of 12x boilerplate is deletable by hoisting.** The 330-byte 'As a delegated subagent Claude cannot ask mid-task…' paragraph (3,960 B), Symbolic-First (1,800 B), memory_guide header (~1,900 B), `<does>` restating `<mission>` (~1,400 B). One copy in the loader/shared preamble keeps the gate; 11 copies add tokens only.
5. **~18 KB (25%) is class A domain knowledge:** `<focus>`, most `<actions>`, `<outputs>`, `<examples>`, `Proceed/Never` lines and generic checklists describe what a current model does unprompted (TDD, measure before optimize, WCAG, conventional commits). Largest single A blocks: project-initializer task_details detection heuristics (1.3 KB), business-panel lens blurbs (0.7 KB).
6. **The real B mechanisms in scope are few and should be kept, once each:** deep-researcher `Replan-Triggers` (A3) and the ≥2-source / single-source label gate (A2) — but the evidence rule is stated four times in that file (focus, actions, evidence, checklist; ~1 KB of repeats); project-manager `self_correction` (A3, failure-triggered only); business-panel `Trade-Off-Map` per-option conditional shape (R3).
7. **Exhortations that look like remedies but have no mechanism (D, not B):** 'MEMORY.md = prior lessons; verify against current state' (A2, 12x), `intent-confirm` (I0, business-panel and project-manager), business-panel `quality` self-questions placed after the analysis, 'profiling, not intuition' / 'intuition is not evidence' (A1, performance-engineer, 3 restatements). None changes order or what information reaches the model.
8. **A4 and delegate results are unguarded.** git-workflow reads PR title/body/comments with no isolation rule; project-manager's mission is to 'orchestrate sub-agents' yet nothing says how to treat a delegate's report; deep-researcher's sub-investigations return with only 'inter-hop summarization'. No file in scope has a reviewer-isolation or delegate-verification step.
9. **A3 coverage is partial and no file has a compaction re-entry rule.** Only deep-researcher (evidence-triggered) and project-manager (failure-triggered) can re-plan; the other ten carry a plan forward unconditionally. project-manager loads `pm_context`/session records and 'reports status' without checking whether the prior plan still holds.
10. **Repo-only leaks and an internal inconsistency.** `content-not-service`, `cli-simplicity`, `no-frontend-on-sc`, `plain-cli-output`, `make-deploy`, `uv-not-pip` (~1.3 KB) apply only inside superclaude's own repo yet ship to every project. backend-architect gates migrations at '>2 tables' in tool_guidance but '>3 services' in bounds.

Secondary notes: the 'marked unverified' honesty gates (frontend, performance, learning, python, devops checklists) are useful output-shape rules but address none of I0/A1–A4/R1–R3; they were classed D pending measurement. The `status-check` gotchas (performance, devops, python) are the only premise checks in scope (B, R1) and check existence only — they do not ask whether the user's stated cause is the cause.

## 6. Not read

- The other 14 files in `src/superclaude/agents/` (quality-engineer, refactoring-expert, repo-index, requirements-analyst, root-cause-analyst, security-engineer, self-review, simplicity-guide, socratic-mentor, system-architect, technical-writer, verifier, README.md, __init__.py) — out of scope.
- `src/superclaude/scripts/context_loader.py` — not needed; delivery mode was clear from ARCHITECTURE.md.
- Per the isolation rule: `~/.claude/`, repo `.claude/`, `docs/`, CHANGELOG.md, README.md, tests, and the `superclaude-repo-maintenance` skill were not opened.
