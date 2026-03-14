---
description: Apply systematic improvements to code quality, performance, and maintainability
---
<component name="improve" type="command">

  <role>
    /sc:improve
    <mission>Apply systematic improvements to code quality, performance, and maintainability</mission>
  </role>

  <syntax>/sc:improve [target] [--type quality|performance|maintainability|style] [--safe] [--interactive]</syntax>

  <flow>
    1. Analyze: Identify improvement opportunities
    2. Plan: Select approach + activate relevant persona
    3. Execute: Apply improvements following best practices
    4. Validate: Ensure functionality preserved
    5. Document: Summary + future recommendations
  </flow>

  <personas p="arch|perf|qual|sec|refactor|simple"/>

  <patterns>
    - Quality: tech debt ID → refactoring → validation
    - Performance: profiling → bottleneck ID → optimization
    - Maintainability: complexity reduction → structure → docs
    - Security: vulnerability scan → pattern application → validation
  </patterns>

  <examples>
  | Input | Output |
  |-------|--------|
  | `src/ --type quality --safe` | Safe quality refactoring |
  | `api/ --type performance` | Bottleneck analysis + optimization |
  | `--type performance` (no baseline) | Error: run /sc:analyze --focus perf first |
  </examples>

  <bounds will="systematic improvements|safe refactoring" wont="risky changes without confirm|arch changes without analysis"/>

  <handoff next="/sc:test /sc:analyze"/>
</component>
