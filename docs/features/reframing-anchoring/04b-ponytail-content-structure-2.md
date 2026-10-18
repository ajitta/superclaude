# 04b — Ponytail lean criteria applied to the content structure (ADAPTATION) — part 2 of 2

> Continuation of [part 1](./04b-ponytail-content-structure-1.md) (split by size; content unchanged).

## 2. Answers to the six questions (continued)

### (5) Gotchas and bounds repeated across files

Exact-sentence scan (≥60 chars, XML stripped) found **15,827 redundant bytes** in verbatim copies; the paraphrased families below add more.

| Sentence (verbatim or near) | Copies | Files | Bytes |
|---|---|---|---|
| "As a delegated subagent Claude cannot ask mid-task: wherever this file says to ask the user or get the user's confirmation, it stops before that step and returns the proposed action and the question in its report. The task text counts as confirmation only for a reversible action it names with its target; a destructive or irreversible one needs the user's own approval quoted in the task." | 24 | every agent `<tool_guidance>` Ask First | 389 × 24 = **9,336** |
| "MEMORY.md = prior lessons; verify against current state before acting on them. After task: save a lesson only if a future run would act differently, in the file layout Claude Code's memory instructions give." | 24 | every agent `<memory_guide>` | 209 × 24 = **5,016** |
| "Symbolic-First: with a symbol-aware tool connected (LSP or code index), query overview → definition → references before whole-file Read" / "…prefer symbol-aware queries (when connected) or targeted Grep over whole-file Read…" | 19 (+ explain.md symbolic-first gotcha, + MODE_Orchestration priorities, + select-tool matrix row) | 11 + 4 + 2 agents in three wordings | ~2,900 |
| ≥2-independent-sources / single-source rule | 8 | see Q2 Research | ~1,800 |
| "slug resolution (zero-match default `[f]`), frontmatter, README update per core/rules/RULES_DOCS.md `<doc_output_convention>`" | 7 | analyze, brainstorm, design, plan, research, roadmap, intent | ~900 |
| "Coverage beats filtering: Claude reports every finding, including low-severity…" + "Each finding carries `severity: … confidence: …`" + "When the user explicitly limits the scope…" (the whole `<finding_policy>` block) | 3 | quality-engineer, security-engineer, self-review | ~1,400 |
| evidence-fabrication: "Do not construct hypothetical failure scenarios to justify a pre-existing recommendation. Evidence (code, config, measurements) must precede proposals." | 3 | analyze, brainstorm, troubleshoot gotchas | ~480 |
| analysis-loop: "If reasoning reaches the same conclusion twice on the same question, end that line…" | 4 | analyze, brainstorm, troubleshoot, spec-panel (iteration-escalation cites it) | ~500 |
| workflow-fanout / Write-Return: "fan-out subagents RETURN … — subprocess writes discarded; main loop performs the Write" | 5 | design, plan, implement gotchas; task gotcha (workflow-task-state); MODE_Orchestration; RULES_DELEGATION (the declared "full rule") | ~1,100 |
| ">3 files → numbered plan → wait for approval" | 9 | RULES_QUALITY ×3, RULES_INTERACTION, RULES_DELEGATION, PRINCIPLES, FLAGS, implement ×2, task ×2 | ~900 |
| "Apply [R18 Necessity Test] …" | 6 files | RULES, RULES_QUALITY, RULES_DOCS, design, improve, spec-panel | ~400 |
| "Revert to default behavior when this mode was loaded by a keyword match … or by a flag or keyword that appeared only in quoted, pasted or code text …" | 7 | every mode `<fallback>` | 1,590 |
| "…unrelated to the global --focus / --scope / --safe-mode / --validate / --plan" | 9 | cleanup, business-panel, auto-improve, reflect, improve, review, implement, spec-panel | ~600 |
| `--strategy systematic\|agile\|enterprise: systematic works through every requirement area in order; agile splits…; enterprise adds compliance…` | 2 | brainstorm, roadmap (identical) | 290 |
| existing-check / existing-plan / existing-spec / check-existing / already-done ("check if X already exists before creating") | 5 | design, plan, spec-panel, init, task | ~350 |
| stale-list / phantom-command ("command list may go stale; verify against commands/sc/") | 3 | help ×1, sc ×2 | ~250 |
| "new-commit: never amend unless asked" | 2 | git.md, git-workflow.md | 160 |
| never-bare-python | 2 | insight, auto-improve | ~600 |
| lens-not-impersonation | 2 (+ MODE never) | business-panel-experts, spec-panel | ~350 |
| intent-confirm / scope-anchoring | 3 each | project-manager, root-cause-analyst, business-panel-experts | ~500 |

