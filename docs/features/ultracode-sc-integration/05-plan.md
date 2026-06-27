---
status: complete
revised: 2026-06-27
---

## Feature: Integrate SuperClaude content with new harness features (ultracode effort, Workflow tool, goal-driven execution)

Goal: make `src/superclaude/` content compatible + integrated with the harness execution layer (ultracode effort level, the deterministic multi-subagent Workflow tool, goal-driven loop/budget). Conclusions are encoded from the prior research (`./02-research.md`), not re-derived. Thesis: harness execution and SC governance are orthogonal layers that compose; SC decides WHETHER + WITH WHAT INTENT to fan out, the Workflow tool EXECUTES the fan-out SC ships no runtime for.

All edits land inside `src/superclaude/` and are self-contained (no docs/.claude/tests path refs — install-tree-boundary). File writes happen in the main loop; this plan is the ordered apply list.

### Surface: RENAME `/sc:workflow` → `/sc:roadmap` (name-collision removal)
The SC slash command shares the word "workflow" with the harness Workflow tool. Rename the command token (filename stem is the command identity per command-authoring.md:29/84). `git mv` first, then retoken the renamed file's identifiers, then fix every cross-file reference.
- File rename + in-file identifiers: `<component name>`, `<role command>`, `<syntax>`, description, two examples (workflow.md:2/4/6/10/57/59).
- Disambiguation gotcha (R8): states `/sc:roadmap` is the content/plan command, distinct from the harness Workflow tool — the edit that actually closes the rename's integration gap.
- Cross-file `/sc:workflow` token refs: README.md:43, estimate.md:62, design.md:78, recommend.md:29, requirements-analyst.md:78, system-architect.md:77, RULES.md:190/192.
- BARE-ID refs the original RENAME grep missed (token form `workflow:`, not `/sc:workflow`): dispatcher listings sc.md:47 and help.md:47. Added for complete coverage.
- Stale command-list ref: RULES.md:147 `05-plan (plan, workflow)` lists the producing commands (brainstorm/plan/workflow), not doc-type vocab — post-rename "workflow" there dangles → `(plan, roadmap)`.
- OUT OF SCOPE (per user decision, intentionally retained): doc-type "workflow" vocabulary at RULES.md:153/154 (`workflow→plans/`, `workflow→-workflow`) and `05a-plan-workflow.md` filenames. These name an artifact KIND, not a command — they collide with nothing. Result: command verb (roadmap) and artifact suffix (-workflow) differ by design.
- Grounding: research thesis (orthogonal layers); command-authoring.md:29/84/88.

### Surface: RULES.md (governance/execution layer split)
- R-1 (insert): opening "Axis:" line in `<sub_agent_decision>` — the section governs the single Agent-tool delegate; authoring a multi-subagent Workflow is the orthogonal harness EXECUTION layer. Without it, "Never sub-agent: sequential A→B" falsely reads as forbidding harness pipelines (which embrace sequenced work). Grounding: research 3.1/§1/OV-1.
- R-2-3 (replace, revised): extend the Delegate packet line — six fields pack into the one free-form `agent(prompt)` arg (many-to-one); `opts.schema`/StructuredOutput hardens RETURN SHAPE only (a well-typed citation can be fabricated → re-grep stays mandatory); resume-from-cache may cite stale state and MUST be re-validated (R15 gates resume). New "Workflow fan-out (OUT):" clause — every `parallel()` must `log()` dropped/null thunks before `filter(Boolean)` (silent drop = R15 partial-evidence risk). Revised: dropped the out-of-tree "context-leak" token (defined only in non-shipped gotchas file). Grounding: SYN-1, OV-3/§4.2, §7.5, Recipe-f.
- R-5a/R-5b: workflow_gates command-token rename (RULES.md:190/192); R-5b also retokens the label "Workflow tasks" → "Roadmap tasks" to remove the residual capitalized "Workflow" noun. This region OVERLAPS the RENAME surface — emitted ONCE; the relabel variant wins.

### Surface: PRINCIPLES.md (compose-not-collide foundation)
- P1 (insert): "Layered-Composition" principle — governance content composes with harness execution as orthogonal layers; content ships no fan-out runtime. The foundational framing downstream edits depend on. Grounding: §1, Rec-1, context_loader.py:501-529 (no --delegate key).
- P2 (replace): append to Goal-Driven-Execution lens — R20 criteria are the quality gate a deterministic harness loop/budget terminates against; prefer harness loop for termination, R20 stays the gate. Grounding: §4.1/OV-5.

