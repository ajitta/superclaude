---
description: Generate focused documentation for components, functions, APIs, and features
---
<component name="document" type="command">

  <role>
    /sc:document
    <mission>Generate focused documentation for components, functions, APIs, and features</mission>
  </role>

  <syntax>/sc:document [target] [--type inline|external|api|guide] [--style brief|detailed]</syntax>

  <flow>
    1. Analyze: Component structure + interfaces
    2. Identify: Audience + requirements
    3. Generate: Content by type + style (see outputs)
    4. Format: Consistent structure
    5. Integrate: Project doc ecosystem
  </flow>

  <outputs note="Per --type flag">
| Type | Output | Metrics |
|------|--------|---------|
| inline | JSDoc/docstring in source | coverage ≥80% |
| external | {component}_DOCS.md | all public APIs |
| api | API.md or api.json | endpoints 100% |
| guide | GUIDE.md | install+usage+examples |
  </outputs>


  <tools>
    - Read: Component + existing docs
    - Grep: Reference extraction
    - Write: Doc file creation
    - Glob: Multi-file organization
  </tools>

  <patterns>
    - Inline: Code analysis → JSDoc/docstring
    - API: Interface extraction → reference + examples
    - Guide: Feature analysis → tutorial content
    - External: Overview → specs → integration
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `src/auth/login.js --type inline` | JSDoc comments |
| `src/api --type api --style detailed` | API reference |
| `payment-module --type guide --style brief` | User docs |
| `components/ --type external` | Component library docs |

  <example name="document-unstable-code" type="error-path">
    <input>/sc:document src/api --type api --detailed (during active refactoring)</input>
    <why_wrong>Documenting code that's actively being refactored produces docs that immediately go stale.</why_wrong>
    <correct>Complete the refactoring first, then /sc:document for stable API surface.</correct>
  </example>

  </examples>

  <token_note>Medium consumption — scales with target scope; use --style brief for lighter output</token_note>

  <bounds will="focused docs|multi-format|ecosystem integration" wont="doc without analysis|override standards|expose sensitive details" fallback="Ask user for guidance when uncertain" type="document-only">

    Produce documentation, then complete | Preserve source code (except inline comments if --type inline) | Defer feature implementation to /sc:implement → Output: Documentation files per --type flag

  </bounds>

  <handoff next="/sc:implement /sc:improve"/>
</component>
