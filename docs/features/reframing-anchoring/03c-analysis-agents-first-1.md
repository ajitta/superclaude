# Phase 2 content-value classification — agents (first half)

> Split by size into 3 files (part 1 of 3): [part 2](./03c-analysis-agents-first-2.md) · [part 3](./03c-analysis-agents-first-3.md). Section boundaries and content unchanged.

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
