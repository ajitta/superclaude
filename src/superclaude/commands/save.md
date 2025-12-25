---
description: Session lifecycle management with Serena MCP integration for context persistence
---
<component name="save" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="low"/>

  <role>
    /sc:save
    <mission>Session lifecycle management with Serena MCP integration for context persistence</mission>
  </role>

  <syntax>/sc:save [--type session|learnings|context|all] [--summarize] [--checkpoint]</syntax>

  <triggers>
    <t>Session completion</t>
    <t>Cross-session memory management</t>
    <t>Discovery preservation</t>
    <t>Progress tracking</t>
  </triggers>

  <flow>
    <s n="1">Analyze: Session progress + discoveries</s>
    <s n="2">Persist: Context + learnings (Serena memory)</s>
    <s n="3">Checkpoint: Recovery points + progress tracking</s>
    <s n="4">Validate: Data integrity + compatibility</s>
    <s n="5">Prepare: Ready for future session continuation</s>
  </flow>

  <mcp servers="serena:memory|serena:persistence"/>

  <tools>
    <t n="write_memory/read_memory">Session context persistence</t>
    <t n="think_about_collected_information">Discovery identification</t>
    <t n="summarize_changes">Progress documentation</t>
    <t n="TodoRead">Auto checkpoint triggers</t>
  </tools>

  <patterns>
    <p n="Preservation">Discovery → memory → checkpoint</p>
    <p n="Learning">Accumulation → archival → understanding</p>
    <p n="Progress">Completion → auto-checkpoint → continuity</p>
    <p n="Recovery">State → validation → restoration ready</p>
  </patterns>

  <examples>
    <ex i="/sc:save" o="Auto-checkpoint if >30min session"/>
    <ex i="--type all --checkpoint" o="Complete preservation + recovery"/>
    <ex i="--summarize" o="Summary + learning patterns"/>
    <ex i="--type learnings" o="Patterns + insights only"/>
  </examples>

  <bounds will="Serena integration|auto-checkpoints|discovery preservation" wont="operate without Serena|save without validation|override without checkpoint"/>
</component>
