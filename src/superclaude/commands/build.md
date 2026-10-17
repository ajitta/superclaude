---
description: Build, compile and package projects with error analysis and optimization. On request only — the user's /sc:build or a workflow step that names it. Not for a single build command (npm run build, cargo build) — run it with Bash.
---
<component name="build" type="command">

  <role command="/sc:build">
    <mission>Build, compile and package projects with error analysis and optimization</mission>
  </role>

  <syntax>/sc:build [target] [--type dev|prod|test] [--clean] [--optimize] [--verbose]</syntax>

  <flow>
  1. Analyze: read the project structure, build config and dependencies.
  2. Validate: confirm the environment and toolchain are ready.
  3. Execute: run the build and watch its output.
  4. Optimize: check artifacts and bundle size (only with --optimize).
  5. Package: collect the artifacts and report the result in the console.
  </flow>

  <flags>
  - --type dev|prod|test: build variant passed to the project's build tool; console report per the outputs table.
  - --clean: before building, delete only the output directory the project's build config names (outDir, target/, build/); if the config names none, ask which directory to delete; never git clean.
  - --optimize: runs the Optimize step.
  - --verbose: run the build tool in its verbose mode and report the full output, not a summary.
  </flags>

  <outputs note="Per --type flag; console only, no report file">
| Type | Artifacts | Report |
|---|---|---|
| dev | output directory named in the build config (tool-generated) | Console: build output + warnings |
| prod | output directory named in the build config (tool-generated) | Console: bundle size + optimization summary |
| test | output directory named in the build config (tool-generated) | Console: build output + test config |
  </outputs>

  <examples>

| Input | Output |
|---|---|
| `/sc:build` | Default build + console report |
| `--type prod --clean --optimize` | Production artifacts |
| `frontend --verbose` | Detailed component build |
| `--type dev --verbose` | Dev build + detailed output |

  <example name="build-failure-retry" type="error-path">
    - Input: /sc:build --type prod (after the build failed with a missing dependency)
    - Why wrong: retrying the same build without fixing the root cause wastes tokens and time.
    - Correct: read the error, report the missing dependency and the install command for the project's package manager, and stop — /sc:build never installs dependencies. Rerun /sc:build --type prod after the user installs it.
  </example>

  </examples>

  <bounds>
    <does>runs builds, analyzes build errors, recommends optimizations, reports in the console.</does>
    <never>modifies build config, installs dependencies, deploys, or writes a report file.</never>
  </bounds>

  <handoff next="/sc:test /sc:troubleshoot"/>
</component>