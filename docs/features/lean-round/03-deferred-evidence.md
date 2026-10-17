---
feature: lean-round
phase: analysis
owner: ajitta
created: 2026-10-18
updated: 2026-10-18
---

# 03. Deferred items — evidence for a later decision

Scope: the six deletion/shrink candidates the owner deferred (plus one budget item found during B4, §7) in `00-intent.md:45-49` (Q3, Q5, Q6, Q7). This file records what exists today, with `path:line`, so a later round can decide. It carries no proposal. Line numbers come from commit `5f7c205e` (branch `fix/lean-round-2`); for files dirty in the working tree at the time of writing (`src/superclaude/scripts/context_loader.py`, `src/superclaude/cli/main.py`, `tests/unit/test_context_loader.py`) the numbers are from `git show HEAD:<path>`.

## 1. `commands/sc.md` (dispatcher, 3,799 B)

| Dependency | Evidence | What a deletion touches |
|---|---|---|
| Version test | `tests/unit/test_version_consistency.py:42` defines `_SC_DISPATCHER`; `:184-190` `test_sc_dispatcher_version_matches_pyproject` reads it and asserts the pyproject version string is present (`sc.md:74` carries `version: 4.28.0`) | Test errors on a missing file; the test and the `<meta>` bump step go together |
| Catalog test | `test_version_consistency.py:316-323` `test_dispatcher_lists_every_command` is parametrized over `[_SC_DISPATCHER, _HELP]` and asserts each `<commands>` block has exactly `_command_file_count()` entries (`:65-67`: every `commands/*.md` except README) | The `sc` id errors; the `help` id fails until `help.md:46` (`- sc: command dispatcher (main entry)`) is removed, because the file count drops to 35 while help lists 36 |
| Count tests | `_README_COUNT_PATTERNS` `:219-228` and `test_readme_badge_table_matches_source` `:264-269` pin README counts to the tree; README states 36 at `README.md:27`, `:32`, `:83`, `:120`, `:570` | All five become 35 |
| README roster | `test_readme_lists_every_command_and_no_phantoms` `:272-288` compares the "All Commands" section to the file set; `README.md:713` lists `/sc:sc` | Row removal, else "phantom" failure |
| Inventory | `src/superclaude/commands/README.md:15` row `/sc:sc` | Manual row removal |
| Version-bump checklist | No repo file lists `sc.md` as a bump step: `rg sc.md` over `Makefile`, `AGENTS.md`, `CLAUDE.md`, `.claude/rules/` returns nothing; `AGENTS.md:46` says only "version-bump branch merged and green on master". The step exists in prior plans (`docs/features/plugin-install/05a-plan-release-channel.md:31,120`, `05-plan.md:235`) and in the test above | The test is the only enforced checklist item |
| Help/recommend catalog | `help.md:46` lists `sc`; `help.md:90` hands off to `/sc:recommend`, not to `sc`; `recommend.md` (`:26-42`) maps keywords to commands and never names `sc`; `sc.md:88` hands off to `/sc:recommend /sc:help` | One line in help.md; nothing in recommend.md |
| CLI / loader | `rg -n "sc\.md|\bsc\b" src/superclaude/cli/` matches only the `commands/sc` directory name (`install_paths.py:23,30`, `install_inventory.py:59,349`, `main.py:105,282`) and `CLAUDE_SC.md` (`main.py:558-560`); `context_loader.py:469` likewise names the directory. No Python reads the dispatcher file | Nothing in code |
| Content overlap | `sc.md:18-55` `<commands>` = 1,900 B / 36 entries; `help.md` `<commands>` = 1,924 B / 36 entries (measured 2026-10-18); `sc.md:13` flow step 2 "invoke the matching /sc:<name> command via the Skill tool"; `sc.md:10` syntax `/sc:[command]`; `sc.md:2` description says "On request only — the user's /sc:sc or a workflow step that names it" | — |
| Workflow steps naming it | `rg -n "sc:sc" src/superclaude` finds only `commands/README.md:15` and `sc.md:2,6` | No command or agent routes through `/sc:sc` |

Routing use of `/sc` (bare) has not been measured: no transcript count, eval arm or hook log in the repo records how often a user types `/sc:sc` or `/sc` without a subcommand. The decision deferred at `00-intent.md:45` waits on that measurement.

## 2. `modes/MODE_Orchestration.md` (4,196 B) and `modes/MODE_Task_Management.md` (2,388 B)

