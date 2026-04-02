---
description: Repository indexing with 94% token reduction (58K → 3K)
---
<component name="index-repo" type="command">

  <role>
    /sc:index-repo
    <mission>Repository indexing with 94% token reduction (58K → 3K)</mission>
  </role>

  <syntax>/sc:index-repo [mode=create|update|quick]</syntax>

  <flow>
    1. Detect: Project type from entry files (pyproject.toml, package.json, etc.)
    2. Analyze: Auto-discover structure (parallel Glob for code|docs|tests|config)
    3. Extract: Entry points + modules + APIs + deps
    4. Generate: docs/reports/PROJECT_INDEX.md (human-readable summary)
    5. Generate: docs/reports/PROJECT_INDEX.json (machine-readable, detailed)
    6. Validate: Both files exist + size <5KB each
  </flow>


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
      - docs/reports/PROJECT_INDEX.md: ~3KB, human-readable, quick reference
      - docs/reports/PROJECT_INDEX.json: ~10KB, machine-readable, full metadata
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

  <example name="index-outside-repo" type="error-path">
    <input>/sc:index-repo (run outside a git repository)</input>
    <why_wrong>Repository indexing requires a git repo for structure analysis and change detection.</why_wrong>
    <correct>Navigate to a git repo first, or use /sc:index for non-repo directories.</correct>
  </example>
  </examples>

  <bounds will="94% token reduction|parallel analysis|human-readable output" wont="modify source|exceed 5KB" fallback="Ask user for guidance when uncertain" type="document-only">

    Generate docs/reports/PROJECT_INDEX.md and docs/reports/PROJECT_INDEX.json, then complete | Preserve source code unchanged | Defer implementation to /sc:implement → Output: docs/reports/PROJECT_INDEX.md (~3KB) + docs/reports/PROJECT_INDEX.json

  </bounds>

  <handoff next="/sc:analyze /sc:index"/>
</component>
