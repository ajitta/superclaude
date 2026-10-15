---
description: Build a compact PROJECT_INDEX briefing of the repo for token-cheap navigation. On request only — the user's /sc:index-repo or a workflow step that names it. Not for a routine code lookup — use Glob or Grep.
---
<component name="index-repo" type="command">

  <role command="/sc:index-repo">
    <mission>Build a compact repo index (~3KB) for token-cheap navigation</mission>
  </role>

  <syntax>/sc:index-repo [mode=create|update|quick]</syntax>

  <flow>
  1. Detect: project type from entry files (pyproject.toml, package.json, etc.)
  2. Analyze: auto-find structure (parallel Glob code|docs|tests|config)
  3. Extract: entry points + modules + APIs + deps
  4. Generate: docs/reports/PROJECT_INDEX.md (human summary)
  5. Generate: docs/reports/PROJECT_INDEX.json (machine, full detail)
  6. Validate: confirm both files exist and each is under 5KB; report the measured byte size of each.
  </flow>


  <tools>
  - Glob: parallel structure scan (code|docs|config|tests|scripts)
  - Read: pull metadata
  - Write: make index
  - Bash: find the git repo root and files changed since the last index (mode=update)
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
      - docs/reports/PROJECT_INDEX.json: <5KB, machine, full metadata
  </patterns>

  <examples>

| Input | Output |
|---|---|
| `/sc:index-repo` | make full index |
| `mode=update` | update existing |
| `mode=quick` | skip tests |

  <example name="index-outside-repo" type="error-path">
    - Input: /sc:index-repo (run outside a git repo)
    - Why wrong: the repo index needs a git repo for the structure scan and change detection.
    - Correct: move into a git repo first, or use /sc:index for a non-repo directory.
  </example>
  </examples>


  <gotchas>
  - token-target: keep the index compact (~3KB for the .md); report the measured byte size of each file, never a percentage cut.
  - structure-only: output the file structure and each file's role, not file content.
  </gotchas>

  <bounds>
    <does>builds a compact index, scans in parallel, writes a human-readable summary, reports measured byte sizes.</does>
    <never>modifies source files or writes an index file over 5KB.</never>
  </bounds>

  <handoff next="/sc:analyze /sc:index"/>
</component>