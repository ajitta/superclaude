---
description: Build, compile, and package projects with intelligent error handling and optimization
---
<component name="build" type="command">

  <role command="/sc:build">
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
|---|---|---|
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
|---|---|
| `/sc:build` | Default build + report |
| `--type prod --clean --optimize` | Production artifacts |
| `frontend --verbose` | Detailed component build |
| `--type dev --verbose` | Dev build + detailed output |

  <example name="build-failure-retry" type="error-path">
    - Input: /sc:build --type prod (after build fails with missing dependency)
    - Why wrong: Retrying the same build without fixing the root cause wastes tokens and time.
    - Correct: Investigate error → fix dependency (npm install / uv add) → then /sc:build --type prod
  </example>

  </examples>


  <gotchas>
  - make-deploy: SuperClaude uses `make deploy` for installation. Do not use npm/pip/yarn build
  - uv-only: Use `uv` for all Python operations. Never use `pip` directly
  </gotchas>

  <bounds>
    <does>execute build, error analysis, and optimization recs.</does>
    <never>modify build config, install deps, and deploy.</never>
    <fallback>Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:test /sc:troubleshoot"/>
</component>
