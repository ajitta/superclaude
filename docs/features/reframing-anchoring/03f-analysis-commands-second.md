# 03f — Phase 2 content value classification: commands (second half)

Scope: `src/superclaude/commands/` — intent, load, plan, pm, promote-feature, recommend, reflect, research, review, roadmap, save, sc, select-tool, spec-panel, task, test, troubleshoot, README.md. Branch `feature/reframing-anchoring`. Judged from the file text only (plus `ARCHITECTURE.md` / `context_loader.py` for delivery).

Delivery: command files are CC-native slash commands installed to `~/.claude/commands/sc/` (ARCHITECTURE.md §commands). The `description` frontmatter is the always-visible part; the body loads on invocation. `README.md` has no frontmatter and is a repo doc, not a command.

## 1. Files read (bytes)

| File | Bytes |
|---|---|
| intent.md | 4,326 |
| load.md | 3,529 |
| plan.md | 5,479 |
| pm.md | 2,381 |
| promote-feature.md | 6,034 |
| recommend.md | 3,460 |
| reflect.md | 2,665 |
| research.md | 3,922 |
| review.md | 7,005 |
| roadmap.md | 4,214 |
| save.md | 6,348 |
| sc.md | 3,799 |
| select-tool.md | 3,895 |
| spec-panel.md | 4,378 |
| task.md | 4,285 |
| test.md | 3,635 |
| troubleshoot.md | 4,624 |
| README.md | 3,277 |
| **Total** | **77,256** |

## 2. Classification table

Class key: A = bare model already does it; B = structural remedy (names failure + mechanism/exhortation); C = project fact; D = other (exhortation, persona, duplicate, repo-only, unmeasurable, uncertain A).

