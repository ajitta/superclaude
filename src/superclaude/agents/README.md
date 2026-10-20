# superclaude Agents

Five subagents, each kept because the work needs something only a subagent gives: a context of its own for high-volume reading, tools restricted to the job, or a reviewer that has not seen the author's reasoning. Domain knowledge the model already has (language, framework, architecture, security practice) is not an agent here; commands and rules carry the checklists, and the main session or a `general-purpose` delegate applies them. The 2026-10 roster audit retired 19 persona agents on that test: docs/features/agent-roster-audit/.

## Content Delivery

Agents managed by Claude Code native delegation. Claude Code delegates when a request matches the "Use when …" trigger in an agent's `description` frontmatter and is not a look-alike that the description's "Not for … — <neighbor>" gate sends elsewhere. `self-review` and `verifier` run only when the user explicitly asks for them. Install to `~/.claude/agents/` on `superclaude install`; an upgrade removes a retired agent file only when its text matches a revision superclaude shipped.

## Available Agents

| Agent | Why it is a subagent | Description |
|-------|----------------------|-------------|
| `deep-researcher` | Isolates many web fetches; returns a cited synthesis | Web research, cross-check, citation-ready synthesis |
| `repo-index` | Isolates a whole-repo scan; writes one compact index | Repo indexing + codebase briefing |
| `business-panel-experts` | Long multi-framework analysis in its own context; SSOT of the panel's frameworks for /sc:business-panel | Multi-lens business strategy synthesis + debate |
| `self-review` | Fresh-context reviewer, read-only tools; invoked explicitly | Independent second pass on a finished work product (plan, design, code) + reflexion |
| `verifier` | Fresh-context run-and-report, no edit tools; invoked explicitly | Run-and-report check of shipped behavior against its plan doc |

## Permission Framework

No shipped agent sets `permissionMode` — all inherit the session's permission mode (frontmatter field stripped in 672055c as unreliable). CC-native values remain available for local overrides:

| permissionMode | Effect |
|---------------|--------|
| `acceptEdits` | File edits auto-approve; Bash/MCP prompt |
| `default` | Each tool prompts on first use |
| `plan` | Read-only; mods blocked till approved |

## Model Routing

Every agent omits `model:` and inherits the parent session model — no agent pins a tier.

Rationale mirrors the `effort:` removal in commit `8edd05d`: no hardcoded model without measured evidence. Pinning a tier overrides the user's cost-vs-quality choice for the session, and a pin written against one model generation silently misroutes after the next.

Resolution order: per-invocation `model` parameter > frontmatter `model:` > `CLAUDE_CODE_SUBAGENT_MODEL` > main conversation model (Claude Code v2.1.251+).

Moving work to Fable 5.1 is the user's call. Each path lasts a different length:

| Path | How long it lasts |
|---|---|
| `claude --model fable` | That session only (a later `--continue` or `--resume` of it restores Fable). The recommended "when needed" path, because it never changes the saved default |
| `/model fable` | Saved to user settings, so later sessions also start on Fable, until `/model default`; in `-p` mode it applies to that session only |
| `/model` picker, `s` on the Fable row | This session only; the saved default stays unchanged |
| Asking for one delegation on Fable | That delegation only: the Agent tool call carries `model: "fable"` |
| `CLAUDE_CODE_SUBAGENT_MODEL=fable` | Every subagent that no per-invocation parameter or frontmatter assigns a model (built-in Explore and Plan, and forks, excepted) |

When Fable 5.1: Anthropic's routing advice is "Most workloads start with Claude Opus 5.5"; move to Fable 5.1 when your evals at `xhigh` or `max` effort still fall short on demanding reasoning or long-horizon agentic work. Claude Code describes Fable as suited to "tasks larger than a single sitting". At list price Fable 5.1 costs 2.5× Opus 5.5 on input and output ($10/$50 against $4/$20 per MTok) and 1.25× on cache reads ($0.25 against $0.20), which Anthropic says "make up the majority of agentic and coding work costs". Where a plan bills Fable to usage credits, `-p` mode and the Agent SDK bill it without the consent prompt that interactive sessions show.

When Sonnet 5.5: the downward path is also the user's call. Anthropic's announcement places Sonnet 5.5 at "well-scoped everyday tasks, fixing bugs" and Opus 5.5 at "complex work requiring careful judgment", and the Sonnet 5.5 prompting guide adds "For the hardest long-horizon work, an Opus model is the better choice." At list price Sonnet 5.5 costs half of Opus 5.5 on input and output ($2/$10 against $4/$20 per MTok) and the same on cache reads ($0.20). The paths last as long as the Fable ones: `claude --model sonnet` for that session only, `/model sonnet` saved to user settings until `/model default`. Neither 5.5 model reads the other's thinking blocks, so switching between them mid-session runs the later turns without the earlier reasoning; start the session on the model it needs.

## Authoring Rules

See `.claude/rules/agent-authoring.md` for full authoring spec.

Validation: `uv run python -m pytest tests/unit/test_agent_structure.py -v`

## Agent Memory (v2.1.33)

Agents declare persistent memory via `memory` frontmatter. Source files ship `memory: project`; installer rewrites to match install scope. The independent reviewers `self-review` and `verifier` ship no `memory`, so no earlier verdict reaches their next review and they leave no memory folder in the project. Full spec (scope→location table, `_rewrite_agent_memory_scope` mechanics, MEMORY.md injection): `.claude/rules/agent-authoring.md` § memory.

## Escalation

An agent that hits a question outside its job returns it to the main session as an open item; no agent hands work to a sibling, because the main session decides what runs next. Nested spawning is possible where `Agent` is in an agent's tools; `self-review` and `verifier` leave it out so they stay read-only and run-only. Scope unclear or a likely breaking change: stop and return the question. Harness-reported context usage ≥60% (the --uc point): compress output, don't skip steps; with no reported figure, don't estimate one.

## Routing Overlaps

The split is set by the `Not for … — <neighbor>` gate in the named descriptions (SSOT: change the description first, then this row):

| Overlap | Goes to | Gate in |
|---|---|---|
| second-pass review vs run-and-report evidence | self-review / verifier | self-review, verifier |
| web research vs one question about the code | deep-researcher / direct search | deep-researcher |

## Related

- `commands/` — Workflow entry points; some dispatch these agents
- `modes/` — Cognitive overlays shaping agent behavior
- `core/FLAGS.md` — Behavioral flags + execution modes (Model Routing lives in this README's section above)
