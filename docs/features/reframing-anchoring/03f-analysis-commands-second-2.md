# 03f — Phase 2 content value classification: commands (second half) — part 2 of 2

> Continuation of [part 1](./03f-analysis-commands-second-1.md) (split by size; content unchanged).

## 2. Classification table (continued)

| File | Section | Class | Reason | Failure (B) | Mechanism / exhortation (B) |
|---|---|---|---|---|---|
| task | patterns Dependency | B (weak) | "detect circular deps, present resolution options" | R3 | Output-shape: options, no default (example shows "A)… B)… User chooses") |
| task | patterns rest | C/D | Hierarchy C; Cleanup line duplicates task_cleanup | | |
| task | examples | D | Duplicates patterns: "Extract shared interface to break cycle" | | |
| task | gotchas task-count, already-done | D | "at most 3-7 tasks"; uncertain A "Check git log… before creating" | | |
| task | gotcha workflow-task-state | C | Harness fact: "task-state may not survive the subagent boundary" | | |
| task | bounds | D | "compromises quality" | | |
| task | handoff | C | "/sc:test /sc:implement" | | |
| test | description | C | "Not for 'run the tests' or one test file" | | |
| test | role/mission | D | Duplicates description | | |
| test | syntax | C | "[--tdd] [--coverage] [--watch] [--fix]" | | |
| test | flow 1–5 | A | "Categorize tests via runner patterns"; "Run + real-time progress" | | |
| test | flow 6 Verify | C | Routing: "when the user asks for independent evidence, dispatch the verifier" | | |
| test | flags | C | "--coverage… thresholds (line ≥80%, branch ≥70%)"; "--fix… never edit a test just to make it pass" | | |
| test | outputs | C | threshold/output table | | |
| test | tools Agent (verifier) | B | "fresh-context run-and-report pass… reports every mismatch without fixing" | A3 (self-anchor) | Mechanism: isolated verifier with no implementer context; gated on explicit user request |
| test | tools rest | A | "Bash: Test runner execution" | | |
| test | patterns | A/D | TDD cycle A ("RED… GREEN… REFACTOR"); Watch D | | |
| test | examples + retry-without-diagnosis | D | "Retrying failing tests without root cause investigation" | | |
| test | gotcha baseline-first | A | "record baseline before changes" | | |
| test | bounds | D | "makes destructive changes" | | |
| test | handoff | C | "/sc:troubleshoot /sc:implement" | | |
| troubleshoot | description | C | "Not for a clear error with an obvious fix" | | |
| troubleshoot | role/mission | D | Duplicates description | | |
| troubleshoot | syntax | C | "--type bug\|build\|performance\|deployment" | | |
| troubleshoot | flow 1–2 Reproduce/Investigate | A | "read full error, identify exact trigger"; "Check git log/diff" | | |
| troubleshoot | flow 3 Hypothesize | B | "max 3 cycles before escalate to user" | A3 | Mechanism: numeric cycle cap with escalation |
| troubleshoot | flow 4 Confirm | B | "check the environment before code" when "the symptom could come from the runtime" | R2 | Ordering rule (one layer out first); trigger is a judgment call |
| troubleshoot | flow 5 Test | C/A | "commit only that test file… if… default branch, ask first" is C; failing-test-first is A | | |
| troubleshoot | flow 6–7 Fix/Verify | A | "no 'while I'm here' fixes"; "all existing tests pass" | | |
| troubleshoot | flags | C | "--fix: … stop after the Confirm step and propose the fix" | | |
| troubleshoot | tools | A | "Bash: Diagnostic command execution" | | |
| troubleshoot | examples + symptom-only-fix | D | "applies caching without profiling" | | |
| troubleshoot | gotcha evidence-fabrication | D (exhortation) | "Evidence… must precede proposals" — ordering stated, no gate/shape | (would be A1/A3) | Exhortation |
| troubleshoot | gotcha analysis-loop | B | "same conclusion twice on same question, terminate that line" | A3 | Mechanism: named trigger + action |
| troubleshoot | gotcha fix-not-test | D | Uncertain A: "the failing test is read-only for the fix" | | |
| troubleshoot | gotcha three-failure-levels | D (exhortation) | "(2) bug in expectations… the requirement is itself wrong → re-examine" — the only R1 content in scope, but no step requires stating the level | (would be R1) | Exhortation |
| troubleshoot | bounds | D | "applies risky fixes without confirmation" | | |
| troubleshoot | auto_fix_threshold | C | "approval_required: Schema changes, dependency updates" | | |
| troubleshoot | handoff | C | "/sc:improve /sc:implement" | | |
| README | whole file | D (repo-only) | Not a command; "See `.claude/rules/command-authoring.md`"; command table duplicates sc.md | | |

