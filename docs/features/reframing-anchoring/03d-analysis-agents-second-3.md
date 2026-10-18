# 03d — Phase 2 content value classification: agents (second half) + README — part 3 of 3

> Continuation of [part 1](./03d-analysis-agents-second-1.md) (split by size; content unchanged).

## 2. Classification table (continued)

| File | Section | Class | Reason | Failure (B) | Mechanism/exhortation (B) | Quote | ~Bytes |
|---|---|---|---|---|---|---|---|
| README.md | whole file | D | Not delivered to the model: context_loader.py:523 excludes README stems, and ARCHITECTURE.md says agents are delivered by CC-native description matching. Maintainer doc. If it were delivered: Available Agents + Cross-Agent Conflict Resolution tables would be C (~3.3KB); Model Routing (Fable/Sonnet pricing, ~2.6KB), Permission Framework, Authoring Rules pointer to .claude/rules, Agent Memory internals are repo-only; Escalation Rules '>10% chance of breaking change' is unmeasurable. |  |  | "Risk: >10% chance of breaking change → escalate" | 9973 |

## 3. Anchor-point map

| File | Moment | What arrives | B step before it? |
|---|---|---|---|
| quality-engineer | task text | action instruction ('build a test strategy for X') | none — action 1 starts analysing scenarios of the named scope; no purpose/criterion step |
| quality-engineer | reading code under change | code, existing tests, CI config | none |
| quality-engineer | writing the report | prompt guidance such as 'focus on real issues' | yes — finding_policy: "does not pre-filter under general guidance" (A1/A4 output shape) |
| refactoring-expert | task text | action instruction, possibly with a complexity figure | partial — "Capture a baseline complexity metric from a tool's output" (A1) and "search to confirm the work is not already done"; no purpose step |
| refactoring-expert | reading code | code + comments/docstrings | none (A2 gap: comments explaining why code is shaped a way are trusted) |
| repo-index | task text | 'index the repo' / 'give me an overview' | n/a — purely mechanical task |
| repo-index | existing index | prior PROJECT_INDEX files / remembered index | yes — "re-read them from disk (never answer from memory)" (A2/A3) |
| requirements-analyst | task text | fuzzy feature request ('we want a dashboard') | partial — action 1 "Drive structured discovery questions to surface the real requirement"; the file does not say to state the inferred purpose or a success criterion, and gotcha scope-anchoring forbids looking outward |
| requirements-analyst | stakeholder input | stakeholder statements, existing specs | none — 'Never ... assume unstated reqs' and 'skip discovery when reqs exist' accept supplied framing (R1) |
| requirements-analyst | prioritization | MoSCoW candidate list | none — no rule against a starred default (R3) |
| root-cause-analyst | task text | symptom report, often with a suspected cause | partial — "restate the user's intent before non-trivial work" (I0, restates not infers); "Generate multiple hypotheses" (A1) but the user's suspect is not explicitly demoted to one-of-many |
| root-cause-analyst | logs/evidence | logs, prior postmortems, prior AI output | none for prior documents (A2); evidence-over-narrative is exhortation |
| root-cause-analyst | after failed cycles | own earlier hypotheses | yes — exploration_budget: "caps the investigation at three hypothesis-test cycles" (A3 counted gate) |
| security-engineer | task text | 'audit X' instruction, maybe 'I think it's SQLi' | none — action 1 scans 'the named scope'; no purpose or premise step |
| security-engineer | reading code | code + comments ('sanitised upstream'), README security notes | none (A2 gap) |
| security-engineer | writing the report | prompt guidance / scope limits | yes — finding_policy (A1/A4 output shape) |
| self-review | task text | 'review this' + the author's description/rationale | none — focus lists "rationale for designs" as EVIDENCE; nothing orders code-before-rationale or withholds the rationale (A4 gap, the biggest in scope) |
| self-review | work product | diff/plan/design + tests claimed | partial — Verdict shape PASS/FAIL/UNVERIFIED and "42/42 pass requires test output in hand" (A2/A4 output shape) |
| self-review | plan review | a prior plan | partial — checklist "Requirements traced 1:1 to acceptance criteria / stated intent" (stated, not inferred intent) |
| self-review | delegate result | output of an Agent call (tool list includes Agent) | none |
| simplicity-guide | task text | brief/design/'should we add X?' | YES — actions 1-3: "Orient by reading the artifact" → "Restate the artifact's purpose and constraints" → "Question whether the work is needed ... state confidence" before any reduction (I0/R1). Closest to the restructure principle in scope. No success criterion derived. |
| simplicity-guide | yes/no question | 'should we add Redis for caching?' | example only — dependency-gate example answers conditionally ("verify load pattern before adopting"); not a rule (R3 gap) |
| simplicity-guide | delegate result | docs-check sub-agent verdict | none — result reported with the delegate's confidence; no cross-check |
| socratic-mentor | task text | 'quiz me toward X' | n/a — the agent questions the learner, not its own framing; no I0/A/R moment |
| system-architect | task text | design request with stated growth horizon | none — action 2 "sized to user's stated growth horizon" and mindset "not about adjacent systems" accept the frame (R1/R2 anti-mechanism) |
| system-architect | existing architecture | current patterns, ADRs, diagrams | none (A2 gap: existing ADR rationale trusted) |
| system-architect | yes/no question | 'should we move to microservices?' | example only — "trade-off matrix vs current pain, staged path"; not a rule (R3 gap) |
| technical-writer | task text | 'document the API' | none — action 1 identifies the READER's goal, not the requester's purpose; A-level |
| technical-writer | source material | code, docstrings, existing README | none — 'document unverified behavior' in Never is exhortation (A2 gap: docstrings over code) |
| verifier | task text | 'verify X against its plan' | none for purpose — verifier never asks whether the plan serves the feature's purpose (R2: frame locked to the plan document by design) |
| verifier | plan document | prior plan with Proof section and checked boxes | YES — "re-run its commands, never copy its numbers"; "read the output rather than inferring it from a green suite"; per-claim MATCH/MISMATCH/UNVERIFIED (A2) |
| verifier | command failure | own failed probe | yes — failure-record: "take one different probe, never an identical retry" (A3 minimal) |
| verifier | compaction / re-entry | — | none anywhere in scope (A3 re-entry rule absent) |
| README.md | — | not delivered | n/a |

