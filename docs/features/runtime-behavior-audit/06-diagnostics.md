---
status: complete
revised: 2026-08-22
---

# Diagnostics — why the activation paths are closed

Phase 1 of [05-plan.md](./05-plan.md): Task 1 (why 22 auto-triggerable commands never fire, A12)
and Task 2 (why delegation never reaches the agents, A6). Both were investigation-only; the
findings set the upgrade half of Task 8, the scope of Task 12, and the packaging notes of Task 13.

## Method

The audit's evidence came from a macOS machine — 14,596 prompt-history entries and 1,331 session
transcripts. This work ran on a different machine (Windows, user-scope install), so none of that
corpus is reachable here and nothing below re-derives it. Instead the questions were answered two
ways that the audit could not use:

1. **A live probe set.** Six `claude -p` runs in scratch directories, captured as
   `--output-format stream-json` and parsed for `tool_use` blocks. Each prompt was written to match
   one command's stated positive cue as closely as the description allows.
2. **A second, independent transcript corpus.** The 39 transcripts on this machine, 2026-07-08 →
   2026-08-21, 743 `tool_use` blocks.

Machine-level facts that make the probes meaningful: this machine carries a **user-scope** install
(36 commands, 23 agents in `~/.claude/`) and **no project-scope install** in the probe directories.
That is the opposite configuration from the audit's machine, which had project-scope installs only.

---

## Task 1 — Why 22 auto-triggerable commands never fire

### The mechanical preconditions, checked

The plan named three. None of them is the blocker.

| Precondition | Result |
|---|---|
| Description length against the 1024-char skill cap | Longest is `prompt` at 517. Nothing is near the cap, so nothing is being rejected for length |
| Whether commands reach the model's skill list at all | **They do.** Probe 1 asked a scratch-directory session to name every skill beginning `sc:`; it returned 35, the full roster minus the one command carrying `disable-model-invocation` |
| Whether the negative gate suppresses more than intended | Not distinguishable from the outside, and moot — see below, where commands whose gate plainly does *not* cover the prompt still do not fire |

Probe 1 settles the availability question for user scope specifically. Project scope, the audit's
configuration, was not re-tested; but availability cannot be the explanation for a machine where
availability is confirmed and the fire count is still zero.

### The probes

| # | Prompt | Setup | Result |
|---|---|---|---|
| 1 | "name every skill beginning `sc:`" | user scope, scratch dir | **35 skills listed** |
| 2 | "audit this codebase for security and performance issues" | same | Bash ×4, **0 Skill calls** |
| 3 | "give me a second opinion on it — an independent review before I share it with the team" | same | Bash ×3, **0 Skill calls** |
| 4 | *identical to probe 2*, plus a six-line routing block in `CLAUDE.md` | same | **`Skill sc:analyze`**, args `--focus security,performance --scope project` |
| 5 | "the login flow fails intermittently … I need a proper root-cause investigation with hypotheses tested against evidence" | same | Bash ×2, **0 Skill calls, 0 sub-agents** |
| 6 | probe 4's shape aimed at an explicit-only command | same | **inconclusive** — blocked three times by an unrelated third-party `UserPromptSubmit` hook, never reached the model |

Probe 2's prompt contains the word *audit*, which `sc:analyze`'s description names as a positive cue,
and asks for two of the four domains it names. Probe 3 uses *second opinion* and *independent
review*, both of which appear verbatim in `sc:review`'s description. Probe 5 describes an
intermittent failure whose quick fix did not hold and asks for hypotheses tested against evidence —
which is `sc:troubleshoot`'s cue and `root-cause-analyst`'s description almost word for word.

Probe 4 is the same prompt as probe 2 against the same install, differing only by six lines of
always-loaded text. It fired, and picked correct flags unprompted.

### The corroborating corpus

Across 39 transcripts and 743 tool calls in 44 days on this machine, the model issued **6 `Skill`
calls in 6 sessions**: `claude-api` ×3, `skill-builder`, `tavily-search`,
`engagement-retention-advisor`. **Zero `sc:` calls** — with all 36 descriptions in the skill list
the whole time.

That base rate is the point. Model-initiated skill invocation is rare for *everything*, not just for
SuperClaude: roughly one call per 124 tool calls, in 15% of sessions. And half of them went to
`claude-api`, whose description does not describe — it commands: *"TRIGGER — read BEFORE opening the
target file; don't skip because it 'looks like a one-liner'"*, followed by a list of literal tokens
and an explicit SKIP rule. The audit's own 30-day table has the same shape: `artifact-design` took
22 of 36 calls, and it is mandated by the `Artifact` tool description — *"you MUST load the
`artifact-design` skill"* — not selected on its own merits.

### Finding

**The question "is the description considered and rejected, or never considered at all?" has no
observable answer, and does not need one — because the channel it competes in carries almost no
traffic for anybody.** What fires is what some *always-loaded* text tells the model to fire:
a tool description, an output style, an imperative TRIGGER block, or a project instruction file.
Descriptions in the "Use when the user asks X" form are a routing table nothing consults.

SuperClaude's problem is sharper than a wording problem, and it is one-line checkable:

