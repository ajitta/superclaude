# Orchestration commands: `/sc:agent` vs `/sc:pm` vs `/sc:task`

Which of the three orchestration commands to run, and when none of them is the right call. SSOT for each command's behavior is its file in `src/superclaude/commands/` — this page only explains how to choose.

All three analyze a request, delegate to sub-agents and track progress, and all three load `core/rules/RULES_DELEGATION.md` (`scripts/context_loader.py` matches `/sc:(pm|agent|task)`). They differ in what they add on top. Two questions pick the command:

1. **Is the scope settled?** — success criteria, acceptance checks, affected modules.
2. **What is the hard part: many domains, or many steps?**

```
Request
 ├─ single file, < 3 steps ─────────────── no command: edit directly (all three say so)
 ├─ scope unclear ──────────────────────── /sc:agent   stops at Phase 1 until scope is confirmed
 ├─ scope clear, several domains ───────── /sc:pm      brainstorm / direct / wave routing
 └─ scope clear, 3–7 dependent steps ───── /sc:task    Epic → Story → Task, evidence-gated completion
```

## Comparison

| | `/sc:agent` | `/sc:pm` | `/sc:task` |
|---|---|---|---|
| Adds | 5-phase session protocol (Clarify → Plan → Iterate → Implement → Review); `@repo-index` / `@deep-researcher` services | Strategy classification + parallel streams of `general-purpose` sub-agents; PDCA learning log in `.claude/memories/learnings_[topic].md` | Task hierarchy in `TaskCreate`/`TaskUpdate`; `--strategy sequential\|parallel\|adaptive`; `cleanup` sub-command |
| Gate | No implementation before scope, success criteria and acceptance checks are confirmed | Simple task → direct work, no orchestration | > 3 files → numbered plan, wait for approval; `completed` only with cited evidence (exit code, test output, observed outcome) |
| Best when | Vague request, cost of misreading it is high | 3+ independent streams in different expertise domains | Dependency chains, circular-dep risk, work that spans sessions |
| Wrong when | A spec already exists — Clarify idles | Work is sequential (A → B → C) — nothing to parallelize | Fewer than 3 tasks — overhead only |
| Source | `commands/agent.md` | `commands/pm.md` | `commands/task.md` |

## Examples

### `/sc:agent` — pin the scope first

| Request | Why | What happens |
|---|---|---|
| `/sc:agent 'login feels slow, fix it'` | Where it is slow and what "fixed" means are undefined | Clarify: target p95? → `@repo-index` for the auth path → measure → agree on scope → implement |
| `/sc:agent 'can we move to React 19?'` | Investigation; implementation not yet decided | `@repo-index` (current deps) → `@deep-researcher` (breaking changes) → risk report, no code |
| `/sc:agent 'first time in this repo, raise test coverage'` | First task of the session, scope open | `<startup>` git status → `@repo-index` → "which module first?" → proceed |

### `/sc:pm` — scope is known, domains are many

| Request | Strategy | What happens |
|---|---|---|
| `/sc:pm 'real-time chat + video'` | wave | W1 (WebSocket ‖ WebRTC) → W2 UI → W3 E2E → W4 (security ‖ quality) |
| `/sc:pm 'build an auth system'` (no requirements) | brainstorm | requirements (/sc:brainstorm) → design → [API + data stream ‖ security review stream] → UI stream |
| `/sc:pm 'audit security + performance + a11y'` | wave, one wave | Three independent domains → three sub-agents at once → merged report |
| `/sc:pm 'fix LoginForm.tsx:45'` | **not pm** | Single file, < 3 steps → edited directly |

### `/sc:task` — many steps that must be tracked

| Request | Why | What happens |
|---|---|---|
| `/sc:task 'refactor auth and permissions modules'` | Circular dependency likely | Dependency map → cycle detected → options: A) extract shared interface, B) merge → user picks → execute |
| `/sc:task 'TODO app, vanilla JS, 4–5 files'` | > 3 files → approval checkpoint | Epic → Story → Task → numbered plan → approval → implement → test output cited as evidence for `completed` |
| `/sc:task 'migration → model → API → frontend' --strategy sequential` | Strict A → B → C chain | Each step records its evidence (exit code, test result) before the next starts |
| `/sc:task cleanup --dry-run` | Previous session left tasks behind | Lists completed/cancelled for deletion; stale ones deleted only after confirmation |

## Combining them

The `<handoff>` chains already point this way: `/sc:pm → /sc:task`, `/sc:agent → /sc:implement / /sc:research`.

- New payment system: `/sc:agent` settles the scope → `/sc:pm --strategy wave` splits the domains → inside a large wave, `/sc:task` tracks the steps.
- In practice one command usually absorbs the others' role lightly (`pm` also tracks with `TaskUpdate`; `task` also delegates). Using all three on one request is rare.

## Why they overlap

The analyze → delegate → track skeleton is shared by authoring spec, not by accident: each command is a different axis over the same primitives — `agent` is a session protocol, `pm` is a routing strategy, `task` is a tracking structure. Evidence of distinct value: in `docs/analysis/karpathy-empirical-test-ajitta-2026-05-08.md`, `/sc:task` was the only command that caught the baseline skipping the > 3-file checkpoint.