## 3. Anchor-point map

| File | Moment | What arrives | B step before it? |
|---|---|---|---|
| intent | flow 1 Capture | user's action request + their framing | none for the model — the command *records* the user's purpose ("Proposed outcome… quoted from the requester") but never asks the model to infer the unstated purpose or question the premise; "Keep the user's request verbatim… No rewording" |
| intent | flow 4 Approve | user corrections | n/a (user-authored) |
| load | flow 1 | prior session record (prior plan, next-actions checklist) | partial: gotcha "verify loaded memory against the current file state before acting on it" — thin |
| load | flow 2 | MEMORY.md + pointed memory files (prior AI output) | none |
| plan | flow 1 Load | spec/design doc (document anchor) + 00-intent.md | yes: review gate "still `status: draft` → stop and point to `/sc:review`"; intent read first. No step makes the model state its own purpose/criterion — the plan's "**Goal:** [One sentence]" is written at step 4, after Map and Decompose |
| plan | flow 1 (--from) | user-chosen source | none beyond the draft gate |
| plan | flow 5 Interrogate | own plan (self-anchor) | post-hoc footer only |
| pm | flow 1 Analyze | action request | none — goes straight to "classify complexity" and strategy |
| pm | flow 4 Monitor | delegates' results | none |
| promote-feature | flow 1–3 | slug + candidate files | none; mechanical file operation, no judgment anchor (acceptable) |
| recommend | flow 1–3 | request keywords → keyword_map | none; the map itself is the anchor ("debug (error\|bug\|not working): /sc:troubleshoot") — no purpose inference, no "what is the user trying to achieve" |
| reflect | flow 1 | session work (own prior plan) | none before; flow 2 compares to 00-intent.md after the fact |
| research | flow 1 Understand | query | partial: "Success criteria" listed before Plan, unspecified |
| research | flow 3 Execute | sources (document anchors) | yes: "Adaptive replan when sources conflict, run thin…"; gotcha "≥2 independent sources" |
| review | flow 2 Gather | artifact + author's spec/plan/PR description (A4 rationale) | I0 partial: 00-intent.md read. A4: none — the rationale and the artifact arrive in the same step; no "form your own expectation before reading the description" ordering, no withholding |
| review | flow 4 Challenge | own categorisation | yes: "before categorizing, answer in plain words…" (after rationale already read) |
| review | flow 8 --audit-delegated | recorded choice + ★ marker | yes: "never the recorded choice or a ★/recommendation marker" — only for `mode: delegated` rows and only when the flag is given |
| review | tools Agent (--structured) | artifact + context to a subagent | deferred to "delegate packet rule in core/rules/RULES_DELEGATION.md" (out of scope) |
| roadmap | flow 1 Analyze | PRD (document anchor; user's frame) | none; gotcha "scope must match PRD… exactly" locks the frame |
| roadmap | flow 3 Consult | domain agents' findings | none |
| save | flow 1 Analyze | own session (self-anchor) | none before; compaction "Claim strength" rule governs what crosses to the next session |
| sc | flow 1 Parse | command + args | none (dispatcher; acceptable) |
| select-tool | flow 1 Parse | operation as the user framed it ("rename… 10 files") | none; minor |
| spec-panel | flow 1 Analyze | spec (document anchor) | none before; the six fixed lens questions act as partial reframers after reading |
| spec-panel | flow 4 Collaborate | experts' outputs (own prior output) | partial: iteration-escalation "change the lens, not the severity" |
| task | flow 1 Analyze | action request | none |
| task | flow 6 Validate | sub-agent results | yes: "a sub-agent's result is a claim to check, not evidence" |
| task | patterns Dependency | circular-dep options | partial: "present resolution options" (no default) |
| test | flow 6 / tools Agent | implementer's plan + verifier | yes (isolation): "fresh-context run-and-report pass" — only on request |
| troubleshoot | flow 1 Reproduce | issue text with a suspected cause (A1) | none that quarantines the user's hypothesis; Reproduce/Investigate precede Hypothesize (ordering a bare model already follows) |
| troubleshoot | flow 3 Hypothesize | own hypothesis (A3) | yes: "max 3 cycles before escalate"; gotcha analysis-loop |
| troubleshoot | flow 4 Confirm | code-level frame (R2) | yes: "check the environment before code" |

I0 check (purpose stated and success criterion derived BEFORE acting): **no file in scope has such a step.** Closest: research flow 1 "Success criteria" (two words, unspecified); intent records the *user's* "Proposed outcome" but forbids the model from adding anything ("No solutions… No rewording"); plan/review *read* 00-intent.md when it exists but do not make the model state the purpose of the request in front of it. reflect flow 2 compares against purpose only after delivery.

## 4. Totals per class (approximate bytes; 18 files, 77,256 B)

| Class | Rows (approx.) | Bytes (approx.) | Share |
|---|---|---|---|
| A | 22 | 3,500 | 5% |
| B | 22 (of which 7 weak/under-specified) | 6,800 | 9% |
| C | 110 | 37,000 | 48% |
| D | 95 | 28,700 | 37% (incl. README 3,277 repo-only) |

Mixed rows were split by estimate. C is dominated by path/frontmatter conventions, flag semantics, routing tables and the sc.md/README command lists (one of which is redundant).

## 5. Top 10 findings (ranked)

1. **I0 gap is total.** No command in scope makes the model state the purpose behind the request and derive a success criterion before acting. intent.md records the user's purpose but bans model inference ("Keep the user's request verbatim… No rewording"); plan/review only *read* `00-intent.md` when it happens to exist. The nearest thing, research flow 1 "Success criteria", is two words with no required output.
2. **review.md has no A4 isolation for the ordinary review path.** Flow 2 Gather delivers artifact and author rationale together; the only withholding mechanism (flow 8, "never the recorded choice or a ★/recommendation marker") is gated behind `--audit-delegated` and applies to `mode: delegated` spec rows only. A Challenge-before-Categorize gate exists (flow 4) but runs after the rationale has been read. Extending the flow-8 isolation shape (reviewer forms own expectation before reading the description) to all reviews would be the largest B gain in scope.
3. **D deletion: ~11 KB of duplicates.** Every file carries a `<mission>` restating the description, a `<bounds>` restating the flow, example tables restating flags, and gotchas restating flow steps (promote-feature: slug-collision/partial-match/cross-link-blast duplicate steps 4/2/7 and are then duplicated a third time in the error-path examples; sc.md `<commands>` duplicates README.md's table).
4. **Anti-B content:** plan gotcha "No expand to adjacent features" and roadmap gotcha "Workflow scope must match PRD or feature request exactly" instruct frame lock (R2) — the opposite of the chosen principle. recommend.md's `keyword_map` maps surface words straight to commands ("error|bug|not working → /sc:troubleshoot") with no "what is the user trying to achieve" step.
5. **B that are exhortations (D by the brief):** troubleshoot gotcha evidence-fabrication ("Evidence… must precede proposals") and three-failure-levels ("the requirement is itself wrong → re-examine") carry the only R1/A1 content in scope but require no step or output; converting them into a flow gate ("state the failure level before Fix") would make them B.
6. **Best existing B mechanisms worth keeping as the pattern:** review flow 8 delegate isolation (R3/A4); research flow 3 named re-plan triggers + ≥2-source gate (A3/A2); task flow 6 "a sub-agent's result is a claim to check, not evidence" (A2); test verifier "fresh-context run-and-report" (A3); save compaction "an assumption stays an assumption… never upgrades it" (A3 re-entry); troubleshoot "max 3 cycles", analysis-loop, "environment before code" (A3/R2).
7. **A deletion: ~3.5 KB.** test.md flow 1–5 and the TDD pattern, troubleshoot flow 1–2 and 6–7, all `<tools>` lists except the few project-specific entries (`git config user.name`, verifier agent, `git mv`), load's "verify the project path first (ls, git remote -v)", review "flag issues but do not fix".
8. **pm.md, roadmap.md, task.md receive the action request and delegate results with no B step at all** (orchestrators are the point where I0 compounds: a delegate inherits a purpose the orchestrator never inferred).
9. **README.md (3,277 B) is repo-only** (references `.claude/rules/command-authoring.md` and pytest); its command table duplicates sc.md. Keep one list.
10. **Weak Bs to tighten or drop:** load flow 6 Session Goal (undefined trigger "changes direction", only if the user supplies a goal); plan flow 5 Interrogate ("alternatives not taken" written in the footer after decomposition — rationalisation, not pre-anchor); reflect 2.5 Misunderstanding-Audit (retrospective "spot moments"); sc.md `<meta>` "version: 4.27.2" is a stale-prone repo leak.

## 6. Not read

Per the isolation rule: `~/.claude/`, repo `.claude/`, `docs/`, `CHANGELOG.md`, root `README.md`, `core/rules/RULES_*.md` (referenced by many steps — e.g. the delegate packet rule, `<doc_output_convention>`), `modes/RESEARCH_CONFIG.md`, `agents/*`, and the other 20 command files (assigned to the sibling auditor). Classification of pointer sections assumes the pointed-to rule exists; whether those rules are themselves B or D is outside this report.
