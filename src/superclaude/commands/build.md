---
description: Build, compile, and package projects with intelligent error handling and optimization
---
<component name="build" type="command">

  <role>
    /sc:build
    <mission>Build, compile, and package projects with intelligent error handling and optimization</mission>
  </role>

  <syntax>/sc:build [target] [--type dev|prod|test] [--clean] [--optimize] [--verbose]</syntax>

  <flow>
    1. Analyze: Structure, configs, deps
    2. Validate: Environment + toolchain ready
    3. Execute: Build + real-time monitoring
    4. Optimize: Artifacts + bundle size (if --optimize)
    5. Package: Artifacts + generate report
  </flow>

  <outputs note="Per --type flag">
| Type | Artifacts | Report |
|------|-----------|--------|
| dev | `dist-dev/` (tool-generated) | Console: build output + warnings |
| prod | `dist/` (tool-generated) | Console: bundle size + optimization summary |
| test | `dist-test/` (tool-generated) | Console: build output + test config |
  </outputs>


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
| `--type dev --verbose` | Dev build + detailed output |

  <example name="build-failure-retry" type="error-path">
    <input>/sc:build --type prod (after build fails with missing dependency)</input>
    <why_wrong>Retrying the same build without fixing the root cause wastes tokens and time.</why_wrong>
    <correct>Investigate error → fix dependency (npm install / uv add) → then /sc:build --type prod</correct>
  </example>

  </examples>

  <bounds will="execute build|error analysis|optimization recs" wont="modify build config|install deps|deploy" fallback="Ask user for guidance when uncertain">

    Execute build commands | Preserve build configuration | Preserve current dependencies | Defer deployment to user or CI/CD

  </bounds>

  <handoff next="/sc:test /sc:troubleshoot"/>
</component>
