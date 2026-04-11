---
description: Generate comprehensive project documentation and knowledge base with intelligent organization
---
<component name="index" type="command">

  <role>
    /sc:index
    <mission>Generate comprehensive project documentation and knowledge base with intelligent organization</mission>
  </role>

  <syntax>/sc:index [target] [--type docs|api|structure|readme] [--format md|json|yaml]</syntax>

  <flow>
    1. Analyze: Project structure + key components
    2. Organize: Intelligent patterns + cross-refs
    3. Generate: Type-specific documentation (see outputs)
    4. Validate: Completeness + metrics per type
    5. Maintain: Preserve <!-- MANUAL --> marked sections
  </flow>

  <outputs note="Per --type flag">
| Type | Output File | Metrics |
|------|-------------|---------|
| docs | docs/reports/KNOWLEDGE.md | coverage ≥80% |
| api | docs/reports/API.md | endpoints 100% |
| structure | docs/reports/STRUCTURE.md | depth ≤4 levels |
| readme | README.md | sections: install, usage, api |
  </outputs>

  <distinction note="vs /sc:index-repo">
    - index-repo: Minimal index (~3KB), token-efficient, PROJECT_INDEX.*
    - index: Comprehensive docs, full coverage, type-specific files
  </distinction>


  <tools>
    - Read/Grep/Glob: Structure analysis + content extraction
    - Write: Doc creation + cross-referencing
    - TaskCreate/TaskUpdate: Multi-component progress
    - Task: Large-scale doc delegation
  </tools>

  <patterns>
    - Structure: Examination → component ID → organization → cross-refs
    - Types: API docs | Structure docs | README | Knowledge base
    - Quality: Completeness → accuracy → compliance → maintenance
    - Framework: C7 patterns → official standards → best practices
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `project-root --type structure --format md` | Navigable structure docs |
| `src/api --type api --format json` | API docs + validation |
| `. --type docs` | Knowledge base creation |

  <example name="index-huge-monorepo" type="error-path">
    <input>/sc:index . --type structure (in a 10,000+ file monorepo)</input>
    <why_wrong>Indexing an entire large monorepo in one pass exhausts context. Index specific packages instead.</why_wrong>
    <correct>/sc:index packages/auth --type structure or /sc:index-repo for token-efficient full indexing</correct>
  </example>

  </examples>


  <gotchas>
  - living-doc: Index output uses UPPER_SNAKE naming in docs/reports/ (no date/username)
  - token-budget: Use structural reading, not full file reads. Keep index compact
  </gotchas>

  <bounds should="comprehensive docs|multi-agent|framework patterns" avoid="override manual docs|generate without analysis|bypass standards" fallback="Ask user for guidance when uncertain">

    Generate documentation files, then complete | Preserve source code unchanged | Preserve <!-- MANUAL --> marked sections → Output: Documentation files per --type (docs/reports/KNOWLEDGE.md, docs/reports/API.md, etc.)

  </bounds>

  <handoff next="/sc:implement /sc:improve"/>
</component>
