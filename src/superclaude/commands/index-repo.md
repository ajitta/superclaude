---
description: Repository indexing with 94% token reduction (58K → 3K)
---
<component name="index-repo" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="low"/>

  <role>
    /sc:index-repo
    <mission>Repository indexing with 94% token reduction (58K → 3K)</mission>
  </role>

  <syntax>/sc:index-repo [mode=create|update|quick]</syntax>

  <triggers>
    - Repository indexing requests
    - Token reduction needs
    - Project structure documentation
  </triggers>

  <flow>
    1. **Analyze**: Repo structure (5 parallel Glob)
    2. **Extract**: Entry points + modules + APIs + deps
    3. **Generate**: PROJECT_INDEX.md + .json
    4. **Validate**: Completeness + size <5KB
  </flow>

  <tools>
    - **Glob**: Parallel structure scan (code|docs|config|tests|scripts)
    - **Read**: Metadata extraction
    - **Write**: Index generation
  </tools>

  <patterns>
    - **Structure**: src/**/*.{ts,py,js} | docs/**/*.md | *.toml | tests/**/*
    - **Output**: PROJECT_INDEX.md (3KB) + PROJECT_INDEX.json (10KB)
  </patterns>

  <roi>
    - **creation**: 2K tokens (one-time)
    - **reading**: 3K tokens (per session)
    - **full-read**: 58K tokens (per session)
    - **breakeven**: 1 session
    - **10-sessions**: 550K tokens saved
  </roi>

  <examples>

| Input | Output |
|-------|--------|
| `/index-repo` | Create full index |
| `mode=update` | Update existing |
| `mode=quick` | Skip tests |

  </examples>

  <bounds will="94% token reduction|parallel analysis|human-readable output" wont="modify source|exceed 5KB"/>
</component>
