---
status: draft
revised: 2026-08-21
---

# Trigger-tier classification — which `/sc:` commands may fire on their own

Detail for [05-plan.md](./05-plan.md) Task 6 (and the two upgrades deferred to Task 14), which
addresses finding A12 in
[03-analysis.md](./03-analysis.md). Twenty-two commands already carry auto-triggerable wording and
none fired in thirty days, so this classification is not about unlocking the roster — its value is
that five commands which mutate the repository or skip a workflow gate are open to model invocation
today and should not be.

**Classification criteria.** Three axes, applied to every command: side effect (code mutation /
file creation / session-state mutation / none), recovery cost of a wrong fire (zero steps — read and
move on / one step — delete a file / many steps — revert), and whether a wrong fire skips an
approval gate. The `<never>` bounds in each command body are the evidence for the first axis.

**Allow auto-trigger — 15**

| Group | Commands | Basis |
|---|---|---|
| Console-only, no side effect | help, recommend, select-tool, explain, estimate, reflect, prompt | `<never>` bars exec and modify. A wrong fire costs one paragraph. `help` is explicit: *never exec commands, make files, activate modes, modify project state* |
| One file, recoverable by deleting it | analyze, review, troubleshoot, index-repo, document | `analyze` — *never modify code*; `review` — *never auto-merge, auto-approve, modify artifact without explicit permission*; `index-repo` — *never modify source, exceed 5KB* |
| Safe but expensive — allow with cost noted | business-panel, spec-panel, research | No file or code mutation, but multi-expert panels and multi-hop web research make a wrong fire cost tokens rather than cleanup |

`recommend` is the clearest case for routing: answering "which `/sc:` command fits here?" is its
entire purpose, and it is useless if it only fires when the user already knows the answer.

**Keep explicit-only — 21**

| Group | Commands | Basis |
|---|---|---|
| Mutates code or repository | implement, improve, cleanup, build, test, git, init, promote-feature, index, auto-improve | Recovery needs a revert. `git` rewrites history; `init` — *never overwrite existing files*; `promote-feature` moves files between directories |
| Mutates session or stored state | save, load, insight, sc, agent, pm, task | Memory stores and `insights.jsonl` are appended to. `sc` is the dispatcher — a wrong fire hijacks the whole turn |
| Guarded by a workflow gate | brainstorm, design, plan, roadmap | `RULES_DOCS.md` `workflow_gates` requires user approval between phases. Auto-firing creates a feature folder and phase documents unasked and skips the gate |

**Changes against the current wording — 11 commands**

Downgrade to explicit-only (9), currently Tier A:

| Command | Reason |
|---|---|
| git | rewrites repository history |
| brainstorm, design, plan, roadmap | skips the approval gate, creates phase docs unasked |
| improve | mutates code |
| insight | appends to `insights.jsonl` |
| pm, task | sub-agent orchestration — both cost and side effects |

Upgrade to auto-triggerable (2), currently Tier B: `select-tool` (console-only analysis,
*never override explicit preference*) and `index-repo` (output ceiling written into its own bounds).

Net effect: Tier A shrinks from 22 to 15.
