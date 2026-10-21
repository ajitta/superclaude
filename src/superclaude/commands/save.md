---
description: Save session context to the committed project memory folder (.claude/memories/) and Claude auto memory. On request only — the user's /sc:save or a workflow step that names it. Not for "remember this" or the end of a task — keep working.
---
<component name="save" type="command">

  <role command="/sc:save">
    <mission>Session lifecycle management with a committed project memory folder + Claude auto memory for context persistence</mission>
  </role>

  <syntax>/sc:save [--type session|learnings|context|all] [--summarize] [--checkpoint]</syntax>

  <flow>
  1. Sync: run the /sc:load Sync step (installed sibling commands/sc/load.md; Read it when its text is not in context) before writing — a `learnings_` file the other machine changed would otherwise conflict
  2. Analyze: session progress + discoveries
  3. Persist (memory folder): Write .claude/memories/session_[date]_[host-slug]_[branch-slug].md — first line `branch: <name> @<short sha>`, then the summary and a `## Next actions` checklist; a second save the same day on the same branch from the same machine updates it; a record another machine wrote is never edited → .claude/memories/learnings_[topic].md (insights); flat basename only, no path segments; create the folder when absent
  4. Persist (auto memory): save the durable facts a later session needs (the no-ephemeral gotcha) to the auto memory folder, in the file layout Claude Code's memory instructions give; every worktree of the repo shares this folder, so name the branch in each project entry and Edit the one MEMORY.md line instead of rewriting the file
    4.5. Corrections-Review: capture each user correction not yet recorded as a feedback memory whose body names the broken rule as `violated_rule: "[RNN Name]"` [R14 Correction Capture].
    4.6. Auto memory off: Claude Code names no auto memory folder anywhere in the session's context, neither in the system prompt nor in the first message (an agent's own agent memory folder does not count; for example the `autoMemoryEnabled` setting, `CLAUDE_CODE_DISABLE_AUTO_MEMORY`, or a self-hosted session turns it off) → skip the Persist (auto memory) step and write each correction from the Corrections-Review step to .claude/memories/learnings_corrections.md instead, so /sc:analyze still finds its `violated_rule` line
  5. Verify: Glob .claude/memories/*.md + Read MEMORY.md confirms both stores (auto memory off: the memory folder only)
  6. Checkpoint: recovery points + progress tracking
  7. Validate: data integrity + no duplicates across stores
  8. Session Goal: if session goal set via /sc:load, evaluate completion status (done/partial/deferred)
  9. Share: the .claude/memories/ files this save wrote are uncommitted → list them and ask `[y/n]` to commit only those files: `git add -- <files>`, then `git commit -m "docs: session memory — <topic>" -- <files>`, so nothing else already staged goes in; detached HEAD → no commit offer, say why; yes, and the branch has an upstream, is not behind it, and `git diff --name-only '@{u}'...HEAD` lists memory files only → ask `[y/n]` again before `git push`; otherwise commit only and say the push is left to the user; no → leave the files uncommitted
  </flow>

  <flags>
  - --type session|learnings|context|all: what to save, per the outputs table.
  - --summarize: also write a summary of the session's work and learned patterns.
  - --checkpoint: recovery points, per the Checkpoint step of the flow.
  </flags>

  <compaction_strategy>
  Preserve (high signal): (1) problems hit and how they were resolved; (2) approaches tried or set aside, and why; (3) what was asked, decided, ruled out, or set as a constraint — stated exactly; (4) where the work stands, including session goal status; (5) what is open or promised next; (6) exact names, numbers, paths, commands, and wording that would be hard to reconstruct
  Discard (low signal): verbatim tool output, intermediate search results, committed diffs, duplicate context
  Claim strength: an assumption stays an assumption, planned work stays planned, an attempted check stays attempted — compaction shortens the record, never upgrades it, because a promoted claim re-enters the next session as fact [R15 Verification]
  Format: structured summary (decisions, todo, context pointers) — not narrative prose
  </compaction_strategy>

  <storage>
    Memory folder (primary): .claude/memories/ — one markdown file per memory name, committed with the project
    Branch slug: `git branch --show-current` with `/` → `-`; detached HEAD → `detached-<short sha>`. Session records are add-only per branch and machine, so parallel branches, worktrees and machines never conflict on merge
    Host slug: `hostname` output, lowercased, each run of characters outside [a-z0-9] → `-`, leading and trailing `-` removed; no `hostname` → the `COMPUTERNAME` or `HOSTNAME` variable; neither → `unknown-host`
    Auto memory (supplementary): the folder Claude Code names for the session, in the system prompt or the first message (CC-native, per-project; moves with the `autoMemoryDirectory` setting) — MEMORY.md is its index and loads automatically, memory files are read on demand
    Agent memory: per agent, kept by Claude Code (not written by /sc:save); location follows the agent's `memory:` scope — user ~/.claude/agent-memory/{name}/, project .claude/agent-memory/{name}/, local .claude/agent-memory-local/{name}/
  </storage>

  <outputs note="Per --type flag">
| Type | Memory folder | Content |
|---|---|---|
| session | session_[date]_[host-slug]_[branch-slug] | Full context |
| learnings | learnings_[topic] | Patterns + insights |
| context | context_[project] | Project state |
| all | All above | Complete preservation |
Every type also saves its durable facts to auto memory as memory files, unless auto memory is off; MEMORY.md holds only their one-line pointers.
  </outputs>


  <tools>
  - Write/Edit: memory folder + auto memory persistence
  - Glob: list memory files
  - Read: verify both stores
  - Bash: `hostname` and read-only git (branch, rev-parse, rev-list, diff) for the record name and the Sync and Share steps; fetch in the Sync step; pull, commit and push only after the user's yes
  </tools>

  <examples>

| Input | Output |
|---|---|
| `/sc:save` | Session record for the current branch + one-line MEMORY.md pointer |
| `--type all --checkpoint` | Complete preservation + recovery |
| `--summarize` | Summary + learning patterns |
| `--type learnings` | Patterns + insights only |

  <example name="save-incomplete-work" type="error-path">
    - Input: /sc:save --type all --checkpoint (mid-debugging, broken state)
    - Why wrong: checkpointing broken state preserves errors. Next session loads broken context.
    - Correct: reach stable state first (tests pass or revert), then /sc:save --type all --checkpoint.
  </example>

  </examples>


  <gotchas>
  - no-ephemeral: auto memory (MEMORY.md and its memory files) keeps only what a later session on any branch needs; this session's progress and next actions belong in the session_ file.
  - verify-value: before saving, ask "Will this be useful in future conversation?" If no, skip
  </gotchas>

  <bounds>
    <does>memory folder + auto memory sync, checkpoints when --checkpoint is given, discovery preservation.</does>
    <never>saves without validation, overrides without a checkpoint, duplicates content across stores, or commits, pulls or pushes without the user's yes.</never>
    <fallback>Memory folder not writable: auto memory only, and tell the user. Ask the user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:load /sc:reflect"/>
</component>