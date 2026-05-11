---
description: Apply systematic improvements to code quality, performance, and maintainability. Use when the user types `/sc:improve` or asks for a multi-file quality/perf/maintainability sweep with measurable targets. Do NOT auto-trigger on "improve this function", "rename this variable", or small single-file refactors — those are direct edits.
---
<component name="improve" type="command">

  <role command="/sc:improve">
    <mission>Apply systematic improvements to code quality, performance, and maintainability</mission>
  </role>

  <syntax>/sc:improve [target] [--type quality|performance|maintainability|style] [--safe] [--interactive]</syntax>

  <flow>
  1. Analyze: Identify improvement opportunities
  2. Plan: Select approach + delegate to relevant agent
  3. Execute: Apply improvements following best practices
  4. Validate: Ensure functionality preserved
  5. Document: Summary + future recommendations
  </flow>


  <patterns>
    - Quality: tech debt ID → refactoring → validation
    - Performance: profiling → bottleneck ID → optimization
    - Maintainability: complexity reduction → structure → docs
    - Security: vulnerability scan → pattern application → validation
  </patterns>

  <examples>
  | Input | Output |
  |---|---|
  | `src/ --type quality --safe` | Safe quality refactoring |
  | `api/ --type performance` | Bottleneck analysis + optimization |
  | `--type performance` (no baseline) | Error: run /sc:analyze --focus perf first |
  </examples>


  <gotchas>
  - necessity-test: Apply R18 before proposing improvements. "safer/better" alone is insufficient justification
  - halo-improvement: When improving target A, do not also rewrite adjacent function B because it "looks worse by comparison". Each improvement must be the user's explicit target, not bundled cleanup of nearby code that suddenly looks dated next to the improved code.
  </gotchas>

  <bounds>
    <does>systematic improvements and safe refactoring.</does>
    <never>risky changes without confirm and arch changes without analysis.</never>
    <fallback>Ask user when improvement scope exceeds target boundary.</fallback>
  </bounds>

  <handoff next="/sc:test /sc:analyze"/>
</component>
