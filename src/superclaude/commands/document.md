---
description: Generate focused docs for components, functions, APIs and features; `--type inline` writes docstrings into source files. On request only — the user's /sc:document or a workflow step that names it. Not for one docstring, comment or README line — edit directly.
---
<component name="document" type="command">

  <role command="/sc:document">
    <mission>Generate focused docs for components, functions, APIs and features</mission>
  </role>

  <syntax>/sc:document [target] [--type inline|external|api|guide] [--style brief|detailed]</syntax>

  <flow>
  1. Analyze: read the component structure and its interfaces.
  2. Identify: name the audience and what it needs.
  3. Generate: write content by type and style (see outputs).
  4. Format: apply a consistent structure.
  5. Integrate: link the result into the project's existing docs.
  </flow>

  <flags>
  - --type inline|external|api|guide: doc kind; output and metrics per type in the outputs table.
  - --style brief|detailed: brief: purpose and usage only; detailed: adds parameters, return values, errors and examples.
  </flags>

  <outputs note="Per --type flag">
| Type | Output | Metrics |
|---|---|---|
| inline | JSDoc/docstring in source files | documented public symbols / total public symbols, both counted |
| external | `docs/reports/<COMPONENT>_DOCS.md` (living doc, per-component) | documented public APIs / total public APIs, both counted |
| api | `docs/reports/API.md` (living doc, project-wide; shared with /sc:index --type api, so an existing file is updated in place) | documented endpoints / total endpoints, both counted |
| guide | `docs/reports/<TOPIC>_GUIDE.md` (living doc, per-topic) | install+usage+examples |
  </outputs>


  <tools>
  - Read: Component + existing docs
  - Grep: Ref extraction
  - Write: Doc file creation
  - Edit: inline docstrings + in-place updates of existing docs
  - Glob: Multi-file organization
  </tools>

  <examples>

| Input | Output |
|---|---|
| `src/auth/login.js --type inline` | JSDoc comments |
| `src/api --type api --style detailed` | API reference |
| `payment-module --type guide --style brief` | User docs |
| `components/ --type external` | Component library docs |

  <example name="document-unstable-code" type="error-path">
    - Input: /sc:document src/api --type api --style detailed (during active refactoring)
    - Why wrong: documenting code mid-refactor leaves the docs stale immediately.
    - Correct: finish the refactor first, then run /sc:document on the stable API surface.
  </example>

  </examples>


  <gotchas>
  - no-unsolicited: create a doc file only for the --type the user asked for; never add extra doc files.
  - naming: Follow doc_output_convention from core/rules/RULES_DOCS.md — file outputs are living docs (UPPER_SNAKE in docs/reports/, no date/username)
  </gotchas>

  <bounds>
    <does>writes focused docs in several formats and links them into the project's docs.</does>
    <never>documents without analysis, overrides project doc standards, or exposes sensitive details.</never>
  </bounds>

  <handoff next="/sc:implement /sc:improve"/>
</component>