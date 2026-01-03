---
name: abbreviations
type: reference
cache: pinned
triggers: [abbr, abbreviation, shorthand, alias, mapping]
---
<component name="abbreviations" type="core" priority="medium">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <triggers>abbr|abbreviation|shorthand|alias|mapping|c7|seq|play|arch|fe|be</triggers>

  <role>
    <mission>Canonical abbreviation mappings for MCP servers and agent personas</mission>
    <note>Used in `<mcp servers="..."/>` and `<personas p="..."/>` declarations</note>
  </role>

  <mcp_abbreviations>
| Abbr | Full Name | File | Triggers |
|------|-----------|------|----------|
| c7 | Context7 | MCP_Context7.md | library, docs, framework, import |
| seq | Sequential | MCP_Sequential.md | think, debug, architecture, reasoning |
| play | Playwright | MCP_Playwright.md | browser, E2E, test, screenshot |
| magic | Magic | MCP_Magic.md | UI, component, form, modal |
| morph | Morphllm | MCP_Morphllm.md | pattern, bulk, transform, style |
| serena | Serena | MCP_Serena.md | symbol, rename, memory, LSP |
| tavily | Tavily | MCP_Tavily.md | search, research, news, web |
| chrome | Chrome DevTools | MCP_Chrome-DevTools.md | performance, debug, layout, CLS |
| airis | Airis Agent | MCP_Airis-Agent.md | confidence, index, optimize |
| mindbase | Mindbase | MCP_Mindbase.md | memory, conversation, embedding |
  </mcp_abbreviations>

  <mcp_usage>
```xml
<!-- Command file example -->
<mcp servers="c7:patterns|seq:analysis|play:testing"/>

<!-- Interpretation -->
<!-- c7:patterns → Use Context7 for pattern lookup -->
<!-- seq:analysis → Use Sequential for analysis -->
<!-- play:testing → Use Playwright for testing -->
```
  </mcp_usage>

  <persona_abbreviations>
| Abbr | Full Name | Agent File | Domain |
|------|-----------|------------|--------|
| arch | System Architect | system-architect.md | Architecture, scalability, boundaries |
| fe | Frontend Architect | frontend-architect.md | UI, accessibility, React/Vue |
| be | Backend Architect | backend-architect.md | API, database, security |
| sec | Security Engineer | security-engineer.md | OWASP, vulnerabilities, compliance |
| qa | Quality Engineer | quality-engineer.md | Testing, coverage, edge cases |
| qual | Quality Engineer | quality-engineer.md | (alias for qa) |
| ops | DevOps Architect | devops-architect.md | CI/CD, Kubernetes, Terraform |
| pm | PM Agent | pm-agent.md | Orchestration, documentation |
| anal | Requirements Analyst | requirements-analyst.md | PRD, scope, stakeholders |
| perf | Performance Engineer | performance-engineer.md | Optimization, profiling, metrics |
| educator | Learning Guide | learning-guide.md | Teaching, tutorials, concepts |
| scribe | Technical Writer | technical-writer.md | Documentation, API docs |
| mentor | Socratic Mentor | socratic-mentor.md | Discovery learning, patterns |
| refactor | Refactoring Expert | refactoring-expert.md | Tech debt, SOLID, simplify |
| root | Root Cause Analyst | root-cause-analyst.md | Debug, hypothesis, evidence |
  </persona_abbreviations>

  <persona_usage>
```xml
<!-- Command file example -->
<personas p="arch|fe|be|sec|qa"/>

<!-- Interpretation -->
<!-- Multi-persona activation for comprehensive coverage -->
<!-- arch: System design perspective -->
<!-- fe: Frontend implementation -->
<!-- be: Backend implementation -->
<!-- sec: Security review -->
<!-- qa: Quality assurance -->
```
  </persona_usage>

  <flag_abbreviations>
| Abbr | Full Flag | Effect |
|------|-----------|--------|
| --uc | --ultracompressed | Token efficiency mode, 30-50% reduction |
| --bs | --brainstorm | Collaborative discovery mode |
| --c7 | --context7 | Enable Context7 MCP |
| --seq | --sequential | Enable Sequential MCP |
| --play | --playwright | Enable Playwright MCP |
| --morph | --morphllm | Enable Morphllm MCP |
  </flag_abbreviations>

  <role_abbreviations note="Used in <mcp servers='abbr:role'/>">
| Role | Meaning |
|------|---------|
| patterns | Pattern lookup, best practices |
| analysis | Deep analysis, reasoning |
| testing | Test execution, validation |
| UI | Component generation |
| transform | Bulk edits, pattern replacement |
| memory | Session persistence |
| persistence | Cross-session storage |
| search | Web search, discovery |
| reasoning | Complex multi-step thinking |
| extraction | Content extraction from URLs |
| semantic | Symbol-level operations |
| reflection | Self-check, validation |
| benchmarks | Performance comparison |
| coordination | Multi-agent orchestration |
  </role_abbreviations>

  <priority_rules>
- Explicit > Implicit: User-specified abbreviations override auto-detection
- Specificity: Longer matches take precedence (c7:patterns > c7)
- Order: First declaration wins when ambiguous
  </priority_rules>

  <examples>
| Declaration | Expands To |
|-------------|------------|
| `c7:patterns` | Context7 for pattern lookup |
| `seq:analysis` | Sequential for deep analysis |
| `play:e2e` | Playwright for E2E testing |
| `serena:memory` | Serena for session persistence |
| `tavily:search` | Tavily for web search |
| `arch\|fe\|sec` | system-architect + frontend-architect + security-engineer |
| `pm-agent` | Full PM Agent orchestration |
  </examples>
</component>
