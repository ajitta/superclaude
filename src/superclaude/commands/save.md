---
description: Session lifecycle management with Serena MCP + Claude auto memory for context persistence. Use ONLY when user explicitly types `/sc:save` — session-end lifecycle action that writes Serena memories and auto-memory entries. Do NOT auto-trigger on "save this", "remember this", or end-of-task completions.
---
<component name="save" type="command">

  <role command="/sc:save">
    <mission>Session lifecycle management with Serena MCP + Claude auto memory for context persistence</mission>
  </role>

  <syntax>/sc:save [--type session|learnings|context|all] [--summarize] [--checkpoint]</syntax>

  <flow>
  1. Analyze: session progress + discoveries
  2. Persist (Serena): write_memory("session_[date]", context) → write_memory("learnings_[topic]", insights)
  3. Persist (auto memory): Write/Edit MEMORY.md + topic files for cross-session continuity
    3.5. Corrections-Review: scan session for user corrections (rejected approaches, "no I meant...", redirections). For each unrecorded correction, save structured feedback memory with trigger/misread/actual_intent/prevention fields.
  4. Verify: list_memories() + Read MEMORY.md confirms both stores
  5. Checkpoint: recovery points + progress tracking
  6. Validate: data integrity + no duplicates across stores
  7. Session Goal: if session goal set via /sc:load, evaluate completion status (done/partial/deferred)
    Fallback (no Serena): Claude auto memory only (MEMORY.md + topic files)
  </flow>

  <compaction_strategy>
  Preserve (high signal): architecture decisions + rationale, unresolved issues, key patterns discovered, session goal status
  Discard (low signal): verbatim tool output, intermediate search results, committed diffs, duplicate context
  Format: structured summary (decisions, todo, context pointers) — not narrative prose
  </compaction_strategy>

  <storage>
    Serena (primary): .serena/memories/ — semantic project memories, symbol-aware context
    Auto memory (supplementary): .claude/memory/MEMORY.md (project-scoped, committable, max 200 lines)
    Topic files: .claude/memory/{topic}.md (linked from MEMORY.md)
    Agent memory: .claude/agent-memory/{name}/MEMORY.md (project-scoped, per-agent)
  </storage>

  <outputs note="Per --type flag">
| Type | Serena Memory | Auto Memory | Content |
|---|---|---|---|
| session | session_[date] | MEMORY.md | Full context |
| learnings | learnings_[topic] | topic files | Patterns + insights |
| context | context_[project] | MEMORY.md | Project state |
| all | All above | All above | Complete preservation |
  </outputs>


  <tools>
  - write_memory/read_memory: Serena semantic persistence (primary)
  - list_memories: verify Serena memories
  - Write/Edit: Claude auto memory persistence (supplementary)
  - Read: verify auto memory content
  </tools>

  <patterns>
    - Preservation: Discovery → Serena memory → auto memory → checkpoint
    - Learning: Accumulation → archival → understanding
    - Progress: Completion → auto-checkpoint → continuity
    - Recovery: State → validation → restoration ready
  </patterns>

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
    <does>Serena integration, auto memory sync, auto-checkpoints, discovery preservation.</does>
    <never>save without validation, override without checkpoint, duplicate across stores.</never>
    <fallback>Without Serena: use Claude auto memory only (Write/Edit MEMORY.md). Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:load /sc:reflect"/>
</component>