### Surface: FLAGS.md (primitive disambiguation + cap/posture arithmetic)
- `--delegate`: governs SC policy (Agent tool), NOT the harness Workflow executor; a Workflow fans out with no --delegate set. Grounding: §1/§2 matrix, Rec-1.
- `--concurrency`: batches tool-calls-per-message, not processes; Workflow fan-out is hard-capped at min(16, cpu-2) which silently wins on process count. Grounding: §7.6, Rec-5.
- `--uc`: the ≥60% proactive band still fires under token-unbounded effort modes (ultracode) as a context-window-overflow guard (compressed TRANSPORT ≠ token cost). Grounding: §3.3, Recipe-d, Rec-5.

### Surface: MODE_Orchestration.md (the fan-out execution home)
- Insert `<fan_out_execution>` + `<examples>` after `</behaviors>`: when-to-author (3+ streams / ~20K tokens), pipeline-default vs parallel-barrier, packet-as-prompt with verbatim intent, harness caps (min(16,cpu-2), 1000 agents), discarded-write → return-markdown → main-loop-Write + main-loop-only >3-file approval, schema-shape-not-evidence re-validation, main-loop-only mode/MCP injection (name --seq/--c7/--tavily in the prompt). Closes the mode's zero-Workflow-content gap. Grounding: Recipe-b/c, Rec-1/2/3/4, §6/§7.1/§7.6/A.3.

### Surface: MODE_Token_Efficiency.md (ultracode token posture)
- Insert `## Ultracode Posture`: orthogonal axes (PROCESS breadth vs OUTPUT compression coexist), ≥60% proactive --uc holds as window guard / only money-saving reach dropped / safety floor intact, per-subagent compression does NOT raise the 1000-agent cap, compressed output stays advisory. Dropped caveman/context-mode plugin attribution (research §7.7 NOT-VERIFIABLE-FROM-REPO) — kept the harness-verified cap invariant. Grounding: §3.3, Recipe-d, §7.7.

### Surface: doc-producer commands (design/plan/implement/task — fan-out FS-write rule)
- design.md / plan.md: subagents RETURN markdown (subprocess writes discarded) → main loop performs the native Write per outputs routing. No >3-file checkpoint (single doc).
- implement.md: subagents return code/results → main loop applies edits AND runs the >3-file checkpoint (flow step 3, subagents cannot pause). Grounded in Recipe-c.
- task.md: harness task-state MAY NOT survive the subagent boundary → main loop owns TaskCreate/TaskUpdate + the >3-file checkpoint (flow step 4). Hedged — task-state survival is an OPEN harness question (matrix line 42 / IR-3), not settled fact.
- Grounding: Rec-2, Recipe-c, matrix lines 41/42/48.

### Verification
Verification level 0-1 (text-only content edits) — static inspection plus the structural test suite. test_command_structure stays green via file-rename + `<component name>` retoken; test_workflow_gates_reference_commands asserts only brainstorm/plan/implement/test (unchanged).

## Outcome (2026-06-27 — applied)

All 32 edits applied across 16 files via the main loop (anchors re-validated against `src/` before each edit). The `/sc:workflow` command renamed to `/sc:roadmap` (`git mv` + 8 cross-file token refs + 2 bare-id dispatcher refs).

Tests: structural suite 1577 passed / 3 skipped; full unit suite **1995 passed / 3 skipped / 0 failed** (665s). No regressions. Repo-wide grep confirms zero remaining `/sc:workflow` command references (doc-type `-workflow` artifact vocabulary intentionally retained).

Open items the research flagged that content edits cannot close (carried forward, not regressions): SC ships no fan-out runtime (all integrated behavior is model-followed prose); resume-from-cache staleness + `parallel()` silent-null-drop are harness runtime behaviors the rules can only warn against; harness task-state survival across the subagent boundary is unverified (task.md hedges); the `min(16, cpu-2)` cap is hardware-derived; the `roadmap` verb vs `-workflow` artifact-suffix mismatch is permanent by design.