| Dependency | Evidence |
|---|---|
| Loader triggers | `context_loader.py:146` `(r"(--task-manage)", "modes/MODE_Task_Management.md", 2)`; `:152` `(r"(--orchestrate|tool.?select|/sc:select-tool)", "modes/MODE_Orchestration.md", 2)`. Modes are always Tier 2 = full `.md` injection (`:714-731` `_get_injection_tier`, `modes/` branch at `:723-724`) |
| Flag roster | `context_loader.py:337-338` list `task-manage` and `orchestrate` in `VALID_FLAGS` (fuzzy-match roster; `tests/unit/test_command_structure.py:14,336` uses `VALID_FLAGS` to exempt global flags from per-command `<flags>` declaration) |
| FLAGS.md rows | `src/superclaude/core/FLAGS.md:12` `--task-manage: >3 steps, >2 dirs, >3 files → hierarchical task tracking…`; `:13` `--orchestrate: multi-tool, perf constraints, parallel → tool matrix opt`; `:7` names both modes in the "Read it from modes/ after compaction" list |
| Structure tests | `tests/unit/test_mode_structure.py:18` globs `MODE_*.md`; no pin by name — a removed file removes its parametrized cases. `tests/unit/test_content_usage.py:42-60` requires every `MODE_*.md` to appear in `TRIGGER_MAP`; `:92-110` requires every `TRIGGER_MAP` path to exist. Deleting a file without its `TRIGGER_MAP` entry fails the second; deleting both passes both |
| Count tests | README "8 modes" at `README.md:27`, `:32`, `:407` and the modes rows in `_README_COUNT_PATTERNS` (`test_version_consistency.py:224-225`) and the badge test (`:264-269`) |
| Inventories | `src/superclaude/modes/README.md:19-20` rows; `README.md:411`, `:413` bullets; `.claude/rules/mode-authoring.md:85` uses `MODE_Task_Management.md` as the naming example |
| Cross-references | `rg -n "MODE_Orchestration|MODE_Task_Management|--orchestrate|--task-manage" src/superclaude` (excluding the loader) matches only `core/FLAGS.md:7,12,13`, `modes/README.md:19-20`, and the two files' own `<fallback>` lines (`MODE_Orchestration.md:45`, `MODE_Task_Management.md:33`). No command, agent or `<handoff>` names either mode or flag; `commands/select-tool.md` does not mention the mode (its trigger reaches the mode only through the loader regex at `:152`) |
| Handoffs out | `MODE_Orchestration.md:48` → `/sc:task /sc:select-tool /sc:implement`; `MODE_Task_Management.md:36` → `/sc:task /sc:save /sc:reflect` |
| Eval coverage | `rg` over `evals/` for `task-manage`, `--orchestrate`, either filename: no match |

No measurement in the repo shows that "the model already does this" for either mode: no eval arm, canary gate or transcript comparison runs a prompt with and without the mode text. `00-intent.md:47` records the owner's instruction not to infer redundancy without measurement.

## 3. `mcp/MCP_*.md` body shrink and `modes/RESEARCH_CONFIG.md` deletion

### 3a. Manual-load references to RESEARCH_CONFIG (current tree)

`rg -n "RESEARCH_CONFIG" .` excluding `.hermes/`, `docs/features/reframing-anchoring/`, `docs/features/lean-round/`, run 2026-10-18. Prior-audit citations checked one by one:

| Prior citation | Current | Text |
|---|---|---|
| `ARCHITECTURE.md:47` | confirmed `src/superclaude/ARCHITECTURE.md:47` | "not auto-injected by context_loader.py; it ships with modes/ as reference material accessed via cross-refs from commands/research.md and the research mode body" |
| `modes/README.md:30` | confirmed `:30`; also `:28` (table row, `type=config`) | "never injected by context_loader.py; /sc:research points to its installed copy" |
| `commands/research.md:25,38` | confirmed `:25` (`<depth note="Full profiles and thresholds: .claude/superclaude/modes/RESEARCH_CONFIG.md …">`), `:38` (`<tools note="Routing: tool_routing in the RESEARCH_CONFIG.md named in the depth note">`) | path given, model must Read it |
| `MODE_DeepResearch.md:3` | confirmed `src/superclaude/modes/MODE_DeepResearch.md:3` | "depth profiles and tool routing for /sc:research are in the installed .claude/superclaude/modes/RESEARCH_CONFIG.md" |
| `README.md:548` | confirmed `README.md:548` | "Profiles are defined in modes/RESEARCH_CONFIG.md" (link) |
| — (not in prior list) | `CHANGELOG.md:205-206` (history), `tests/unit/test_mode_structure.py:17` (comment: excluded from the mode glob), `docs/features/sonnet-5-5-prompting/04-design.md:106`, `docs/features/command-local-flags/05-plan.md:151` (plan, `RESEARCH_CONFIG.md:7,21` cited for `--strategy` values), `docs/features/prompt-content-audit/*` and `docs/archive/*` (history) | — |

