---
description: Build, compile, and package projects with intelligent error handling and optimization
---
<component name="build" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="medium"/>

  <role>
    /sc:build
    <mission>Build, compile, and package projects with intelligent error handling and optimization</mission>
  </role>

  <syntax>/sc:build [target] [--type dev|prod|test] [--clean] [--optimize] [--verbose]</syntax>

  <triggers>
    - Project compilation + packaging
    - Build optimization needs
    - Build error debugging
    - Deployment artifact preparation
  </triggers>

  <flow>
    1. Analyze: Structure, configs, deps
    2. Validate: Environment + toolchain
    3. Execute: Build + real-time monitoring
    4. Optimize: Artifacts + bundle size
    5. Package: Artifacts + reports
  </flow>

  <mcp servers="play:validation"/>
  <personas p="devops"/>

  <tools>
    - Bash: Build execution
    - Read: Config analysis
    - Grep: Error parsing
    - Glob: Artifact discovery
    - Write: Build reports
  </tools>

  <patterns>
    - Environment: dev|prod|test → appropriate config
    - Error: Build failures → diagnostic + resolution
    - Optimize: Artifact analysis → size reduction
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `/sc:build` | Default build + report |
| `--type prod --clean --optimize` | Production artifacts |
| `frontend --verbose` | Detailed component build |
| `--type dev --validate` | Dev build + Playwright validation |

  </examples>

  <bounds will="execute build|error analysis|optimization recs" wont="modify build config|install deps|deploy"/>
</component>
