---
description: Repo index, 94% token cut (58K→3K). Use ONLY when user type `/sc:index-repo` — make compact PROJECT_INDEX briefing for token-cheap navigation. NOT auto-fire on routine code look or "what in repo?" — use Glob/Grep/Serena overview direct.
---
<component name="index-repo" type="command">

  <role command="/sc:index-repo">
    <mission>Repo index, 94% token cut (58K→3K)</mission>
  </role>

  <syntax>/sc:index-repo [mode=create|update|quick]</syntax>

  <flow>
  1. Detect: project type from entry files (pyproject.toml, package.json, etc.)
  2. Analyze: auto-find structure (parallel Glob code|docs|tests|config)
  3. Extract: entry points + modules + APIs + deps
  4. Generate: docs/reports/PROJECT_INDEX.md (human summary)
  5. Generate: docs/reports/PROJECT_INDEX.json (machine, full detail)
  6. Validate: both files exist + size <5KB each
  </flow>


  <tools>
  - Glob: parallel structure scan (code|docs|config|tests|scripts)
  - Read: pull metadata
  - Write: make index
  </tools>

  <patterns>
    - Structure: auto-find from root
      1. Entry: pyproject.toml | package.json | Cargo.toml | go.mod | *.csproj
      2. Source: Glob code dirs (src/ | lib/ | app/ | cmd/)
      3. Docs: **/*.md | docs/
      4. Tests: tests/ | test/ | __tests__/ | *_test.*
      5. Config: *.toml | *.json | *.yaml | *.yml
    - Output:
      - docs/reports/PROJECT_INDEX.md: ~3KB, human, quick ref
      - docs/reports/PROJECT_INDEX.json: ~10KB, machine, full metadata
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
|---|---|
| `/index-repo` | make full index |
| `mode=update` | update existing |
| `mode=quick` | skip tests |

  <example name="index-outside-repo" type="error-path">
    - Input: /sc:index-repo (run outside a git repo)
    - Why wrong: Repo index need git repo for structure scan + change detect.
    - Correct: Go to git repo first, or use /sc:index for non-repo dir.
  </example>
  </examples>


  <gotchas>
  - token-target: Aim 94% cut (58K→3K). No verbose index
  - structure-only: Output file structure + role, not content
  </gotchas>

  <bounds>
    <does>94% token cut, parallel scan, human output.</does>
    <never>modify source, exceed 5KB.</never>
    <fallback>Ask user when unsure.</fallback>
  </bounds>

  <handoff next="/sc:analyze /sc:index"/>
</component>