### (6) XML sections that carry no instruction

| Section | Where | Why it carries nothing |
|---|---|---|
| `<role command="/sc:x"><mission>…</mission></role>` | all 36 commands (5,412 B) | The mission is the first clause of the frontmatter `description` (analyze: description "Code analysis across quality, security, performance, architecture domains, with severity-rated findings…" / mission "Code analysis across quality, security, performance, architecture domains"; help: identical strings; 34 of 36 are prefix-copies). The `command=` attribute restates the filename. |
| `<bounds><does>` in commands | 36 (part of 10,318 B) | Restates the mission/flow as a noun list: explain `<does>clear explanations, agent expertise, framework integration.</does>`; design `<does>comprehensive specs, multi-format output, validation.</does>`; sc `<does>command dispatch, feature routing, context-aware help.</does>`; pm `<does>orchestration, auto-delegation, self-documenting.</does>`. |
| `<bounds><never>` tautologies | ~20 commands | explain `<never>explains without analysis, overrides standards, or reveals sensitive information.</never>`; index `<never>override manual docs, generate without analysis, bypass standards.</never>`; roadmap `<never>… generates without analysis</never>`; estimate `<never>… estimates without analysis</never>`; pm `<never>bypasses documentation.</never>`. "X without analysis" is the flow's step 1; "overrides standards" is the RULES kernel's project_rules_priority. The `<never>` lines that **do** carry a rule (build: "modifies build config, installs dependencies, deploys"; cleanup: "deletes files only after the user confirms the listed paths"; test: "generates test cases outside an explicit --tdd request") are the ones to keep. |
| `<memory case_based="true" pattern_learning="true" cross_session="true"/>` | RESEARCH_CONFIG | empty element, attributes name no action. |
| `<checklist>` items that restate `<actions>` | agents, 8,447 B | business-panel-experts action 3 "Run each lens's questions, collect insights and list assumptions" ↔ checklist "2-3 relevant lenses applied"; socratic-mentor action 4 "Reveal the concept name only after the learner articulates the idea" ↔ checklist "Principle named only after the learner articulates the idea". ~half of checklist lines are the actions list in past tense. |
| `<meta>` | sc.md | "version: 4.27.2 (SSOT: pyproject.toml — answer version queries via `superclaude --version`)" — tells the reader not to use the value it carries. |
| `<startup>` Report / Remind lines | agent.md | "Report: Core services: deep research, repo index" and "Remind: 💡 Use /context to confirm token budget" — status-line text, no decision. |
| `<description>` sub-elements | git.md `<pr_status_integration>`, task.md `<task_cleanup>` | "PR review status indicator", "Task cleanup via TaskUpdate delete" — a title repeated as an element. |
| `<tools>` lists of native tools | 25 commands | "Read: examine file content and context", "Grep: search patterns across changed files", "Bash: run git and gh commands" — names tools Claude Code already exposes with their own descriptions; only the `Agent:` lines (review, test, implement) carry an instruction. |

---

## 3. Findings

### Must fix

**1. RULES module trio overruns the budget by 72 tokens and the skipped module is marked loaded** (core/rules/RULES_QUALITY.md, RULES_DELEGATION.md, RULES_DOCS.md; scripts/context_loader.py)
- What this is: the three P1 rule modules sum to 8,072 estimated tokens against an 8,000 budget.
- Problem: `/sc:analyze --delegate` (QUALITY via `/sc:analyze`, DELEGATION via `--delegate`, DOCS via `/sc:analyze`) on a fresh session drops RULES_DOCS with a `⚠️ Budget exceeded` comment, and `check_triggers()` has already written it to the dedup cache, so no later prompt re-injects it. analyze.md step 5 then writes the report path from memory.
- Fix: cut ≥300 chars from RULES_QUALITY (the `>3 files` rule is stated three times inside it, lines 12, 13, 32) **or** move `mark_as_loaded` after the budget pass. Both are small.
- If we skip it: every delegated analysis/implement that also produces a doc runs without the doc convention for the whole session.