`agents/deep-researcher.md` no longer names the file (the prompt-content audit removed the path-less reference, `docs/features/prompt-content-audit/03c-analysis-agents-first.md:34`). The loader never lists it: `rg RESEARCH_CONFIG src/superclaude/scripts/context_loader.py` → none. No test reads it.

### 3b. What the loader needs from `mcp/MCP_*.md`

| Mechanism | Evidence | Requirement on the file |
|---|---|---|
| Trigger entries | `context_loader.py:111-125`: Tavily P1 (`tavily|fact.?check|/sc:research|--tavily`), Playwright P2, Chrome-DevTools P2. `COMPOSITE_FLAGS` `:192-201`: `--frontend-verify` → Playwright + DevTools, `--all-mcp` → all three | Path must exist in source: `tests/unit/test_content_usage.py:92-110`; every `MCP_*.md` must be mapped: `:65-87`; exactly 3 mcp paths: `tests/unit/test_context_loader.py:309-314` |
| Tier 0 hint (Playwright, DevTools) | `TIER_0_MAP` `:229-233`; emitted at `:772-783` as `<sc-context-hint src=…>`; the body is NOT read. `:774-777`: "skip hint if backing file is missing" — `(BASE_PATH / context_file).exists()` is the only check | File must exist at the install path; content irrelevant at Tier 0 |
| Tier 1 instruction (Tavily) | `INSTRUCTION_MAP` `:210-224` is an in-code string; emitted at `:787-796` as `<sc-context src=…>` with no existence check | Body not read; no existence check |
| Tier 2 full `.md` | `_get_injection_tier` `:714-731`: `--verbose-context` or `CLAUDE_CONTEXT_USE_INSTRUCTIONS=0` → tier 2 for every file; `:799-823` reads the file (`:800-806`, silently skipped if missing) and prints `<context-inject file=… tokens=~N>` under the 8,000-token budget (`:45-47`) | Only here is the body in context |
| `--verbose-context` | `:750-758` prints the "forcing full .md injection … 5-10x token inflation" comment; `tests/unit/test_context_loader.py:195-197` pins tier 2 for `MCP_Playwright.md` and `MCP_Tavily.md` under verbose | — |
| `check_mcp_fallbacks` | `:684-711` derives the server name from the path string (`mcp/MCP_Tavily.md` → `tavily`) and calls `check_mcp_and_notify`; `tests/unit/test_mcp_fallback.py:82-94`, `:207-216` pin `MCP_FALLBACKS` ↔ `CURRENT_MCP_SERVERS`; `tests/unit/test_context_loader.py:765-789` pin that removed servers (Context7, Serena) have no doc, hint, map entry or fallback | Name only; body not read |
| CLI explain | `main.py:761` `_CTX_HINT_RE` parses `<sc-context-hint>` lines; `tests/unit/test_cli_context.py:138,151` expect `mcp/MCP_Tavily.md` in `superclaude context explain` output | Path string only |
| Structure tests | `tests/unit/test_content_structure.py:22` globs `MCP_*.md`; `:104-141` require `<component type="mcp">`, `<role>`, non-empty `<mission>`, `<bounds>` with `<does>`/`<never>` and no `<should>`/`<avoid>` | Minimum body shape |
| Authoring rule | `.claude/rules/mcp-authoring.md:79` required tags `<role>` (with `<mission>`), `<choose>`, `<bounds>`, `<handoff>`; `:89` "No `<role>` body beyond `<mission>`"; `:112` "Drop tool inventories, role descriptions, version/install blocks" | Rule, not test |
| Roster | `tests/integration/test_cross_directory_refs.py:76-83` `EXPECTED_MCP_DOCS` = Playwright, Tavily, Chrome-DevTools; `tests/unit/test_codex_component_map.py:79,103` count `MCP_*.md` | File set pinned, not size |

