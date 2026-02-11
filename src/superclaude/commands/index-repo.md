---
description: Repository indexing with 94% token reduction (58K → 3K)
---
<component name="index-repo" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

  <role>
    /sc:index-repo
    <mission>Repository indexing with 94% token reduction (58K → 3K)</mission>
  </role>

  <syntax>/sc:index-repo [mode=create|update|quick]</syntax>

  <triggers>repository indexing|token reduction|project structure docs</triggers>

  <flow>
    1. Detect: Project type from entry files (pyproject.toml, package.json, etc.)
    2. Analyze: Auto-discover structure (parallel Glob for code|docs|tests|config)
    3. Extract: Entry points + modules + APIs + deps
    4. Generate: PROJECT_INDEX.md (human-readable summary)
    5. Generate: PROJECT_INDEX.json (machine-readable, detailed)
    6. Validate: Both files exist + size <5KB each
  </flow>

  <checklist note="Completion criteria">
    - [ ] PROJECT_INDEX.md created/updated (confirm file exists)
    - [ ] PROJECT_INDEX.json created/updated (confirm file exists)
    - [ ] Both files validated for completeness (check size <5KB)
    - [ ] Statistics synced between .md and .json (compare counts)
  </checklist>

  <tools>
    - Glob: Parallel structure scan (code|docs|config|tests|scripts)
    - Read: Metadata extraction
    - Write: Index generation
  </tools>

  <patterns>
    - Structure: Auto-detect from project root
      1. Entry: pyproject.toml | package.json | Cargo.toml | go.mod | *.csproj
      2. Source: Glob for code dirs (src/ | lib/ | app/ | cmd/)
      3. Docs: **/*.md | docs/
      4. Tests: tests/ | test/ | __tests__/ | *_test.*
      5. Config: *.toml | *.json | *.yaml | *.yml
    - Output:
      - PROJECT_INDEX.md: ~3KB, human-readable, quick reference
      - PROJECT_INDEX.json: ~10KB, machine-readable, full metadata
  </patterns>

  <roi>
    - creation: 2K tokens (one-time)
    - reading: 3K tokens (per session)
    - full-read: 58K tokens (per session)
    - breakeven: 1 session
    - 10-sessions: 550K tokens saved
  </roi>

  <examples>

| Input | Output |
|-------|--------|
| `/index-repo` | Create full index |
| `mode=update` | Update existing |
| `mode=quick` | Skip tests |

  </examples>

  <bounds will="94% token reduction|parallel analysis|human-readable output" wont="modify source|exceed 5KB" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="document-only" critical="true">
    <rule>Generate PROJECT_INDEX.md and PROJECT_INDEX.json, then complete</rule>
    <rule>Preserve source code unchanged</rule>
    <rule>Defer implementation to /sc:implement</rule>
    <output>PROJECT_INDEX.md (~3KB) + PROJECT_INDEX.json</output>
  </boundaries>

  <handoff>
    <next command="/sc:analyze">For detailed codebase analysis</next>
    <next command="/sc:index">For comprehensive documentation</next>
    <format>Index provides entry point for deeper exploration</format>
  </handoff>
</component>
