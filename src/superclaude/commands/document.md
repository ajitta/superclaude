---
description: Gen focused docs for components, functions, APIs, features. Use when user types `/sc:document` or ask for structured docs (API reference, README section, feature guide) with target audience + template. NOT auto-trigger on add single docstring, fix comment typo, or update one README line — those direct edits.
---
<component name="document" type="command">

  <role command="/sc:document">
    <mission>Gen focused docs for components, functions, APIs, features</mission>
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
|---|---|---|
| inline | JSDoc/docstring in source files | coverage ≥80% |
| external | `docs/<component>-docs.md` (per-component) | all public APIs |
| api | `docs/reports/API.md` (living doc, project-wide) | endpoints 100% |
| guide | `docs/<topic>-guide.md` (per-topic) | install+usage+examples |
  </outputs>


  <tools>
  - Read: Component + existing docs
  - Grep: Ref extraction
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
|---|---|
| `src/auth/login.js --type inline` | JSDoc comments |
| `src/api --type api --style detailed` | API reference |
| `payment-module --type guide --style brief` | User docs |
| `components/ --type external` | Component library docs |

  <example name="document-unstable-code" type="error-path">
    - Input: /sc:document src/api --type api --detailed (during active refactoring)
    - Why wrong: Doc code mid-refactor → docs stale immediately.
    - Correct: Finish refactor first, then /sc:document for stable API surface.
  </example>

  </examples>


  <gotchas>
  - no-unsolicited: No create doc files unless explicit request
  - naming: Follow doc_output_convention from RULES.md for file naming (topic-slug-username-date.md)
  </gotchas>

  <bounds>
    <does>focused docs, multi-format, ecosystem integration.</does>
    <never>doc w/o analysis, override standards, expose sensitive details.</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:implement /sc:improve"/>
</component>