**I0 check per file** (does any step make the model state the purpose behind the request and derive a success criterion BEFORE acting?):

- simplicity-guide — purpose yes, criterion no: "2. Restate the artifact's purpose and constraints; if uncertain about the domain, ask the user rather than assume." Then "3. Question whether the work is needed and what the smallest thing that works looks like; state confidence (high, medium, low) and its basis."
- root-cause-analyst — restatement only: "intent-confirm: restate the user's intent before non-trivial work". Restates the stated intent; does not infer the unstated purpose; no criterion.
- requirements-analyst — questions only: "Drive structured discovery questions to surface the real requirement." No instruction to state purpose or criterion; action 4 ("Define measurable outcomes") comes after specification, as an output.
- All other nine agents — no. quality-engineer, security-engineer, system-architect, technical-writer, refactoring-expert, verifier, self-review, repo-index, socratic-mentor start acting on the named scope at action 1.

## 4. Totals per class

| Class | Rows | ~Bytes | Share of 79.9 KB |
|---|---|---|---|
| A already does it | 15 | 5026 | 6% |
| B structural remedy | 18 | 6023 | 7% |
| C project information | 70 | 18043 | 22% |
| D other | 119 | 50601 | 63% |

D without README.md: ~40628 bytes (~58% of the 12 agent files). B is concentrated in verifier (~1.6 KB), the shared finding_policy block (3 × 641 B), root-cause-analyst (~0.7 KB) and simplicity-guide (~0.4 KB). A is low only because most generic practice in these files is phrased as duplicate checklist/example/bounds restatements, which were counted as D (duplicate) rather than A.

## 5. Top 10 findings

