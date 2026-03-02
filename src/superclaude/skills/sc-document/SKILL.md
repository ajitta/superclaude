---
name: sc-document
description: >-
  This skill should be used when the user asks to
  "document this code",
  "generate API documentation",
  "add docstrings",
  "write a user guide",
  "create component documentation",
  "generate JSDoc comments",
  "document the module",
  "write technical documentation".
version: 1.0.0
metadata:
  context: inline
  agent: technical-writer
  mcp: seq
  allowed-tools:
    - Read
    - Grep
    - Write
    - Glob
---
<component name="sc-document" type="skill">

  <role>
    <mission>Generate focused documentation for components, functions, APIs, and features</mission>
  </role>

  <syntax>/sc:document [target] [--type inline|external|api|guide] [--style brief|detailed]</syntax>

  <flow>
    1. Analyze: Read target code, identify public interfaces, understand component structure
    2. Audience: Determine documentation audience (developers, users, API consumers)
    3. Generate: Create documentation matching --type and --style parameters
    4. Format: Apply consistent structure, cross-reference related components
    5. Integrate: Place documentation in appropriate location within project doc ecosystem
  </flow>

  <doc_types>
| Type | Output | Coverage Target |
|------|--------|----------------|
| inline | JSDoc/docstring in source files | ≥80% of public APIs |
| external | {component}_DOCS.md | All public interfaces |
| api | API.md or openapi.yaml | 100% of endpoints |
| guide | GUIDE.md | Install + usage + examples |
  </doc_types>

  <template_selection note="Auto-select based on target">
| Target Pattern | Template | Style |
|---------------|----------|-------|
| *.py | Python docstrings (Google style) | reStructuredText or Google |
| *.js/*.ts | JSDoc comments | TypeDoc-compatible |
| src/api/ | OpenAPI spec | YAML with examples |
| README.md | Project guide | Markdown with badges |
  </template_selection>

  <patterns>
    - Inline: Parse source → identify undocumented functions/classes → generate docstrings/JSDoc
    - API: Extract route handlers → document parameters, responses, errors → generate spec
    - Guide: Analyze features → write install/setup/usage/examples → organize by audience
    - External: Survey module → document architecture, interfaces, data flow → cross-reference
  </patterns>

  <examples>
| Input | Output |
|-------|--------|
| `src/auth/login.js --type inline` | JSDoc comments for all functions |
| `src/api --type api --style detailed` | Comprehensive API reference |
| `payment-module --type guide --style brief` | Quick-start user guide |
| `components/ --type external` | Component library documentation |
| (auto-trigger) "document this code" | Skill activates, generates appropriate docs |
| (auto-trigger) "add docstrings" | Skill activates, adds inline documentation |

  <example name="document-unstable-code" type="error-path">
    <input>/sc:document src/api --type api --style detailed (during active refactoring)</input>
    <why_wrong>Documenting code that's actively being refactored produces docs that immediately go stale.</why_wrong>
    <correct>Complete the refactoring first, then /sc:document for stable API surface.</correct>
  </example>
  </examples>

  <bounds will="focused documentation|multi-format output|ecosystem integration|template selection" wont="document without reading code|override project doc standards|expose secrets in docs" fallback="Ask user for guidance when documentation scope is unclear"/>

  <handoff next="/sc:implement /sc:improve"/>
</component>
