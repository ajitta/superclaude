---
name: sc-build
description: >-
  This skill should be used when the user asks to
  "build the project",
  "compile the application",
  "package for production",
  "run a production build",
  "build with optimizations",
  "clean build",
  "fix build errors",
  "create build artifacts".
version: 1.0.0
metadata:
  context: inline
  agent: devops-architect
  mcp: play
  allowed-tools:
    - Bash
    - Read
    - Grep
    - Glob
    - Write
---
<component name="sc-build" type="skill">

  <role>
    <mission>Build, compile, and package projects with intelligent error handling and optimization</mission>
  </role>

  <syntax>/sc:build [target] [--type dev|prod|test] [--clean] [--optimize] [--verbose]</syntax>

  <flow>
    1. Detect: Identify build system from config files (package.json, pyproject.toml, Cargo.toml, Makefile, build.gradle)
    2. Validate: Check environment readiness (Node version, Python version, dependencies installed)
    3. Execute: Run build command with real-time output monitoring, capture errors
    4. Recover: On failure, analyze error output, suggest fixes (missing deps, version conflicts, config issues)
    5. Optimize: If --optimize, analyze bundle size, suggest tree-shaking, dead code elimination
    6. Report: Output build summary with artifact sizes, timing, and next-step recommendations
  </flow>

  <build_detection note="Auto-detect build system">
| Config File | Build System | Command |
|-------------|-------------|---------|
| package.json (build script) | npm/yarn/pnpm | `npm run build` / `yarn build` / `pnpm build` |
| pyproject.toml (hatchling/setuptools) | Python | `uv build` or `python -m build` |
| Cargo.toml | Rust | `cargo build --release` |
| Makefile | Make | `make` or `make build` |
| build.gradle / build.gradle.kts | Gradle | `./gradlew build` |
| CMakeLists.txt | CMake | `cmake --build .` |
  </build_detection>

  <outputs note="Per --type flag">
| Type | Artifacts | Report |
|------|-----------|--------|
| dev | dist-dev/ | BUILD_DEV.log |
| prod | dist/ | BUILD_REPORT.md |
| test | dist-test/ | BUILD_TEST.log |
  </outputs>

  <patterns>
    - Detection: Scan for build config files, determine build system, select appropriate command
    - Environment: Verify toolchain versions, check dependency freshness, validate config
    - ErrorRecovery: Parse build errors, match against known patterns (missing module, version mismatch, syntax error), suggest targeted fixes
    - Optimize: Analyze output artifacts for size, identify large dependencies, suggest optimizations
  </patterns>

  <examples>
| Input | Output |
|-------|--------|
| `/sc:build` | Detect build system, run default build, report |
| `--type prod --clean --optimize` | Clean build with production optimizations |
| `frontend --verbose` | Detailed frontend build with full output |
| (auto-trigger) "build the project" | Skill activates, detects system, builds |
| (auto-trigger) "fix build errors" | Skill activates, analyzes and resolves failures |

  <example name="build-failure-retry" type="error-path">
    <input>/sc:build --type prod (after build fails with missing dependency)</input>
    <why_wrong>Retrying the same build without fixing the root cause wastes tokens and time.</why_wrong>
    <correct>Investigate error → fix dependency (npm install / uv add) → then /sc:build --type prod</correct>
  </example>
  </examples>

  <bounds will="execute builds|error analysis|optimization recs|build system detection" wont="modify build config without approval|install deps without confirmation|deploy artifacts" fallback="Ask user for guidance when build system is ambiguous"/>

  <handoff next="/sc:test /sc:git /sc:troubleshoot"/>
</component>