Sections on disk vs injected (sizes 2026-10-18): `MCP_Chrome-DevTools.md` 3,214 B (`<role>` :2, `<choose>` :6, `<cwv_thresholds>` :11, `<integration_patterns>` :22, `<examples>` :29, `<bounds>` :38, `<handoff>` :44); `MCP_Playwright.md` 4,759 B (`<role>` :2, `<cli_vs_mcp>` :6, `<capability_system>` :10, `<choose>` :23, `<network_mocking_patterns>` :28, `<integration_patterns>` :37, `<examples>` :45, `<bounds>` :56, `<handoff>` :62); `MCP_Tavily.md` 2,730 B (`<role>` :2, `<choose>` :6, `<search_patterns>` :11, `<integration_patterns>` :21, `<examples>` :27, `<bounds>` :35, `<handoff>` :41). In the default tier path none of these sections is injected: DevTools and Playwright reach the prompt as the one-line hints at `context_loader.py:230-231`, Tavily as the `INSTRUCTION_MAP` string at `:211-224`. The full bodies are read only under `--verbose-context` / `CLAUDE_CONTEXT_USE_INSTRUCTIONS=0` or when the model Reads the file itself.

## 4. `<finding_policy>` blocks (3 copies)

| Item | Evidence |
|---|---|
| Copies | `agents/self-review.md:36-38`, `agents/security-engineer.md:37-39`, `agents/quality-engineer.md:37-39`; identical text, 602 B inner / 641 B with tags each (measured 2026-10-18) |
| Text | "Coverage beats filtering: Claude reports every finding, including low-severity and low-confidence ones, and does not pre-filter under general guidance like "focus on real issues" or "don't nitpick" … Each finding carries `severity: {critical|high|medium|low|nit}` and `confidence: {high|medium|low}` … Recall is the job at this stage; precision is a later stage's job." |
| Other copies | `rg -i "coverage beats filtering"` over `src/superclaude` and `.claude/rules`: only the three agents. No test pins the tag (`rg finding_policy tests/` → none) |
| What reaches an agent | `.claude/rules/agent-authoring.md:12`: a subagent session gets the agent's markdown body as its system prompt; it does not get the parent's system prompt or skills; whether it gets CLAUDE.md depends on Claude Code and `omitClaudeMd`; "the on-demand rule modules never reach it". `tests/unit/test_agent_structure.py:251-256` encodes the same premise (R-IDs "never reach a subagent") |
| Loader side | `core/rules/RULES_DELEGATION.md:32`: "sub-agents never receive context_loader/UserPromptSubmit injections, so mode context that must govern the sub-agent travels only if copied". `src/superclaude/hooks/hooks.json` registers `SessionStart` (:3), `PreCompact` (:41), `SessionEnd` (:53), `UserPromptSubmit` (:65), `PreToolUse` (:77), `PostToolUse` (:112), `Stop` (:143) — no `SubagentStart`, so no hook appends text to a sub-agent prompt |
| `delegate_packet` | Defined at `RULES_DELEGATION.md:29-41`; summarized in `core/RULES.md:10` and routed at `RULES.md:44` ("spawning sub-agents, --delegate, orchestration"). Its fields (`:30-32`) are user_request_verbatim, allowed_scope, forbidden_changes, files_or_areas_of_interest, stop_condition, required_evidence_format, active_mode_directives. No field carries a finding policy. The module itself is injected only when the prompt matches `context_loader.py:173` (`--delegate|--concurrency|/sc:(pm|agent|task)|sub.?agent|worktree`) |
| Native auto-delegation | `agents/README.md:7`: Claude Code delegates when a request matches the agent's `description`. In that path the Agent-tool prompt is whatever the main model writes; the packet rule applies only if `RULES_DELEGATION.md` is in the main context at that moment |

Proven by file inspection: the three copies are the only text that carries the policy into those agents' system prompts; no code path, hook or packet field copies it from a parent. Not proven: whether a main loop that has `RULES_DELEGATION.md` in context in practice copies review guidance into an auto-delegated prompt (no transcript or eval measures it), and whether CLAUDE.md-carried text reaches a given sub-agent (depends on `omitClaudeMd`, `agent-authoring.md:12,46`). `00-intent.md:49` keeps the copies until delivery through `delegate_packet` is proven.

## 5. `/sc:init` vs `agents/project-initializer.md`

