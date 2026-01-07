---
description: Interactive requirements discovery through Socratic dialogue and systematic exploration
---
<component name="brainstorm" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

  <role>
    /sc:brainstorm
    <mission>Interactive requirements discovery through Socratic dialogue and systematic exploration</mission>
  </role>

  <syntax>/sc:brainstorm [topic/idea] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]</syntax>

  <triggers>
    - Ambiguous project ideas
    - Requirements discovery needs
    - Concept validation requests
    - Cross-session refinement
  </triggers>

  <flow>
    1. Explore: Socratic dialogue + systematic questioning
    2. Analyze: Multi-persona coordination + domain expertise
    3. Validate: Feasibility assessment + requirement validation
    4. Specify: Concrete specs + cross-session persistence
    5. Handoff: Actionable briefs for implementation
  </flow>

  <mcp servers="seq:reasoning|c7:patterns|magic:UI|play:UX|morph:analysis|serena:persistence"/>
  <personas p="arch|anal|fe|be|sec|ops|pm"/>

  <tools>
    - Read/Write/Edit: Requirements docs + spec generation
    - TodoWrite: Multi-phase exploration tracking
    - Task: Parallel exploration + multi-agent
    - WebSearch: Market research + tech validation
    - sequentialthinking: Requirements analysis
  </tools>

  <patterns>
    - Socratic: Question-driven → systematic discovery
    - Multi-Domain: Cross-functional → comprehensive feasibility
    - Progressive: Systematic → iterative refinement
    - Specification: Concrete requirements → actionable briefs
  </patterns>

  <examples>
| Input | Output |
|-------|--------|
| `'AI project management tool' --strategy systematic --depth deep` | Multi-persona deep analysis |
| `'real-time collaboration' --strategy agile --parallel` | Parallel FE/BE/Sec exploration |
| `'enterprise data analytics' --strategy enterprise --validate` | Compliance + validation |
| `'mobile monetization' --depth normal` | Cross-session with Serena |
  </examples>

  <bounds will="ambiguous→concrete|multi-persona+MCP|cross-session persistence" wont="impl without discovery|override user vision|bypass systematic exploration"/>
</component>