**2. git-workflow agent and /sc:git are one feature written twice** (agents/git-workflow.md, commands/git.md)
- What this is: same `gh pr view --json state,reviewDecision,isDraft`, same four PR states, same `--from-pr` procedure, same new-commit gotcha. The agent is named by no file in the tree; the command's description says to run git in the main session; the agent's says the same ("Not for one routine commit — the main session commits directly").
- Problem: must change together (a PR state or `gh` flag change hits both), never co-loaded. Two of the agent's gotchas (staged-secret-scan, default-branch-warn) are real rules that the command — the path actually taken — does not carry.
- Fix: delete git-workflow.md; move staged-secret-scan and default-branch-warn into git.md `<gotchas>` (~400 B).
- If we skip it: the secret-scan rule stays on the path nobody routes to. −5,800 B.

**3. /sc:sc duplicates Claude Code's own slash dispatch and the help list** (commands/sc.md)
- What this is: a command whose flow is "invoke the matching /sc:<name> command via the Skill tool", with a 36-entry catalogue copied from help.md and a `<meta>` block that disclaims its own version number.
- Problem: `/sc:[command]` is the native invocation; the unknown-name suggestion is already produced by the loader's `resolve_command_name()`; the catalogue is a second stale-list (its own gotcha says so).
- Fix: delete sc.md. help.md keeps the one list.
- If we skip it: three copies of the command catalogue (sc, help, recommend) to update on every command add. −3,799 B.