| Axis | `commands/init.md` (6,923 B) | `agents/project-initializer.md` (9,595 B) | Differs? |
|---|---|---|---|
| Invocation | User slash command; `:2` "On request only — the user's /sc:init or a workflow step that names it" | Claude Code auto-delegation by `description` (`:3` "Use when the user asks to set up a repository for Claude Code, or CLAUDE.md and memory scaffolding are missing"), or `claude --agent project-initializer` (`:38`, `:43`) | yes |
| `Not for` pointer | `:2` Not for "set this up" on entering a repo — ask what to set up | `:3` Not for indexing a repo that is already set up — repo-index | yes (different neighbors) |
| Flags / presets | `:10` `[tasks] [--quick] [--full]`; `:21-24` `<flags>`; `:44` `--quick (a,b)`, `--full (a…i)` | none; `:43` "presets, or a custom combination" without named flags | yes |
| Task set | `:34-42` nine tasks a–i, incl. [h] gotchas and [i] docs scaffold; `tests/unit/test_init_docs_scaffold.py:130-165` pin task [i] in menu, dependency_graph, task_outputs, safety_rules, `--full` | `:22-28` seven tasks (no gotchas, no docs scaffold) | yes |
| Flow | `:12-19` Detect → Present → Select → Validate → Execute → Report | `:42-46` Present → Accept → Validate → Execute → Summary (no separate Detect step; detection is in `<task_details>` `:36`) | partly |
| Interactivity | `:15` takes the user's choice; `:123` fallback asks the user | `:43` as a delegated subagent returns the menu with a recommended preset and stops unless the task text names tasks; `:32` dependency question goes in the report | yes |
| Authorization — may write without asking | `:91-96` `<tools>` Write/Edit for CLAUDE.md, PROJECT_INDEX.md, auto memory; `:70-78` `<safety_rules>` | `:60` Proceed: read, scan, analyze git history, generate PROJECT_INDEX.md, write project memory as task details define | overlapping |
| Authorization — Ask-First | `:71` dependency install: show command, require confirmation; `:72` CLAUDE.md edit: show diff before applying; `:73` large test suite warning; `:122` `<never>` installs without confirmation | `:62` Ask First: install deps, modify existing CLAUDE.md, run tests, create files in project root — plus the common subagent sentence (task text counts as confirmation only for a reversible action it names); `:63` Never; `:97` `<never>` | agent adds "create files in project root" and the task-text rule; command has the >500-tests subset offer |
| Memory | `:74-75` write in Claude Code's memory layout, skip when no auto memory folder; `:62,65` tasks d,g write auto memory | frontmatter `:4` `memory: project`; `:38` project memory is the main session's folder, never the agent's own; delegated subagent returns entries in the report; `:74-80` `<memory_guide>` categories | yes (agent distinguishes own vs session memory) |
| `tools` / `disallowedTools` | command file has no tool frontmatter; `:95` names `Agent(repo-index)` for task (a) | no `tools:`/`disallowedTools:` key (`:1-6`): default tool set; `<fallback>` `:98` escalates to system-architect / repo-index by name | yes (command delegates to repo-index; agent cannot spawn, `agent-authoring.md:12`) |
| `<handoff next>` | `:126` `/sc:load /sc:implement /sc:test` | `:101` `/sc:load /sc:implement /sc:index-repo` | third target differs |
| Gotchas | `:117` check-existing | `:90-92` check-existing, make-deploy, uv-not-pip (superclaude-repo specific) | yes |
| Cross-links | neither file names the other: `rg project-initializer src/superclaude/commands` → none; `rg "sc:init" src/superclaude/agents` → none. `agents/README.md:142` routes "repo setup vs indexing" between project-initializer and repo-index | — |

Shared prose: detection markers (`init.md:13` / `project-initializer.md:36`), idempotency and "never overwrite" (`init.md:78,117` / `:22-28,90`), MCP recommendation list, summary table. The axes that differ are invocation, flags, task set (9 vs 7), interactivity under delegation, memory ownership, the Ask-First list, and the handoff's third target.

## 6. Agent common paragraph (delegated-subagent Ask-First sentence)

