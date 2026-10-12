---
description: Session lifecycle management with a committed project memory folder (`.claude/memories/`) + Claude auto memory for context persistence. Use ONLY when user explicitly types `/sc:save` — session-end lifecycle action that writes memory files and auto-memory entries. Do NOT auto-trigger on "save this", "remember this", or end-of-task completions.
---
<component name="save" type="command">

  <role command="/sc:save">
    <mission>Session lifecycle management with a committed project memory folder + Claude auto memory for context persistence</mission>
  </role>

  <syntax>/sc:save [--type session|learnings|context|all] [--summarize] [--checkpoint]</syntax>

  <flow>
  1. Analyze: session progress + discoveries
  2. Persist (memory folder): Write .claude/memories/session_[date].md (context) → .claude/memories/learnings_[topic].md (insights) → overwrite .claude/memories/last_session.md (this session's summary) and .claude/memories/next_actions.md (open items); flat basename only, no path segments; create the folder when absent
  3. Persist (auto memory): Write/Edit MEMORY.md + topic files for cross-session continuity
    3.5. Corrections-Review: capture unrecorded user corrections per the /sc:reflect Misunderstanding-Audit step (same feedback-memory fields).
  4. Verify: Glob .claude/memories/ + Read MEMORY.md confirms both stores
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
    Auto memory (supplementary): ~/.claude/projects/{project}/memory/MEMORY.md (CC-native, per-project, first 200 lines auto-load)
    Topic files: ~/.claude/projects/{project}/memory/{topic}.md (linked from MEMORY.md, load on demand)
    Agent memory: .claude/agent-memory/{name}/MEMORY.md (project-scoped, per-agent)
  </storage>

  <outputs note="Per --type flag">
| Type | Memory folder | Auto Memory | Content |
|---|---|---|---|
| session | session_[date], last_session, next_actions | MEMORY.md | Full context |
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
| `/sc:save` | Auto-checkpoint if >30min session |
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
  - no-ephemeral: do not save current-conversation task details as persistent memory
  - verify-value: before saving, ask "Will this be useful in future conversation?" If no, skip
  </gotchas>

  <bounds>
    <does>memory folder + auto memory sync, auto-checkpoints, discovery preservation.</does>
    <never>save without validation, override without checkpoint, duplicate across stores.</never>
    <fallback>Memory folder not writable: auto memory only, and tell the user. Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:load /sc:reflect"/>
</component>