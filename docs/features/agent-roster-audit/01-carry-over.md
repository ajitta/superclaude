---
feature: agent-roster-audit
phase: implementation
owner: ajitta
created: 2026-10-20
updated: 2026-10-20
---

# 01. Carry-over and changes

Base `f467012c`. Rule from the mode-retire round: before a file goes, check each part of its content that something still depends on, and either show where that content already lives or carry it.

## What each retired agent still held

| Agent | Content something depended on | Where it lives now |
|---|---|---|
| project-manager | Session lifecycle; the only writer of `.claude/memories/pm_context.md`, which `/sc:load` read | `/sc:pm` flow: streams go to `general-purpose`, learnings to `learnings_[topic].md` as `/sc:save --type learnings` writes them. `/sc:load` stops reading `pm_context` (no writer left; an existing file stays on disk). `test_every_key_load_reads_has_a_writer` now checks `save.md`. |
| project-initializer | Task menu and dependency batches | `/sc:init` is the same menu (its description named the agent as the "delegated form"; that clause is gone). |
| insight-analyst | Semantic search and annotation with per-link confirmation over `.claude/insights.jsonl`; ref_ts and stats gotchas | Carried into `/sc:insight` (verification finding 4): the Read modes step answers a topic question (narrow with `--list`/`--query`, then judge relevance) and states the `--stats --all` rule; a new Annotate step shows each link with its exact `ref_ts` and appends only approved ones. `deep-researcher`'s "Not for" gate points at `/sc:insight --query`. |
| requirements-analyst | Discovery dialogue | `/sc:brainstorm`. `/sc:pm`'s vague-request pattern now goes through `/sc:brainstorm` → `/sc:design`. |
| git-workflow | PR table and git gotchas | Moved to `/sc:git` in the lean round (`d345f8ac`). |
| learning-guide, socratic-mentor | Teaching styles | `/sc:explain`; Claude Code's built-in Learning and Explanatory output styles (code.claude.com/docs/en/output-styles). |
| root-cause-analyst | Hypothesis loop, 3-cycle cap | `/sc:troubleshoot` flow steps 3–4 ("max 3 cycles before escalate to user"). |
| simplicity-guide | Over-building checks, domain exceptions | `RULES_QUALITY.md` `<anti_over_engineering>`: dependency gate, earned-over-premature, "Do NOT simplify" list. |
| security-, quality-engineer | `<finding_policy>` (report every finding with severity and confidence). It was kept in three copies in the mode-retire round. `security-engineer`'s repo-specific threat model (`sc-not-webapp`, `sc-installer-writes`). | `self-review.md` keeps the full text, and `/sc:review` names it as the `--structured` reviewer. `/sc:analyze` Scan step now holds the rule on every path, main session or delegate, with one severity scale (finding 3). The threat model went to `.claude/rules/gotchas/general.md` `security-review-scope` (finding 5). |
| system-, backend-, frontend-, devops-architect, performance-engineer, python-expert, refactoring-expert, technical-writer | Routing targets in `/sc:analyze`, `/sc:review`, `/sc:implement`, `/sc:pm`, `/sc:agent`. `backend-architect`'s ">2 tables" unit in `RULES_QUALITY.md`. | Routing tables rewritten (next section). The ">2 tables" unit is now stated for "a schema change". |

## Shipped content changed

- `commands/analyze.md`: `<focus_agent_mapping>` → `<focus_delegation>`. One focus on a readable target runs in the main session. Several focuses on a large target get one `general-purpose` delegate per focus, each with the finding rule.
- `commands/review.md`: `<focus_agent_mapping>` → `<review_lens>`. With `--structured`, the domain angle goes into the isolated reviewer's prompt.
- `commands/implement.md`: `--type` selects the checks to lead with, not a lead agent.
- `commands/pm.md`: drops the pointer to the agent file; Delegate and Improve steps, the vague-request pattern and the auth example rewritten.
- `commands/agent.md`: the wrong-route example now uses `deep-researcher` for a repo question.
- `commands/init.md`, `commands/load.md`: see the table above.
- `core/rules/RULES_QUALITY.md`: the ask-first unit sentence (canary gate applies).
- The five kept agents: `<fallback>` returns open items to the main session instead of naming a sibling; `Related:` lines and two "Not for" gates no longer name retired agents.
- `agents/README.md`: one table of the five with the reason each is a subagent. The 14-row overlap table and the 6-row conflict table were about retired agents and are gone.
- `ARCHITECTURE.md`, `README.md`, `docs/reports/ORCHESTRATION_COMMANDS.md`, `docs/codex/.../02_component_and_delivery_map.md`: counts 24 → 5 and the "WHO TO BE" label.

## Authoring rules

- `.claude/rules/agent-authoring.md`: the decision gate now states the test from 00-intent. Agent = "WHO DOES ISOLATED WORK". The description's first part names a job, not an identity. The example descriptions no longer point at retired agents. The `<fallback>` template forbids naming a sibling agent.
- `command-authoring.md`, `mode-authoring.md`, `mcp-authoring.md`: the one-line taxonomy follows.
- `xml-prose-format.md`: the `<bounds>` example's fallback no longer escalates to an agent.

## Upgrade path

`agents/` is shared with the user's own files, so a retired agent is removed by content, not by name. `scripts/gen_shipped_names.py` was rerun and the 19 names are now `shipped_now: false` with digests of every revision. `install_paths.RETIRED_AGENT_DIGESTS` now covers 22 names, built from that history with the generator's own digests. `test_q10_retired_digests_cover_every_shipped_revision` holds the two tables equal.

End-to-end check on a scratch `CLAUDE_CONFIG_DIR`:

1. Installed master (`f467012c`, 24 agents). Added `my-agent.md`, hand-edited `performance-engineer.md`, and wrote `agent-memory/python-expert/MEMORY.md`.
2. Installed the branch. Left in `agents/`: the five kept agents, `my-agent.md` and the edited `performance-engineer.md`. `agent-memory/python-expert/` was untouched.
3. Uninstalled. Left: `my-agent.md` and the edited `performance-engineer.md`.

`test_c08_retired_agents_and_skills_do_not_survive` pins 32 retired items in the `b933fd65p-user` fixture: the earlier 17, plus 15 of the 19 that the fixture holds.

## Tests changed

- `test_agent_structure.py`: `TestSimplicityGuideSpecific` removed with the file.
- `test_session_memory_folder.py`: the three project-manager tests are gone. The writer check now reads `save.md`.
- `test_author_check_corpus.py`: the docstring example names `repo-index.md`.
- `test_install_upgrade_scenarios.py`: the C-08 count is 17 → 32.
- `test_cross_references.py`: the trigger-uniqueness test, which passed on empty input (no agent uses the `triggers -` form), is replaced by `TestRetiredAgentNames`. That test fails when any shipped `.md` names a name in `install_paths.RETIRED_AGENT_FILES`. Planting `python-expert` in `commands/pm.md` turned it red.

## Verification follow-up

Applied after [02-verify.md](./02-verify.md): self-review loses the `Agent` tool (read-only per the sub-agents doc's own advice); the nesting rule in `agent-authoring.md` follows the current docs; `/sc:improve`, `/sc:cleanup`, `/sc:roadmap`, `/sc:task`, `/sc:brainstorm` and both content READMEs stop promising specialist agents. The applied table is at the end of 02-verify.md.
