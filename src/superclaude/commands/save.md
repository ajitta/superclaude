---
description: Session lifecycle management with Serena MCP + Claude auto memory for context persistence
---
<component name="save" type="command">

  <role>
    /sc:save
    <mission>Session lifecycle management with Serena MCP + Claude auto memory for context persistence</mission>
  </role>

  <syntax>/sc:save [--type session|learnings|context|all] [--summarize] [--checkpoint]</syntax>

  <flow>
    1. Analyze: Session progress + discoveries
    2. Persist (Serena): write_memory("session_[date]", context) → write_memory("learnings_[topic]", insights)
    3. Persist (auto memory): Write/Edit MEMORY.md + topic files for cross-session continuity
    3.5. Corrections-Review: Scan session for user corrections (rejected approaches, "no I meant...", redirections). For each unrecorded correction, save structured feedback memory with trigger/misread/actual_intent/prevention fields.
    4. Verify: list_memories() + Read MEMORY.md to confirm both stores
    5. Checkpoint: Recovery points + progress tracking
    6. Validate: Data integrity + no duplicates across stores
    Fallback (no Serena): Claude auto memory only (MEMORY.md + topic files)
  </flow>

  <storage note="Dual persistence">
    Serena (primary): .serena/memories/ — semantic project memories, symbol-aware context
    Auto memory (supplementary): .claude/memory/MEMORY.md (project-scoped, committable, max 200 lines)
    Topic files: .claude/memory/{topic}.md (linked from MEMORY.md)
    Agent memory: .claude/agent-memory/{name}/MEMORY.md (project-scoped, per-agent)
  </storage>

  <outputs note="Per --type flag">
| Type | Serena Memory | Auto Memory | Content |
|------|---------------|-------------|---------|
| session | session_[date] | MEMORY.md | Full context |
| learnings | learnings_[topic] | topic files | Patterns + insights |
| context | context_[project] | MEMORY.md | Project state |
| all | All above | All above | Complete preservation |
  </outputs>

  <mcp servers="serena"/>

  <tools>
    - write_memory/read_memory: Serena semantic persistence (primary)
    - list_memories: Verify Serena memories
    - Write/Edit: Claude auto memory persistence (supplementary)
    - Read: Verify auto memory content
  </tools>

  <patterns>
    - Preservation: Discovery → Serena memory → auto memory → checkpoint
    - Learning: Accumulation → archival → understanding
    - Progress: Completion → auto-checkpoint → continuity
    - Recovery: State → validation → restoration ready
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `/sc:save` | Auto-checkpoint if >30min session |
| `--type all --checkpoint` | Complete preservation + recovery |
| `--summarize` | Summary + learning patterns |
| `--type learnings` | Patterns + insights only |

  <example name="save-incomplete-work" type="error-path">
    <input>/sc:save --type all --checkpoint (mid-debugging, broken state)</input>
    <why_wrong>Checkpointing a broken state preserves errors. Next session loads broken context.</why_wrong>
    <correct>Reach a stable state first (tests pass or revert), then /sc:save --type all --checkpoint.</correct>
  </example>

  </examples>

  <bounds will="Serena integration|auto memory sync|auto-checkpoints|discovery preservation" wont="save without validation|override without checkpoint|duplicate across stores" fallback="Without Serena: use Claude auto memory only (Write/Edit MEMORY.md). Ask user for guidance when uncertain" type="execution">
    Execute session persistence | Preserve project code unchanged | Validate data integrity before save
  </bounds>

  <handoff next="/sc:load /sc:reflect"/>
</component>
