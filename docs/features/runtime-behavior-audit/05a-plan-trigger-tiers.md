---
status: approved-for-plan
revised: 2026-08-21
---

# Trigger-tier classification — which `/sc:` commands may fire on their own

Detail for [05-plan.md](./05-plan.md) Task 8 (and the two upgrades held until Task 1 reports), which
addresses finding A12 in
[03-analysis.md](./03-analysis.md). Twenty-two commands already carry auto-triggerable wording and
none fired in thirty days, so this classification is not about unlocking the roster — its value is
that nine commands which mutate code, write repository state, or skip a workflow gate are open to
model invocation today and should not be.

**Classification criteria.** Three axes, applied to every command: side effect (code mutation /
file creation / session-state mutation / none), recovery cost of a wrong fire (zero steps — read and
move on / one step — delete a file or a memory entry / many steps — revert), and whether a wrong
fire skips an approval gate. The `<never>` bounds in each command body are the evidence for the
first axis, and the `<flow>` and `<outputs>` blocks for the second — a command whose flow writes to
source files is a code mutator regardless of how its description reads.

**Allow auto-trigger — 13**

| Group | Commands | Basis |
|---|---|---|
| Console-only, no side effect | help, recommend, select-tool, explain, estimate, prompt, review | `<never>` bars exec and modify. A wrong fire costs one paragraph. `help` is explicit: *never exec commands, make files, activate modes, modify project state*; `review` — *never auto-merge, auto-approve, modify artifact without explicit permission* — and its `<outputs>` are a console summary, not a file. `prompt` writes only when the user names a destination |
| Creates a recoverable artifact | analyze, index-repo, research, reflect | Recovery is deleting what was made. `analyze` — *never modify code*, and only `--format report` writes at all (`text` is the default); `index-repo` — *never modify source, exceed 5KB*; `research` writes one doc plus a README line per `RULES_DOCS.md` `<doc_output_convention>`; `reflect` appends a memory entry |
| Safe but expensive — allow with cost noted | business-panel, spec-panel | No file or code mutation, but multi-expert panels make a wrong fire cost tokens rather than cleanup |

`recommend` is the clearest case for routing: answering "which `/sc:` command fits here?" is its
entire purpose, and it is useless if it only fires when the user already knows the answer.

**Keep explicit-only — 23**

| Group | Commands | Basis |
|---|---|---|
| Mutates code or repository | implement, improve, cleanup, build, test, git, init, promote-feature, index, auto-improve, troubleshoot, document | Recovery needs a revert. `git` rewrites history (`<approval_required>push --force, reset --hard, rebase`); `init` — *never overwrite existing files*; `promote-feature` moves files between directories; `troubleshoot` writes a failing test and applies the fix (flow steps 5–6) and its `<never>` bars only *risky fixes without confirm*; `document --type inline` writes docstrings into source files |
| Mutates session or stored state | save, load, insight, sc, agent, pm, task | Memory stores and `insights.jsonl` are appended to. `sc` is the dispatcher — a wrong fire hijacks the whole turn |
| Guarded by a workflow gate | brainstorm, design, plan, roadmap | `RULES_DOCS.md:53-62` `workflow_gates` requires user approval between phases. Auto-firing creates a feature folder and phase documents unasked and skips the gate |

**Changes against the current wording — 13 commands**

Downgrade to explicit-only (11), currently Tier A:

| Command | Reason |
|---|---|
| git | rewrites repository history |
| brainstorm, design, plan, roadmap | skips the approval gate, creates phase docs unasked |
| improve | mutates code |
| troubleshoot | writes a test file and applies a code fix |
| document | `--type inline` edits source files |
| insight | appends to `insights.jsonl` |
| pm, task | sub-agent orchestration — both cost and side effects |

Upgrade to auto-triggerable (2), currently Tier B: `select-tool` (console-only analysis,
*never override explicit preference*) and `index-repo` (output ceiling written into its own bounds).

**A stronger mechanism for the worst case, applied to `git`.** `disable-model-invocation: true`
blocks model selection outright rather than discouraging it in prose; `auto-improve` was the only
command carrying it, and A12 counts it as its own tier for that reason. Wording is enough for the
ten downgrades whose worst case is a revertible edit. `git`, whose worst case is a rewritten
history, now carries the flag as well (applied 2026-08-21) and keeps its wording downgrade under
Task 8, matching `auto-improve`, which has both.

Net effect: Tier A shrinks from 22 to 13.
