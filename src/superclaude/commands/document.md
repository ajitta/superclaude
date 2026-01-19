---
description: Generate focused documentation for components, functions, APIs, and features
---
<component name="document" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

  <role>
    /sc:document
    <mission>Generate focused documentation for components, functions, APIs, and features</mission>
  </role>

  <syntax>/sc:document [target] [--type inline|external|api|guide] [--style brief|detailed]</syntax>

  <triggers>
    - Component/function documentation
    - API reference generation
    - Code comments + inline docs
    - User guides + technical docs
  </triggers>

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

  <checklist note="SHOULD complete all">
    - [ ] Target documentation generated
    - [ ] Format matches --style (brief/detailed)
    - [ ] Cross-references validated
    - [ ] Integrated with existing docs
  </checklist>

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
| `src/api --type api --detailed` | API reference |
| `payment-module --type guide --brief` | User docs |
| `components/ --type external` | Component library docs |

  </examples>

  <bounds will="focused docs|multi-format|ecosystem integration" wont="doc without analysis|override standards|expose sensitive details"/>

  <boundaries type="document-only" critical="true">
    <rule>STOP after producing documentation</rule>
    <rule>DO NOT modify source code (except inline comments if --type inline)</rule>
    <rule>DO NOT implement features based on documented gaps</rule>
    <output>Documentation files per --type flag</output>
  </boundaries>

  <handoff>
    <next command="/sc:implement">For implementing documented features</next>
    <next command="/sc:improve">For addressing documentation gaps</next>
    <format>Provide documentation context for implementation</format>
  </handoff>
</component>
