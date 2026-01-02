---
description: Session lifecycle management with Serena MCP integration for context persistence
---
<component name="save" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5"/>

  <role>
    /sc:save
    <mission>Session lifecycle management with Serena MCP integration for context persistence</mission>
  </role>

  <syntax>/sc:save [--type session|learnings|context|all] [--summarize] [--checkpoint]</syntax>

  <triggers>
    - Session completion
    - Cross-session memory management
    - Discovery preservation
    - Progress tracking
  </triggers>

  <flow>
    1. Analyze: Session progress + discoveries
    2. Persist: Context + learnings (Serena memory)
    3. Checkpoint: Recovery points + progress tracking
    4. Validate: Data integrity + compatibility
    5. Prepare: Ready for future session continuation
  </flow>

  <mcp servers="serena:memory|serena:persistence"/>

  <tools>
    - write_memory/read_memory: Session context persistence
    - think_about_collected_information: Discovery identification
    - summarize_changes: Progress documentation
    - TodoRead: Auto checkpoint triggers
  </tools>

  <patterns>
    - Preservation: Discovery → memory → checkpoint
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

  </examples>

  <bounds will="Serena integration|auto-checkpoints|discovery preservation" wont="operate without Serena|save without validation|override without checkpoint"/>
</component>
