---
description: Save session context to the committed project memory folder (.claude/memories/) and Claude auto memory. On request only — the user's /sc:save or a workflow step that names it. Not for "remember this" or the end of a task — keep working.
---
<component name="save" type="command">

  <role command="/sc:save">
    <mission>Session lifecycle management with a committed project memory folder + Claude auto memory for context persistence</mission>
  </role>

  <syntax>/sc:save [--type session|learnings|context|all] [--summarize] [--checkpoint]</syntax>

  <flow>
  1. Analyze: session progress + discoveries
  2. Persist (memory folder): Write .claude/memories/session_[date]_[branch-slug].md — first line `branch: <name> @<short sha>`, then the summary and a `## Next actions` checklist; a second save the same day on the same branch updates it → .claude/memories/learnings_[topic].md (insights); flat basename only, no path segments; create the folder when absent
  3. Persist (auto memory): Write/Edit MEMORY.md + topic files for cross-session continuity; every worktree of the repo shares this folder, so name the branch in each project entry and Edit the one MEMORY.md line instead of rewriting the file
    3.5. Corrections-Review: capture each user correction not yet recorded as a feedback memory with the fields {trigger, misread, actual_intent, violated_rule: "[RNN Name]", prevention} [R14 Correction Capture].
  4. Verify: Glob .claude/memories/*.md + Read MEMORY.md confirms both stores
  5. Checkpoint: recovery points + progress tracking
  6. Validate: data integrity + no duplicates across stores
  7. Session Goal: if session goal set via /sc:load, evaluate completion status (done/partial/deferred)
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
    Branch slug: `git branch --show-current` with `/` → `-`; detached HEAD → `detached-<short sha>`. Session records are add-only per branch, so parallel branches and worktrees never conflict on merge
    Auto memory (supplementary): ~/.claude/projects/{project}/memory/MEMORY.md (CC-native, per-project, first 200 lines auto-load)
    Topic files: ~/.claude/projects/{project}/memory/{topic}.md (linked from MEMORY.md, load on demand)
    Agent memory: .claude/agent-memory/{name}/MEMORY.md (project-scoped, per-agent)
  </storage>

  <outputs note="Per --type flag">
| Type | Memory folder | Auto Memory | Content |
|---|---|---|---|
| session | session_[date]_[branch-slug] | MEMORY.md | Full context |
| learnings | learnings_[topic] | topic files | Patterns + insights |
| context | context_[project] | MEMORY.md | Project state |
| all | All above | All above | Complete preservation |
  </outputs>


  <tools>
  - Write/Edit: memory folder + auto memory persistence
  - Glob: list memory files
  - Read: verify both stores
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
  - no-ephemeral: auto memory (MEMORY.md, topic files) keeps only what a later session on any branch needs; this session's progress and next actions belong in the session_ file.
  - verify-value: before saving, ask "Will this be useful in future conversation?" If no, skip
  </gotchas>

  <bounds>
    <does>memory folder + auto memory sync, checkpoints when --checkpoint is given, discovery preservation.</does>
    <never>saves without validation, overrides without a checkpoint, or duplicates content across stores.</never>
    <fallback>Memory folder not writable: auto memory only, and tell the user. Ask the user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:load /sc:reflect"/>
</component>