**4. The delegated-subagent paragraph is pasted into all 24 agents** (agents/*.md `<tool_guidance>`)
- What this is: 389 characters × 24 = 9,336 B of the identical sentence "As a delegated subagent Claude cannot ask mid-task …".
- Problem: a rule about how *any* subagent returns a question lives in every leaf instead of the one place the caller already assembles — RULES_DELEGATION `<delegate_packet>`, whose `active_mode_directives` field exists precisely because "sub-agents never receive context_loader injections, so … context that must govern the sub-agent travels only if copied".
- Fix: add one `return_rule` line to `<delegate_packet>` (the caller sends it); in each agent keep only the per-agent Ask-First list. Verifier/self-review that run under `claude --agent` as main session are unaffected (the sentence is conditional on delegation anyway).
- If we skip it: a wording fix is a 24-file edit; the sentence also lands in every `claude --agent X` main-session prompt where it does not apply. −8,900 B.

**5. Research domain states its one rule eight times and ships a config file nothing loads** (modes/RESEARCH_CONFIG.md, modes/MODE_DeepResearch.md, agents/deep-researcher.md, commands/research.md)
- What this is: the ≥2-sources/single-source rule in 8 places (4 inside deep-researcher alone); credibility tiers, hop patterns, depth profiles and tool routing each in 2–3; RESEARCH_CONFIG never injected and never Read by a flow step (cited only in two `note=` attributes).
- Problem: four copies of a threshold that must change together; the file that holds the "full profiles" is the one not in context.
- Fix: delete RESEARCH_CONFIG; move its only unique rows (sources/hops/iter numbers, `<errors>`) into deep-researcher `<depth_behavior>`/`<tools>` (~500 B); in deep-researcher keep the rule once in `<evidence>` and reference it from focus/actions/checklist; drop the mode's Replan restatement.
- If we skip it: the next edit to the single-source exception is an 8-site change. −4,600 B.

### Should fix

**6. MODE_Orchestration restates FLAGS `<mcp>` and RULES_DELEGATION `<workflow_delegation>`** (modes/MODE_Orchestration.md)
- What this is: `<behaviors>` Tool-Task Matching points at FLAGS.md (always loaded) for "full routing"; `<fan_out_execution>` (1,700 B) repeats Write-Return / Schema-vs-Evidence / Cap-Aware / Packet-Prompt from RULES_DELEGATION, which the same prompts (`--delegate`, "sub-agent", `/sc:pm|agent|task`) already inject. Trigger `tool.?select` fires on ordinary English; `--orchestrate` is typed by no command.
- Fix: delete the mode; move its two bullets not in RULES_DELEGATION (Pipeline-Default, Context-Carry) there (~350 B); keep select-tool.md as the one tool-routing surface.
- If we skip it: three copies of tool routing (FLAGS, mode, select-tool matrix) plus RESEARCH_CONFIG's fourth. −3,800 B.

**7. mcp/ doc bodies load only under `--verbose-context`** (mcp/MCP_Playwright.md, MCP_Chrome-DevTools.md, MCP_Tavily.md)
- What this is: Playwright and Chrome-DevTools are Tier 0 (one-line `TIER_0_MAP` hint), Tavily is Tier 1 (the `INSTRUCTION_MAP` string); the .md bodies (10,703 B) are read only when `--verbose-context` is typed or `CLAUDE_CONTEXT_USE_INSTRUCTIONS=0`. No command, agent or rule references any of the three files (rg: only mcp/README.md).
- Fix: shrink each file to its hint/instruction string plus the one section README says is the long form (`<cli_vs_mcp>` for Playwright); the loader's "backing file not installed" check then still works.
- If we skip it: 10.7 KB of tool docs that drift unseen because they are never in context. −8,000 B.

**8. Keyword triggers that cannot fire or fire across domains** (scripts/context_loader.py TRIGGER_MAP)
- What this is: `vs-(cot|multi|standard)`, `business.?symbol|strategic.?symbol|business.?example|panel.?example`, `analyze reasoning` are documented nowhere (Q1); `multi.?expert` loads the business mode for spec-panel's own wording; `check_triggers()` ignores `scannable_prompt()`, which seven mode `<fallback>` sentences (1,590 B) compensate for in prose.
- Fix: delete the undocumented alternatives and `multi.?expert`; pass `scannable_prompt(trigger_prompt)` to `check_triggers()`; delete the seven fallback sentences.
- If we skip it: "multi-expert spec critique" keeps loading Porter and Christensen. −1,600 B content.

**9. Agent `<memory_guide>` header is CC-native behaviour pasted 24 times** (agents/*.md)
- What this is: "MEMORY.md = prior lessons; verify against current state … After task: save a lesson only if a future run would act differently, in the file layout Claude Code's memory instructions give." 209 × 24 = 5,016 B. Every agent declares `memory: project`, the Claude Code feature whose own instructions the sentence defers to ("in the file layout Claude Code's memory instructions give").
- Fix: keep the per-agent category bullets, drop the two header lines. (Not verified against Claude Code docs here — isolation rule; the sentence's own wording is the evidence that the native instructions exist.)
- If we skip it: nothing breaks; 5 KB of restated native behaviour. −5,000 B.

**10. Business roster and mode-routing in four files** (modes/MODE_Business_Panel.md, core/BUSINESS_SYMBOLS.md, commands/business-panel.md)
- What this is: Q2 Business table — the nine experts and the Discussion/Debate/Socratic routing in mode, agent, command and BUSINESS_SYMBOLS; the command already names the agent `<focus>` as SSOT.
- Fix: delete the mode's `<experts>` table and BUSINESS_SYMBOLS `<expert_selection>`/`<config_defaults>` (the mode's `<domain_routing>` already carries domain→experts); keep the agent as SSOT.
- If we skip it: adding an expert is a 4-file edit. −1,300 B.

**11. /sc:init and project-initializer carry the same task list without routing to each other** (commands/init.md, agents/project-initializer.md)
- What this is: the command's `<menu>` a–i and the agent's `<tasks>`/`<execution_plan>`/`<task_details>` (3,721 B) describe the same tasks and dependency graph; init.md never names the agent; only repo-index.md's `Not for` does.
- Fix: either init.md step 5 dispatches the agent (then the agent is the task SSOT and the command's `<task_outputs>`/`<dependency_graph>` go), or the agent's three task sections go and it keeps the per-task idempotency rules the command lacks. Smallest: the second.
- If we skip it: the menu gains task [i] (docs scaffold) that the agent's list does not know. −3,000 B.

**12. project-manager writes to a memory store nothing else reads** (agents/project-manager.md)
- What this is: `docs/memory/patterns/` and `docs/memory/mistakes/` appear in one file in the tree. /sc:save, /sc:load, /sc:insight, /sc:reflect and the RULES kernel use `.claude/memories/`, auto memory, `.claude/insights.jsonl`, `.claude/rules/gotchas/`.
- Fix: point the agent's Patterns/Mistakes outputs at `.claude/memories/learnings_<topic>.md` (what /sc:save writes) or `.claude/rules/gotchas/` (what the kernel proposes).
- If we skip it: lessons the agent records are never loaded by /sc:load. 0 B, split fix.

**13. /sc:roadmap writes plan's output path without plan's gate** (commands/roadmap.md, commands/plan.md)
- What this is: both write `docs/features/<slug>/05-plan.md` (roadmap takes `05<letter>-plan-workflow.md` when a plan exists); plan stops on a `status: draft` spec, roadmap does not; roadmap's `--strategy`/`--depth` text is byte-identical to brainstorm's.
- Fix: fold roadmap into plan as `--from <prd>` + `--granularity phase` (lost axes in Q3 table), or add the draft-spec stop to roadmap's Analyze step. Smallest: the latter (+120 B).
- If we skip it: a PRD-derived plan can be written from an unreviewed discovery doc. −2,500 B if folded.

### Nice to have

**14. Command `<role>` wrapper and `<bounds><does>` restate the description** (commands/*.md) — Q6 rows 1–3. Keep `<mission>` text only where it is not a prefix of the description (2 of 36); drop `<does>` lines that are noun lists of the flow; keep the `<never>` lines that carry a rule. −~5,000 B.

**15. MODE_Task_Management is a flag-only mode with a second task hierarchy** (modes/MODE_Task_Management.md) — `--task-manage` appears in no command or agent; FLAGS.md's one line already describes it; task.md carries Epic→Story→Task while the mode carries Plan→Phase→Task→Todo. Delete the mode, or make `/sc:task` trigger it and make the hierarchies agree. −2,388 B.

**16. MODE_Brainstorming is not loaded by /sc:brainstorm** (modes/MODE_Brainstorming.md, scripts/context_loader.py) — trigger is `--brainstorm|--bs` only, unlike research/business-panel/select-tool whose commands trigger their modes. Either add `/sc:brainstorm` to the trigger, or accept that brainstorm.md step 1 and its `<never>` already restate the mode and leave it flag-only. 0 B, consistency.

**17. Three copies of the `<finding_policy>` block** (agents/quality-engineer.md, security-engineer.md, self-review.md) — identical 3-sentence policy; belongs in RULES_QUALITY (already injected on `/sc:review|analyze|test`). −900 B.

**18. agent.md `<startup>`/`<token_discipline>`** (commands/agent.md) — status-line persona text ("Remind: 💡 Use /context"); `<token_discipline>` restates `--uc`. −700 B.

**19. `<tools>` sections naming native tools** (25 commands) — "Read: examine file content"; keep only the `Agent:` lines that say *which* agent and *what packet*. −~2,500 B.

**20. Commands' `<examples>` tables with one-word outputs** (e.g. business-panel: "`market-analysis.md --mode discussion --focus strategy` → Collaborative expert analysis"; sc.md: "`/sc:recommend` → Get suggestions") — 23,452 B across commands, of which the error-path `<example>` blocks carry the only decision content. Not measured line by line; flagged for 03e/03f cross-check.

---

## Verdict

The content tree is not bloated by many weak files; it is bloated by the same rule written into every file that might need it, because the delivery system co-loads almost nothing (command + rule module + sometimes mode) and the authors compensated by copying. The two declared trinities are real on the mindset/workflow axis but carry their domain tables 4–8 times; two undeclared pairs (git, init) are the same feature in two directories with no route between them; one command (`/sc:sc`) re-implements Claude Code's own dispatch. The loader has three undocumented trigger alternatives, one cross-domain misfire (`multi.?expert`), and a 72-token overrun that silently drops RULES_DOCS for the session.

**Lean: -52,000 bytes (~8 files) possible.** (sc.md, git-workflow.md, MODE_Orchestration.md, RESEARCH_CONFIG.md, MODE_Task_Management.md, and the three mcp/ bodies shrunk to their hints; the rest is section-level cuts across agents and commands. Of the 52 KB, ~14 KB is in-context bytes per delegated agent call — the two pasted paragraphs — and ~12 KB is the RULES/mode injection path; the remainder is on-disk only.)

## Not checked

- `skills/sc-author` and `skills/sc-prompt` bodies beyond the duplicate-sentence scan (3 verbatim shared sentences found, all source-citation lines) — user-invoked, out of the routing graph.
- `output-styles/`, `templates/docs-scaffold/` (4.8 KB, referenced by init task [i]).
- Whether Claude Code's agent-memory feature injects the instructions that finding 9 assumes (isolation rule: no docs lookup).
- Whether the `Workflow` tool, `EnterWorktree`, `SendMessage` named in MODE_Orchestration and RULES_DELEGATION exist in the current harness — if not, `<fan_out_execution>` and `<workflow_delegation>` are dead on arrival, which would move finding 6 to Must fix.
- `agents/README.md` (9,973 B), `commands/README.md`, `modes/README.md`, `core/README.md`, `mcp/README.md` — not installed; excluded from the lean count.
- Line-by-line quality of `<examples>` tables (finding 20) and of `<checklist>` vs `<actions>` overlap beyond the two quoted agents.
- Tests under `tests/unit/` that pin section presence (`test_command_structure.py`, `test_agent_structure.py`, `TestCoreLiteSplit`): several cuts above (role/bounds/tools sections, mode deletion, trigger removal) will need the corresponding structural test relaxed; not inspected.