1. **Biggest D deletion — template boilerplate, ~40 KB across 12 files.** role/mindset, focus, outputs, checklist, examples, bounds/does+never restate the actions or the description. Per file ~2.3 KB. The 400-byte 'As a delegated subagent Claude cannot ask mid-task…' paragraph appears verbatim 12 times (~4.8 KB) and could be one sentence or live once in the delivery layer.
2. **Biggest B gap — self-review has no A4 isolation.** It is the reviewer, yet `focus` lists "rationale for designs" as evidence and nothing orders code-before-rationale or withholds the author's description. A structural fix (read diff → form findings → then read author rationale → reconcile) is absent; the Verdict shape only mitigates premature approval.
3. **I0 is addressed by one agent only, partially.** simplicity-guide actions 1-3 order orient → restate purpose → question necessity before acting. No file in scope derives a success criterion from the purpose, and eleven agents start on the named scope at action 1. requirements-analyst (the agent whose job is 'the real requirement') never says to state the inferred purpose.
4. **Three files contain anti-I0/anti-R2 rules.** refactoring-expert scope-discipline ("touching file X does not grant license to refactor its callers"), requirements-analyst scope-anchoring + Never 'assume unstated reqs', system-architect scope-anchoring ("'while we're here' is out of scope") and mindset ("not about adjacent systems", "user's stated growth horizon"). These enforce the frame lock the owner wants to break; decide which way to go.
5. **README.md (~10 KB) is not delivered** (`context_loader.py:523` excludes README stems). Its Model Routing section (~2.6 KB of Fable/Sonnet pricing), Permission Framework, Agent Memory internals and the `.claude/rules/` pointers are maintainer text. If it is ever delivered, only the agent roster and Cross-Agent Conflict tables are C.
6. **A1 is handled by output shape, not by ordering.** finding_policy (3 × 641 B) refuses prompt filtering — a real mechanism. But no agent quarantines a prompt-embedded number or suspected cause: root-cause-analyst generates 'multiple hypotheses' without saying the user's suspect is one of them and must not head the list; refactoring-expert's tool-sourced baseline is the only number gate.
7. **A3 has two real gates, both narrow.** root-cause-analyst exploration_budget (three cycles then stop and ask) and verifier failure-record (different probe, never identical retry). No file has a general 'evidence invalidates the plan → re-plan' trigger or a post-compaction re-entry rule.
8. **R3 exists only as examples.** simplicity-guide 'should we add Redis?' and system-architect 'should we move to microservices?' both show a conditional/staged answer to a yes/no question, but as example rows (D). No rule forbids a bare yes/no or a recommended default; the agents' own Ask-First questions to the user also carry no 'present options without a default' rule.
9. **Exhortations dressed as B.** 'verify against current state before acting on them' (memory_guide ×12), 'A plan line is a hypothesis…' (verifier mindset), 'Assume flaws exist until proven otherwise' (self-review mindset), 'Follow evidence over assumption' (root-cause mindset), 'not absence of alternatives' (root-cause checklist). All D; the real mechanisms sit in verifier actions 4-5 and exploration_budget.
10. **A-class generic knowledge ~5 KB, concentrated in simplicity-guide** (anti_patterns + domain_exceptions ≈ 1.1 KB, methodology 0.4 KB) and in the actions blocks of quality-engineer, security-engineer, system-architect, technical-writer. security-engineer's two `sc-*` gotchas (610 B) are repo-only leaks shipped to every install.

Keep list (shortest form): every `description` routing gate, Ask-First trigger lists, memory category names, handoff/fallback routing, repo-index paths/budgets/naming, technical-writer naming-convention, verifier actions 1-3 (plan path, command sources, hash procedure), finding_policy (once, shared), verifier actions 4-6 + proof-written-ahead + failure-record, root-cause exploration_budget, simplicity-guide actions 1-3, repo-index action 1.

## 6. Not read

- Any file under `~/.claude/`, the repo `.claude/`, `docs/`, `CHANGELOG.md`, root `README.md` (isolation rule).
- Other agents referenced by name (backend-architect, performance-engineer, learning-guide, python-expert, deep-researcher, insight-analyst, project-manager, project-initializer, business-panel-experts, git-workflow, devops-architect, frontend-architect) — out of scope (first-half auditor).
- `commands/`, `modes/`, `core/FLAGS.md` referenced by README.md §Related.
- `src/superclaude/ARCHITECTURE.md` and `scripts/context_loader.py` were grepped only for delivery of agents/README, not read in full.
