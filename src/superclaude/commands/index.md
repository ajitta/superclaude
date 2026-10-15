---
description: Generate project documentation and a knowledge base under docs/reports/. On request only — the user's /sc:index or a workflow step that names it. Not for documenting one file — use /sc:document or edit directly.
---
<component name="index" type="command">

  <role command="/sc:index">
    <mission>Generate project documentation and a knowledge base under docs/reports/</mission>
  </role>

  <syntax>/sc:index [target] [--type docs|api|structure|readme] [--format md|json|yaml]</syntax>

  <flow>
  1. Analyze: read the project structure and key components.
  2. Organize: group content by component and add cross-references.
  3. Generate: write type-specific documentation (see outputs).
  4. Validate: check completeness against the metric for the type.
  5. Maintain: preserve sections marked <!-- MANUAL -->.
  </flow>

  <flags>
  - --type docs|api|structure|readme: output file and metrics per type, in the outputs table.
  - --format md|json|yaml: md writes the files in the outputs table; json or yaml writes the same stem with that extension (e.g. docs/reports/API.json).
  </flags>

  <outputs note="Per --type flag">
| Type | Output File | Metrics |
|---|---|---|
| docs | docs/reports/KNOWLEDGE.md | documented modules / total modules, both counted |
| api | docs/reports/API.md; if it exists (e.g. from /sc:document --type api), update the endpoint list in place | documented endpoints / total endpoints, both counted |
| structure | docs/reports/STRUCTURE.md | depth ≤4 levels |
| readme | README.md; in an existing README edit only the install, usage and api sections and show the diff | sections: install, usage, api |
  </outputs>

  <distinction note="vs /sc:index-repo">
    - index-repo: Minimal index (~3KB), token-efficient, PROJECT_INDEX.*
    - index: Comprehensive docs, full coverage, type-specific files
  </distinction>


  <tools>
  - Read/Grep/Glob: Structure analysis + content extraction
  - Write: Doc creation + cross-referencing
  - Edit: in-place updates of an existing API.md or README.md
  - TaskCreate/TaskUpdate: Multi-component progress
  - Agent: Large-scale doc delegation
  </tools>

  <examples>

| Input | Output |
|---|---|
| `project-root --type structure --format md` | Navigable structure docs |
| `src/api --type api --format json` | API docs + validation |
| `. --type docs` | Knowledge base creation |

  <example name="index-huge-monorepo" type="error-path">
    - Input: /sc:index . --type structure (in 10,000+ file monorepo)
    - Why wrong: Indexing entire large monorepo in one pass exhausts context. Index specific packages instead.
    - Correct: /sc:index packages/auth --type structure or /sc:index-repo for token-efficient full indexing
  </example>

  </examples>


  <gotchas>
  - living-doc: Index output uses UPPER_SNAKE naming in docs/reports/ (no date/username)
  - token-budget: Use structural reading, not full file reads. Keep index compact
  </gotchas>

  <bounds>
    <does>writes project docs per type, delegates large indexes to agents, follows the project's framework patterns.</does>
    <never>override manual docs, generate without analysis, bypass standards.</never>
  </bounds>

  <handoff next="/sc:implement /sc:improve"/>
</component>