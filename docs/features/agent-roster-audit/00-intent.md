---
feature: agent-roster-audit
phase: intent
owner: ajitta
created: 2026-10-20
updated: 2026-10-20
---

# 00. Intent — which agents still earn a subagent

## Request

"Evaluate, investigate and audit whether any subagents are no longer needed or have become meaningless. Agents defined by an identity seem to be disappearing; find out how Anthropic does it now." (2026-10-20, translated.)

## What Anthropic says now (checked 2026-10-20)

| Source | What it says |
|---|---|
| claude.com blog, "Building agents with Skills: Equipping agents for specialized work" (2026-01-22) | "we'll explain why we stopped building specialized agents and started building skills instead". The architecture is one general agent (loop + code runtime) with MCP for connections and Skills for domain expertise. |
| code.claude.com/docs/en/sub-agents | Use a subagent "when a side task would flood your main conversation with search results, logs, or file contents you won't reference again". "Define a custom subagent when you keep spawning the same kind of worker with the same instructions." Use the main conversation for back-and-forth, shared multi-phase context, and quick changes. Built-ins: Explore, Plan, general-purpose. |
| claude.com, "How and when to use subagents in Claude Code" | Good uses: research-heavy tasks, independent parallel tasks, a fresh perspective, verification before committing, pipeline stages. Under "When shouldn't you use subagents?": "Too many specialist agents. … flooding Claude with options makes automatic delegation less reliable. Most teams settle on a handful of well-scoped agents rather than a sprawling roster." Descriptions should name trigger conditions: "'Reviews code for security issues before commits' routes better than 'security expert.'" |
| platform.claude.com, "Prompting Claude Opus 5", Controlling subagent spawning | Opus 5 "delegates to subagents more readily than prior models"; the sample prompt says to delegate only large, independent, parallelizable work and not to "use subagents to verify or double-check your own work". |
| platform.claude.com, Prompting best practices, "Give Claude a role" | Still present: a role "focuses Claude's behavior and tone". The repo's own evidence review (`docs/research/persona-anchoring-framing-audit-chosh1179-2026-09-14.md` F1) found no accuracy gain from expert personas. |
| `anthropics/claude-plugins-official`, `plugins/*/agents/` | Agents are named by job and bound to a plugin's workflow (code-explorer, code-reviewer, silent-failure-hunter, pr-test-analyzer, patch-verifier, grader). None is a language or role persona. |

So role prompting survives as one sentence of tone. What went away is the identity agent as a unit of architecture.

## Evidence in this repo

- `runtime-behavior-audit/06-diagnostics.md`: 22 of 23 agents had zero invocations in 30 days on the audit machine. A second machine logged 3 delegations in 44 days (`general-purpose` ×2, `deep-researcher` ×1). A probe written to be the easiest possible route to `root-cause-analyst` got no delegation.
- That round's Task 12 declined to cut on usage: "fix routing, re-measure, then subtract". Routing was not changed after that. And the precondition no longer fits: making 24 descriptions fire more often runs against Anthropic's current advice (fewer agents, damped delegation on Opus 5). The question this audit asks instead is whether each agent does something only a subagent can do.
- Most agent bodies carried a workaround sentence ("A delegated subagent cannot ask mid-task: … stop there and return the proposed action and the question"). This is a sign the agents were written for a main session.
- Most `<fallback>` lines said "escalate to <sibling agent>". A subagent cannot spawn another one, so in that position the instruction could never run.
- `.claude/rules/agent-authoring.md` defined an agent as "WHO TO BE (domain expert persona)". That definition is where the roster came from.

## The test

An agent stays only if a recurring job needs at least one of:

1. Its own context, because it reads far more than it returns (web sweep, whole-repo scan).
2. Tools restricted to the job (read-only review, run-but-never-edit).
3. A fresh view that has not seen the author's reasoning (independent review, verification).

The test disqualifies an agent that:

- carries only domain knowledge the model already has (a persona); or
- has to talk with the user mid-task (a subagent returns one summary).

## Verdicts

| Agent | Verdict | Reason |
|---|---|---|
| deep-researcher | keep | 1: many fetches, cited synthesis returns |
| repo-index | keep | 1: whole-repo scan, one compact index returns; `/sc:init` dispatches it |
| business-panel-experts | keep | 1: long multi-framework analysis; SSOT of the frameworks for `/sc:business-panel`, `MODE_Business_Panel`, `BUSINESS_SYMBOLS` |
| self-review | keep | 2 + 3: read-only, fresh-context second pass; explicit only |
| verifier | keep | 2 + 3: run-and-report, no edit tools; explicit only |
| project-initializer | retire | interactive menu; `/sc:init` is the same menu, Claude Code has `/init` |
| project-manager | retire | lifecycle ran only as the main session (`claude --agent`); `/sc:pm` carries orchestration |
| insight-analyst | retire | needs per-annotation confirmation; `/sc:insight` covers query and annotation |
| requirements-analyst | retire | discovery is a dialogue; `/sc:brainstorm` |
| git-workflow | retire | no isolation need; its gotchas moved to `/sc:git` in the lean round |
| learning-guide | retire | teaching is a dialogue; `/sc:explain`, Claude Code's built-in Learning/Explanatory output styles |
| socratic-mentor | retire | questioning is a dialogue; same as above |
| python-expert, refactoring-expert, technical-writer | retire | persona over knowledge the model has |
| system-, backend-, frontend-, devops-architect | retire | persona; referenced only by routing tables in commands |
| security-, performance-, quality-engineer | retire | persona; a focus becomes a lens in `/sc:analyze` / `/sc:review` |
| root-cause-analyst | retire | `/sc:troubleshoot` holds the same hypothesis loop and 3-cycle cap |
| simplicity-guide | retire | its rules already live in `RULES_QUALITY.md` `<anti_over_engineering>` |

## Decisions (owner, 2026-10-20: "추천대로 진행")

1. The persona group (10 domain agents): (a) retire all. Analysis and review focuses become lenses run in the main session or by `general-purpose` delegates. Not taken: (b) merge into 2–3 read-only reviewers; (c) fix routing and re-measure.
2. The interactive group and the two absorbed agents (9): (a) retire as recommended.
3. Rewrite the decision gate in `agent-authoring.md` (and the one-line taxonomy in the other authoring rules) and drop sibling-agent escalation from the template: (a) in this round.
4. Process: (a) record the audit here, implement, verify independently, release a minor version.
