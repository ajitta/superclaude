# Phase 2 content-value classification — agents (first half) — part 3 of 3

> Continuation of [part 1](./03c-analysis-agents-first-1.md) (split by size; content unchanged).

## 2. Classification table (continued)

| File | Section | Class | Reason | Failure (B) | Mechanism / exhortation (B) | Quote | ~Bytes |
|---|---|---|---|---|---|---|---|
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