| Item | Evidence |
|---|---|
| Text (verbatim, 389 B) | `As a delegated subagent Claude cannot ask mid-task: wherever this file says to ask the user or get the user's confirmation, it stops before that step and returns the proposed action and the question in its report. The task text counts as confirmation only for a reversible action it names with its target; a destructive or irreversible one needs the user's own approval quoted in the task.` |
| Carriers | `rg -l "cannot ask mid-task" src/superclaude/agents/` → 24 files, one occurrence each, 389 B each (measured 2026-10-18): backend-architect, business-panel-experts, deep-researcher, devops-architect, frontend-architect, git-workflow, insight-analyst, learning-guide, performance-engineer, project-initializer, project-manager, python-expert, quality-engineer, refactoring-expert, repo-index, requirements-analyst, root-cause-analyst, security-engineer, self-review, simplicity-guide, socratic-mentor, system-architect, technical-writer, verifier. Total 24 × 389 = 9,336 B. Position: tail of the `- Ask First:` line inside `<tool_guidance>` (e.g. `agents/project-initializer.md:62`) |
| Source of truth | `.claude/rules/agent-authoring.md:150` carries the sentence in the `<tool_guidance>` template |
| Test pin | `tests/unit/test_agent_structure.py:63-71` `SUBAGENT_ASK_SENTENCE` holds the full text; `:236-249` `test_ask_first_states_subagent_behavior` extracts `<tool_guidance>`, requires a `- Ask First:` line (`:245-246`) and asserts `SUBAGENT_ASK_SENTENCE in ask_first.group(0)` (`:247-249`). The pin is substring-exact over the whole paragraph: any change to any sentence fails all 24 parametrized cases until `:64-71` is changed in the same commit |
| Pinned sentences | S1: "As a delegated subagent Claude cannot ask mid-task: wherever this file says to ask the user or get the user's confirmation, it stops before that step and returns the proposed action and the question in its report." S2: "The task text counts as confirmation only for a reversible action it names with its target; a destructive or irreversible one needs the user's own approval quoted in the task." |
| Related pins | `test_agent_structure.py:228-233` requires Proceed/Ask First/Never in `<tool_guidance>`; `agent-authoring.md:213` notes the memory protocol header is likewise verbatim-pinned (`test_memory_guide_has_protocol`) |

`00-intent.md:49` and `README.md:19` (lean-round) place the shortening in separate B5 work, "retaining leaf safety semantics and Ask-First checks; no hoisting".

## 7. `RULES_QUALITY.md` size vs the 8K budget on `/sc:analyze --delegate`

| Fact | Evidence |
|---|---|
| Prompt `/sc:analyze --delegate` matches four rule modules | `superclaude context explain "/sc:analyze --delegate"` with `SUPERCLAUDE_PATH=src/superclaude` at `67215cd7`: RULES_QUALITY ~3,245 tokens, RULES_DELEGATION ~2,180, RULES_DOCS ~2,534, RULES_INTERACTION ~282 (P2) |
| Budget | `CLAUDE_CONTEXT_MAX_TOKENS` default 8,000 (`context_loader.py`, `utils.int_env` fallback) |
| Before B4 (`30a08be3`) | injected QUALITY, DELEGATION, INTERACTION (~5,820); dropped RULES_DOCS |
| After B4 | injected QUALITY, DELEGATION, RULES_DOCS (~7,959); dropped RULES_INTERACTION |
| What fitting all four would take | the set is ~8,241 tokens; ~275 tokens (~1,100 characters) would have to leave RULES_QUALITY beyond the duplicate removal already done — i.e. cutting rules, not repeats |
| Mitigation already in place | since 4.28.0 the loader marks a context as loaded only after it is injected, so the dropped file stays eligible on the next prompt that triggers it |

Not measured: whether RULES_INTERACTION's ~280 tokens change behavior on a `--delegate` analysis, or what a larger default budget would cost. Any further cut to RULES_QUALITY is a rule removal and falls under `03-analysis.md` §5 ("no deletion on 'the model already does this' without measurement").

## Not checked

- Whether any user transcript, eval run or hook log records `/sc:sc` or bare `/sc` invocations (item 1) — no such artifact exists in the repo; not measured here.
- Model behavior with and without `MODE_Orchestration.md` / `MODE_Task_Management.md` in context (item 2) — no eval arm exists; not run.
- Whether Claude Code passes CLAUDE.md to auto-delegated sub-agents in the current CLI build, and what `omitClaudeMd` defaults to (item 4) — taken from `agent-authoring.md:12,46`, not re-verified against the Claude Code docs or a live session.
- Whether the main loop in practice copies review guidance into Agent-tool prompts when `RULES_DELEGATION.md` is loaded (item 4) — no transcript inspected.
- Install-path behavior of the Tier 0 backing-file check (`context_loader.py:774`) against a project-scope vs user-scope install — read from code, not executed.
- `src/superclaude/mcp/README.md` (6,770 B) content — not part of the shrink candidates; not read.
- Working-tree edits by concurrent agents to `context_loader.py`, `main.py`, `test_context_loader.py` — ignored by instruction; HEAD line numbers used.