| File | Section | Class | Reason | Failure (B) | Mechanism / exhortation (B) |
|---|---|---|---|---|---|
| intent | description | C | Routing: "Not for ideas mentioned in passing" | | |
| intent | role/mission | D | Duplicates description: "Capture a request as an intent record" | | |
| intent | syntax | C | "/sc:intent [request]" | | |
| intent | flow 1–4 Capture/Fill/Draft/Approve | B | Records problem + outcome + constraints BEFORE analysis: "before any analysis"; "No solutions, alternatives, architecture" | I0 (partial), R1 (negative) | Mechanism: ordering (purpose record precedes plan) and isolation (solutions excluded). Caveat: captures the user's stated purpose verbatim; the model never infers purpose or sets its own criterion; "Keep the user's request verbatim" enshrines a wrong premise (R1) — only "Open questions" mitigates |
| intent | flow 5 Save | C | Path/frontmatter: "`docs/features/<slug>/00-intent.md`… `status: approved-for-plan`" | | |
| intent | flow 6 Handoff | C | Routing: "open solution space… → /sc:brainstorm" | | |
| intent | outputs | C | "the record, in the shape of the intent-skeleton" | | |
| intent | tools | A/C | Tool picks are obvious; keep "`git config user.name` for the Author line" | | |
| intent | examples table | D | Restates fallback/flow: "rename this variable… no file" | | |
| intent | example intent-skeleton | C | Record template: "## Problem / ## Proposed outcome" | | |
| intent | gotchas solution-creep, rephrase-drift, question-flood | D | Restate `<never>` and Fill step: "five is a ceiling, not a target" | | |
| intent | gotcha existing-intent | C | Archive convention: "moving it to archive/ per RULES_DOCS" | | |
| intent | bounds | D | Duplicates flow: "saves after approval" | | |
| intent | handoff | D | Duplicates flow 6: "/sc:brainstorm /sc:plan /sc:design" | | |
| load | description | C | Routing: "Not for resuming work or 'let's continue'" | | |
| load | role/mission | D | "Session lifecycle management with the project memory folder" | | |
| load | syntax | C | "--type project\|config\|deps\|checkpoint" | | |
| load | flow 1–2 Load | C | Which files exist and are already in context: "MEMORY.md is already in context" | | |
| load | flow 3–5 Discover/Activate/Validate | D | Unmeasurable: "Activate: project context and workflow preparation" | | |
| load | flow 6 Session Goal | B (weak) | "record it as a 1-line objective; restate it when the work changes direction" | A3 (re-entry) | Mechanism-lite: writes and restates an objective; trigger "changes direction" undefined; only if the user supplies a goal — no inference |
| load | flags | C | "--refresh: re-read sources and replace loaded memory" | | |
| load | storage | C | Pointer: "SSOT in /sc:save <storage>" | | |
| load | tools | A | "Glob/Read: memory folder" | | |
| load | examples table | D | Restates flags: "Fresh dep analysis" | | |
| load | example load-wrong-project | A | "verify the project path first (ls, git remote -v)" | | |
| load | gotcha stale-memory | B (thin) | "verify loaded memory against the current file state before acting" | A2 | Ordering gate (verify before act) but names no concrete check — near-exhortation |
| load | gotcha dual-persistence | D | Duplicates flow 1–2: "Check both the memory folder and auto memory" | | |
| load | bounds does/never | D | "loads without validation" — unmeasurable | | |
| load | bounds fallback | C | "Read CLAUDE.md/PLANNING.md/TASK.md" when folder absent | | |
| load | handoff | C | "/sc:analyze /sc:index-repo /sc:task" | | |
| plan | description | C | Routing: "Not for 'what's the plan?' — answer… inline" | | |
| plan | role/mission | D | Duplicates description: "Write detailed implementation plans with TDD tasks" | | |
| plan | syntax | C | "[--from …] [--output …] [--phases N] [--pr-bundle]" | | |
| plan | flow 1 Load (source + review gate) | B + C | "still `status: draft`… → stop and point to `/sc:review`"; "Also read… `00-intent.md`" | A2, R1, I0 | Mechanism: hard gate (unreviewed spec cannot be planned) + ordering (intent read before mapping). Source routing is C |
| plan | flow 2 Map | A | "List files to create/modify" | | |
| plan | flow 3 Decompose | C | Convention: "each phase = single-commit unit" | | |
| plan | flow 4 Template | C | Header/footer convention: "proof always names the command and its expected output" | | |
| plan | flow 5 Interrogate | B (weak) | "which options were not taken and why" | R3, A3 | Output-shape mechanism, but placed in the footer AFTER decomposition — records rationalisation, does not precede the anchor |
| plan | flow 6 Save | C | "`docs/plans/<feature-name>-<username>-YYYY-MM-DD.md`" | | |
| plan | flow 7 Handoff | C | "Ready for /sc:implement --plan" | | |
| plan | flags | C | "--phases N: preferred phase count; a hint" | | |
| plan | outputs | C | "Split plan: `05<letter>-plan-<phase>.md`" | | |
| plan | tools | A | "Read: Spec + codebase analysis" | | |
| plan | templates | C/A | Header/footer shape is C ("**Goal:** [One sentence]"); TDD 4-step list is A ("Write failing test") | | |
| plan | examples | D | Flag illustrations: "Custom output path" | | |
| plan | size_note | C | Pointer: "RULES_DOCS.md `<doc_output_convention>` (Size)" | | |
| plan | gotcha existing-plan | D | Uncertain A: "Check if plan already exist" | | |
| plan | gotcha scope-match | D (anti-B) | "No expand to adjacent features" — reinforces frame lock (R2) | | |
| plan | gotchas phase-vs-pr, workflow-fanout | C | Naming convention; harness fact "subprocess writes discarded" | | |
| plan | bounds | D | Duplicates gate/flow: "skips spec review"; fallback "Ask… when… ambiguous" is A | | |
| plan | handoff | D | Duplicates flow 7 | | |
| pm | description | C | Routing: "one task from scope to review — /sc:agent" | | |
| pm | role/mission/note | C/D | Note "Full agent def in agents/project-manager.md" is C; mission is D | | |
| pm | syntax | C | "--strategy brainstorm\|direct\|wave" | | |
| pm | flow | D/C | "parse intent + classify complexity" is exhortation; Strategy row is C ("Direct (precise: main thread…)") | | |
| pm | flags | C | "--verbose: report each sub-agent dispatch" | | |
| pm | patterns | C | Agent routing: "requirements-analyst → system-architect → specialists" | | |
| pm | examples | D | Illustrate patterns: "not pm: edit directly" | | |
| pm | gotcha direct-work-first | D | Duplicates description + RULES_DELEGATION: "single file, <3 steps" | | |
| pm | bounds | D | "bypasses documentation" | | |
| pm | handoff | C | "/sc:implement /sc:task /sc:research" | | |
| promote-feature | description | C | Routing: "Not for a 'consider promotion' hint" | | |
| promote-feature | role/mission | D | Duplicates description | | |
| promote-feature | syntax | C | "[--dry-run\|--apply]" | | |
| promote-feature | flow 1–8 | C | Project procedure: "strip suffix/username/date"; "Default `--dry-run` exits here"; type→phase mapping | | |
| promote-feature | flags | C | "--from <path>: promote this one file" | | |
| promote-feature | outputs | C | "Inbound link warning report" | | |
| promote-feature | tools | A/C | Obvious picks; "`git mv` for tracked rename" is C | | |
| promote-feature | examples (table + 2 error-paths) | D | Duplicate gotchas: "Abort with error. User must either pick different slug" | | |
| promote-feature | gotchas slug-collision, partial-match, cross-link-blast | D | Duplicate flow 4/2/7: "Never silently overwrite" | | |
| promote-feature | gotchas multi-of-same-phase, frontmatter-preserve | C | "second→`04a-design-<distinguisher>.md`"; "ADD `status:` + `revised:`" | | |
| promote-feature | bounds | D | Duplicates flow: "run without explicit --apply flag" | | |
| promote-feature | handoff | C | "/sc:cleanup /sc:design /sc:plan" | | |
| recommend | description | C | "Not for a request whose command is already obvious" | | |
| recommend | role/mission | D | Duplicates description | | |
| recommend | syntax | C | "--expertise beginner\|intermediate\|expert" | | |
| recommend | flow | D | Generic: "Analyze… Classify… Map… Recommend" | | |
| recommend | flags | C | "--alternatives: list other viable commands" | | |
| recommend | keyword_map | C (anti-B) | Routing table: "debug (error\|bug\|not working): /sc:troubleshoot" — keyword→command without purpose inference induces R2 | | |
| recommend | project_detect | C | "react (package.json+react): --c7 --play" | | |
| recommend | expertise_adapt | D | Tone/persona: "expert: terse output" | | |
| recommend | examples | D | "ambiguous: ask what aspect" (restates fallback) | | |
| recommend | gotchas | D | Exhortations: "recommend the simplest command first" | | |
| recommend | bounds | D | "executes commands or modifies files" | | |
| recommend | handoff | C | routing list | | |
| reflect | description | C | "Not for the routine end-of-turn summary" | | |
| reflect | role/mission/note | D/C | Mission D; note "to produce new test evidence, run /sc:test" is C | | |
| reflect | syntax | C | "--type task\|session\|completion" | | |
| reflect | flow 1, 3 | D | "judge completeness of info gathered"; "weigh done-criteria" | | |
| reflect | flow 2 Validate | B | "compare its Proposed outcome with what was delivered and record the gap" | I0 | Mechanism: output-shape comparing delivery to the recorded purpose — post-hoc only (after the work) |
| reflect | flow 2.5 Misunderstanding-Audit | B (weak) | "what trigger misread, what actual intent, what rule stop it" | I0, R1 | Output-shape (three fields) but retrospective and relies on "spot moments" — half exhortation |
| reflect | flow 3.5 Gotchas-Gardening | C | "`# Last reviewed:` older 90 days → warn" | | |
| reflect | flow 4 Persist | C | Routing + gate: "write them only when the user agrees" | | |
| reflect | flags | C | "--validate: … unrelated to the global --validate" | | |
| reflect | examples | D | Restates flags: "Done-ready judge" | | |
| reflect | gotchas | D | Uncertain A: "cite real test output + file state, not predict result" | | |
| reflect | bounds | D/C | Routing bit "delegate those to /sc:analyze --focus rules" is C | | |
| reflect | handoff | C | "/sc:improve /sc:troubleshoot" | | |
| research | description | C | "Not for one doc lookup or fetching a URL" | | |
| research | role/mission | D | Duplicates description | | |
| research | syntax | C | "--strategy planning\|intent\|unified" | | |
| research | flow 1 Understand | B (under-specified) | "Complexity + ambiguity check \| Success criteria \| Prior research check" | I0 | Ordering mechanism (criteria precede Plan) but two words — no requirement to state the criterion or derive it from purpose |
| research | flow 2 Plan | C | "ask or wait as the strategy says" | | |
| research | flow 3 Execute | B | "Adaptive replan when sources conflict, run thin, or leave the core question unanswered" | A3 | Mechanism: named re-plan triggers |
| research | flow 4 Validate | D | Generic labels: "Cross-source verify \| Credibility tier" | | |
| research | flow 5 Synthesize | C | "`docs/research/<topic>-<username>-YYYY-MM-DD.md`" | | |
| research | flags | C | "--depth quick always runs without asking" | | |
| research | depth | C | "exhaustive: 5+ hops, subagent delegate"; pointer to RESEARCH_CONFIG | | |
| research | outputs | C | path table | | |
| research | tools | C | "Tavily: tavily-search, tavily-extract…"; "/sc:save (suggest…)" | | |
| research | examples | D | "low-confidence sources → adaptive replan" | | |
| research | gotcha single-source | B | "each load-bearing claim needs ≥2 independent sources… label… single-source" | A2 | Mechanism: count threshold + output label |
| research | gotcha source-quality | A | "never use Wikipedia or Reddit as a primary source" | | |
| research | bounds | D | "carries raw payloads between hops" (unmeasurable here) | | |
| research | handoff | C | routing list | | |
| review | description | C | "Not for a codebase-wide audit… — /sc:analyze" | | |
| review | role/mission | D | Duplicates description | | |
| review | syntax | C | "--scope pr\|diff\|file\|branch\|plan\|design\|spec" | | |
| review | flow 1 Scope | D | "pick review range" — obvious | | |
| review | flow 2 Gather | B + C | "`00-intent.md` from the feature folder when present"; "Find in docs/specs/ or docs/plans/" | I0 | Ordering (purpose doc read before judging). But artifact + author's spec/rationale arrive together — no isolation (A4 gap) |
| review | flow 3 Review Dim 1 | B (weak) | "does the artifact match the intent (the spec, and… `00-intent.md`)" | I0 | Output-shape (fidelity dimension); criterion comes from the doc, not the model |
| review | flow 3 Review Dim 2 | A | "correctness for code, planning rigor for plan" | | |
| review | flow 3 Review Dim 3 | C | Project fact: "CLAUDE.md, AGENTS.md, `.claude/rules/**`… stale" | | |
| review | flow 4 Challenge | B | "before categorizing, answer in plain words — Under what condition does the approach fail?" | A4 | Mechanism: ordering gate + three forced questions. Runs after the author rationale was read, so it counters, not prevents, the anchor |
| review | flow 5 Categorize | D | "Critical \| Important \| Suggestion" — generic | | |
| review | flow 6 Verify | D | "evidence fits the artifact type" — generic | | |
| review | flow 7 Process | D | Uncertain A: "withdraw or downgrade any finding the evidence does not support" | | |
| review | flow 8 Delegated-decision audit | B | "never the recorded choice or a ★/recommendation marker"; "the delegate forms its own candidates" | R3, A4, A1 | Mechanism (strongest in scope): information isolation — delegate receives the question, not the answer or the star; honest limit stated ("a delegate that can read the repo can still find the recorded choice"). Gated behind --audit-delegated and `mode: delegated` rows only |
| review | flow 9 Spec gate | C | "set `status: approved-for-plan`" only with user go-ahead | | |
| review | flags | C | "--scope… unrelated to the global --scope" | | |
| review | outputs | D | Generic: "Categorized findings" | | |
| review | tools | C/A | Agent entry C: "Read the delegate packet rule… before dispatch, since it sets what the reviewer's prompt leaves out"; rest A | | |
| review | focus_agent_mapping | C | "security → @security-engineer" | | |
| review | examples table | D | "Review PR #42" | | |
| review | example finding-self-check | D | Duplicates flow 7: "Withdraw: the finding assumed pattern A" | | |
| review | gotcha scope-focus | C | "review the changed lines and the code they affect" | | |
| review | gotcha no-unsolicited-fixes | A | "flag issues but do not fix them unless asked" | | |
| review | bounds | D | "auto-merge, auto-approve" | | |
| review | handoff | C | routing list | | |
| roadmap | description | C | "Not for a TDD plan from a spec (use /sc:plan)" | | |
| roadmap | role/mission | D | Duplicates description | | |
| roadmap | syntax | C | "--strategy systematic\|agile\|enterprise" | | |
| roadmap | flow 1–2, 4 | D | "Parse PRD + understand requirements"; "Workflow structure + dependency mapping" | | |
| roadmap | flow 3 Consult | C | Harness fact: "they return findings, and the main loop writes the doc" | | |
| roadmap | flow 5 Validate | C | Doc convention: "unchecked box with an empty `Evidence:` line" | | |
| roadmap | flow 6 Document | C | "`docs/plans/<topic>-workflow-<username>-YYYY-MM-DD.md`" | | |
| roadmap | flags | C | "enterprise adds compliance and validation requirements" | | |
| roadmap | outputs | C | path table | | |
| roadmap | tools | A/C | "agents return findings, the main loop writes the doc" is C | | |
| roadmap | examples + workflow-no-prd | D | "Make PRD first: /sc:brainstorm → /sc:design" | | |
| roadmap | gotchas scope-match, step-granularity | D (anti-B) | "Workflow scope must match PRD or feature request exactly" — locks the frame (R2) | | |
| roadmap | gotcha name-vs-harness-tool | C | "distinct from the harness Workflow tool" | | |
| roadmap | bounds | D | "generates without analysis" | | |
| roadmap | handoff | C | "/sc:implement /sc:task" | | |
| save | description | C | "Not for 'remember this' or the end of a task" | | |
| save | role/mission | D | Duplicates description | | |
| save | syntax | C | "--type session\|learnings\|context\|all" | | |
| save | flow 1, 5, 6 | D | "session progress + discoveries"; "data integrity + no duplicates" | | |
| save | flow 2–3, 3.5, 3.6, 4 | C | File names and detection facts: "first line `branch: <name> @<short sha>`"; "`violated_rule: \"[RNN Name]\"`"; "`CLAUDE_CODE_DISABLE_AUTO_MEMORY`" | | |
| save | flow 7 Session Goal | D | "evaluate completion status (done/partial/deferred)" — post-hoc, only if set | | |
| save | compaction_strategy Preserve (3) + Claim strength | B | "what was asked, decided, ruled out… — stated exactly"; "an assumption stays an assumption… never upgrades it" | A3 (re-entry), A2 | Mechanism: governs what information crosses the session boundary and at what claim strength |
| save | compaction_strategy rest | C/D | Preserve/Discard lists are C-ish ("Discard… verbatim tool output"); "Format: structured summary" D | | |
| save | storage | C | "Branch slug: `git branch --show-current` with `/` → `-`"; agent-memory paths | | |
| save | outputs | C | type → file table | | |
| save | tools | A | "Write/Edit: memory folder" | | |
| save | examples + save-incomplete-work | D | "reach stable state first" | | |
| save | gotcha no-ephemeral | C | "this session's progress… belong in the session_ file" | | |
| save | gotcha verify-value | D | Exhortation: "Will this be useful in future conversation?" | | |
| save | bounds | D/C | fallback "auto memory only, and tell the user" is C | | |
| save | handoff | C | "/sc:load /sc:reflect" | | |
| sc | description | C | "Not for a request that matches one command" | | |
| sc | role/mission | D | "main entry for all features" | | |
| sc | syntax/flow | C | "invoke the matching /sc:<name> command via the Skill tool" | | |
| sc | commands list | C (dup) | Routing table "intent: Capture a request…" — duplicates README table; keep one | | |
| sc | examples + unknown-command | D | "Use /sc:help for available commands" | | |
| sc | meta | D | Repo leak, goes stale: "version: 4.27.2" | | |
| sc | gotchas | D | Authoring-time: "When adding new commands, update this dispatcher" | | |
| sc | bounds | D | "bypass command validation" | | |
| sc | handoff | C | "/sc:recommend /sc:help" | | |
| select-tool | description | C | "Not for normal tool selection — choose from context" | | |
| select-tool | role/mission | D | Duplicates description | | |
| select-tool | syntax | C | "[--analyze] [--explain]" | | |
| select-tool | flow | C/D | Step 3 "the chosen tool is connected in this session" is C-gate; 1/4 D | | |
| select-tool | flags | C | "--explain: … why the runner-up loses" | | |
| select-tool | decision_matrix | C/A | Routing "Context7 (--c7)… Fallback WebSearch" is C; "Grep… then Edit" rows are A | | |
| select-tool | examples + wrong-tool-choice | D | "a rename is a symbol op" | | |
| select-tool | gotchas | D | Duplicate of step 3: "never recommend a tool the Check step did not find" | | |
| select-tool | bounds | D | "override the user's explicit tool preference" | | |
| select-tool | handoff | C | "/sc:implement /sc:analyze" | | |
| spec-panel | description | C | "Not for reading a spec or one reviewer's feedback" | | |
| spec-panel | role/mission | D | Duplicates description | | |
| spec-panel | syntax | C | "--mode discussion\|critique\|socratic" | | |
| spec-panel | flow 1–3, 5 | D | "parse spec"; "pick experts"; "improvement roadmap" | | |
| spec-panel | flow 4 Collaborate | D | Output-shape "notes explicitly where experts disagree" — not one of the eight failures | | |
| spec-panel | flags | C | "a command-local enum, unrelated to the global --focus" | | |
| spec-panel | experts | C | Lens definitions: "Nygard… 'What happens when this fails at 3AM?'" (reframing questions, project-chosen) | | |
| spec-panel | modes | C | "critique: Issue → Severity → Recommendation → Priority" | | |
| spec-panel | focus_areas | C | "reliability (Nygard,Majors)" | | |
| spec-panel | examples + spec-no-document | D | "provide spec: /sc:spec-panel @api-spec.yml" | | |
| spec-panel | gotchas existing-spec, necessity-test, lens-not-impersonation | D | "never fabricate quotes" (persona guard); "[R18 Necessity Test]" pointer | | |
| spec-panel | gotcha iteration-escalation | B | "when a pass repeats one, change the lens… not the severity" | A3 | Mechanism: named trigger + action for the panel loop; narrow domain |
| spec-panel | bounds | D | "replaces human judgment… legal guarantees" | | |
| spec-panel | handoff | C | "/sc:design /sc:implement" | | |
| task | description | C | "specialist waves — /sc:pm; one task… — /sc:agent" | | |
| task | role/mission | D | Duplicates description | | |
| task | syntax | C | "--strategy sequential\|parallel\|adaptive" | | |
| task | flow 1, 3, 5 | D | "Parse requirements"; "Pick execution order" | | |
| task | flow 2 Decompose | C | Convention: "empty evidence note in its TaskCreate description" | | |
| task | flow 4 Checkpoint | C | Measurable gate: ">3 files → present numbered plan → wait" | | |
| task | flow 6 Validate | B | "a sub-agent's result is a claim to check, not evidence" | A2 (delegate output) | Mechanism: completion gated on cited evidence, not the delegate's report |
| task | flow 7 Cleanup | C | "delete completed and cancelled tasks" | | |
| task | flags | C | "--dry-run: … delete nothing" | | |
| task | task_cleanup | C | "stale: … deleted only after the user confirms" | | |
| task | tools | A | "Agent: Sub-agent delegation" | | |
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
