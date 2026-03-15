---
name: using-superclaude
description: |
  Meta-skill for discovering and using superclaude features. Loaded at session
  start. Covers SC commands (/sc:*), agents, skills, and core configuration
  (FLAGS, PRINCIPLES, RULES).
---
<component name="using-superclaude" type="skill">

  <role>
    <mission>Orient the user and model to superclaude's available features and how to invoke them</mission>
  </role>

  <features>
**Commands** — Quick actions invoked as `/sc:<name>`. Use `/sc:help` for the full listing.
**Agents** — Specialized personas with defined models, permissions, and tool access. Defined in `~/.claude/agents/`.
**Skills** — Structured process workflows invoked via the Skill tool in Claude Code. Defined in `~/.claude/skills/`.
**Core config** — `FLAGS.md` (behavioral modes and MCP flags), `PRINCIPLES.md` (decision frameworks), `RULES.md` (behavioral rules and workflow gates). Located in `~/.claude/superclaude/core/`.
  </features>

  <flow>
    1. Check for applicable skills before responding — match the current task against available skills by name and description
    2. Invoke matching skills using the Skill tool — process skills before implementation skills, implementation before quality skills
    3. Use SC commands for quick actions that do not require a full skill workflow
    4. Follow core config for behavioral modes (FLAGS), decision frameworks (PRINCIPLES), and workflow rules (RULES)
  </flow>

  <instruction_priority>
    1. User's explicit instructions (highest — always wins)
    2. superclaude skills (process workflows, domain knowledge)
    3. superclaude commands (/sc:* quick actions)
    4. Default system prompt (lowest — yields to the above)
  </instruction_priority>

  <bounds will="feature discovery|skill invocation guidance|instruction priority resolution" wont="modify code|execute workflows directly|override user instructions"/>

  <handoff next="/sc:help /sc:recommend"/>
</component>
