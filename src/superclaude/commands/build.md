---
description: Build, compile, package projects w/ smart err handling + optimize. Use ONLY when user type `/sc:build` — orchestrate build pipeline w/ err analysis. NO auto-trigger on single build cmd (npm run build, cargo build) — use Bash direct.
---
<component name="build" type="command">

  <role command="/sc:build">
    <mission>Build, compile, package projects w/ smart err handling + optimize</mission>
  </role>

  <syntax>/sc:build [target] [--type dev|prod|test] [--clean] [--optimize] [--verbose]</syntax>

  <flow>
  1. Analyze: Structure, configs, deps
  2. Validate: Env + toolchain ready
  3. Execute: Build + real-time monitor
  4. Optimize: Artifacts + bundle size (if --optimize)
  5. Package: Artifacts + gen report
  </flow>

  <outputs note="Per --type flag">
| Type | Artifacts | Report |
|---|---|---|
| dev | `dist-dev/` (tool-generated) | Console: build output + warnings |
| prod | `dist/` (tool-generated) | Console: bundle size + optimization summary |
| test | `dist-test/` (tool-generated) | Console: build output + test config |
  </outputs>


  <tools>
  - Bash: Build exec
  - Read: Config analysis
  - Grep: Err parse
  - Glob: Artifact discover
  - Write: Build reports
  </tools>

  <patterns>
    - Env: dev|prod|test → right config
    - Err: Build fail → diagnostic + fix
    - Optimize: Artifact analysis → size cut
  </patterns>

  <examples>

| Input | Output |
|---|---|
| `/sc:build` | Default build + report |
| `--type prod --clean --optimize` | Production artifacts |
| `frontend --verbose` | Detailed component build |
| `--type dev --verbose` | Dev build + detailed output |

  <example name="build-failure-retry" type="error-path">
    - Input: /sc:build --type prod (after build fail w/ missing dep)
    - Why wrong: Retry same build w/o fix root cause waste tokens + time.
    - Correct: Investigate err → fix dep (npm install / uv add) → then /sc:build --type prod
  </example>

  </examples>


  <gotchas>
  - make-deploy: SuperClaude use `make deploy` for install. No use npm/pip/yarn build
  - uv-only: Use `uv` for all Python ops. Never use `pip` direct
  </gotchas>

  <bounds>
    <does>exec build, err analysis, optimize recs.</does>
    <never>modify build config, install deps, deploy.</never>
    <fallback>Ask user for guidance when unsure.</fallback>
  </bounds>

  <handoff next="/sc:test /sc:troubleshoot"/>
</component>