```
$ grep -c "/sc:" src/superclaude/core/{FLAGS,PRINCIPLES,RULES}.md
FLAGS.md:0   PRINCIPLES.md:0   RULES.md:1
```

The one hit in `RULES.md` is a table row naming when a rules module loads. **The framework's
always-loaded kernel never once points at the framework's own command surface.** It spends that
channel on flags and rules and mentions the commands nowhere. Every competitor that wins these cues
— caveman, karpathy-guidelines, claude-mem, `artifact-design` — reaches the model through exactly
the channel SuperClaude leaves empty.

### Implied fix

Route from the always-loaded channel, which SuperClaude already owns twice over: the
`CLAUDE_SC.md` import chain, and the `context_loader.py` `UserPromptSubmit` hook that already
injects text on every matching prompt. Probe 4 is the working demonstration at the smallest possible
size — six lines mapping a request shape to a command name, and the model both invoked the skill and
chose sensible flags.

Two things this does *not* license:

- **It is not a reason to rewrite the 15 remaining auto-triggerable descriptions.** Probes 2, 3 and
  5 rewrite nothing and show that wording is not the lever. A description rewrite is work in a
  channel measured at near-zero throughput.
- **It is not free.** A routing table in always-loaded context costs tokens on every prompt and
  fires on match, so it belongs to a small set of high-value, low-blast-radius commands
  (`recommend`, `analyze`, `explain`, `review`) rather than to the roster.

### Consequences for the plan

**Task 8, upgrade half — declined, not deferred.** `select-tool` and `index-repo` were held pending
this report. Moving them from explicit-only to auto-triggerable changes wording in the channel this
diagnostic measures at near-zero, so it buys no activation, while removing a bound that costs
nothing to keep. Tier A stays at 11 of 36.

The downgrades already shipped remain justified on their own terms: they are about blast radius if
throughput ever rises — after plugin packaging, or on a future model — not about activation today.
That asymmetry is the whole reason the two halves could be split.

**Task 13, packaging.** Packaging fixes availability. Probe 1 shows availability is already solved
at user scope and the fire count is zero anyway, so packaging alone will reproduce this result
exactly. The plugin must ship the routing mandate, or it ships the same silence more widely.

**Open, with the experiment specified.** Whether explicit-only wording *blocks* a mandate-driven
invocation is untested — probe 6 never reached the model. It matters only if the routing table is
ever pointed at an explicit-only command, which the current shortlist does not do. To settle it:
probe 4's setup with `sc:index-repo` (console-only, output-ceilinged, safe to actually run) in an
environment with third-party `UserPromptSubmit` hooks disabled.

---

## Task 2 — Why delegation never reaches the agents

### Classification: routing never suggests them

The audit found 22 of 23 agents at zero invocations in 30 days, with `self-review` the only one
used. This machine's independent corpus agrees: 3 delegating calls in 44 days —
`general-purpose` ×2, `deep-researcher` ×1. One SuperClaude agent, once.

Probe 5 is the decisive case, because it was written to be the easiest possible route. Recurring
symptom, failed quick fix, explicit demand for hypotheses tested against evidence — the
`root-cause-analyst` description says *"Use proactive when symptoms recur, errors intermittent, or
quick fix fail. Use when suspected cause must be falsified before remediation."* The model answered
inline with two Bash calls and proposed no delegation at all. Nothing was suggested and declined;
nothing was suggested.

### The mechanism, and it is circular

Agent descriptions live in the same near-zero-throughput channel as command descriptions, so
Task 1's finding covers them. But the agents have a second, self-inflicted problem the commands do
not.

The rule that would tell the model to delegate — `RULES_DELEGATION.md` `<sub_agent_decision>` — is
an **on-demand** module. `context_loader.py:189` injects it only on this trigger:

```
(--delegate|--concurrency|/sc:(pm|agent|task)|sub.?agent|worktree)
```

Probe 5's prompt matches none of it, so the delegation rules were never in context. They load when
the user has *already* used delegation vocabulary — which is to say, the guidance that would decide
whether to delegate arrives only after delegation has been requested. A user who describes a problem
in ordinary words can never reach it.

Even once loaded, `<agent_routing>` governs *which* agent to prefer when several overlap on one
verb. Nothing in it decides *whether* to reach for an agent in the first place.

So the answer to Task 2's question is the first branch, and for two compounding reasons: the
descriptions sit in a channel nothing consults, and the rule that would override that sits behind a
trigger the case can never satisfy.

### Consequence for Task 12

Task 12 proposed keeping the agents that "survive Task 2" plus `self-review`. On this finding, **no
agent survives on usage, and usage is not evidence about the agents.** Twenty-two agents at zero
invocations is a measurement of the routing layer, not of the roster's quality: they were never
given a path to be chosen.

Right-sizing on those numbers would delete work that was never tried. The defensible order is to
fix routing first — the same always-loaded mandate Task 1 points at, extended to name a handful of
agents, or a `RULES_DELEGATION.md` trigger that fires on problem shapes rather than on delegation
vocabulary — then re-measure, and only then subtract. Task 12's memory-directory half (A11-b,
`.claude/agent-memory-local/` created at install time) is independent of all of this and should
proceed regardless.
