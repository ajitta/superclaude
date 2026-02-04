---
description: Build, compile, and package projects with intelligent error handling and optimization
---
<component name="build" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

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
    2. Validate: Environment + toolchain ready
    3. Execute: Build + real-time monitoring
    4. Optimize: Artifacts + bundle size (if --optimize)
    5. Package: Artifacts + generate report
  </flow>

  <outputs note="Per --type flag">
| Type | Artifacts | Report |
|------|-----------|--------|
| dev | dist-dev/ | BUILD_DEV.log |
| prod | dist/ | BUILD_REPORT.md |
| test | dist-test/ | BUILD_TEST.log |
  </outputs>

  <checklist note="SHOULD complete all">
    - [ ] Build completed without errors
    - [ ] Artifacts generated in correct location
    - [ ] Bundle size within limits (if --optimize)
    - [ ] Build report generated
  </checklist>

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

  <boundaries type="execution" critical="true">
    <rule>Execute build commands</rule>
    <rule>Preserve build configuration</rule>
    <rule>Preserve current dependencies</rule>
    <rule>Defer deployment to user or CI/CD</rule>
  </boundaries>

  <completion_criteria>
    - [ ] Build completed without errors
    - [ ] Artifacts generated successfully
    - [ ] Build report created
  </completion_criteria>

  <handoff>
    <next command="/sc:test">For running tests on build</next>
    <next command="/sc:git">For committing build artifacts (if applicable)</next>
    <next command="/sc:troubleshoot">For resolving build errors</next>
    <format>Include build status for deployment decisions</format>
  </handoff>
</component>
