---
description: Apply systematic improvements to code quality, performance, and maintainability
---
<component name="improve" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="medium"/>

  <role>
    /sc:improve
    <mission>Apply systematic improvements to code quality, performance, and maintainability</mission>
  </role>

  <syntax>/sc:improve [target] [--type quality|performance|maintainability|style] [--safe] [--interactive]</syntax>

  <triggers>
    - Code quality enhancement requests
    - Performance optimization needs
    - Maintainability + tech debt reduction
    - Best practices enforcement
  </triggers>

  <flow>
    1. Analyze: Improvement opportunities + quality issues
    2. Plan: Approach + persona activation
    3. Execute: Systematic improvements + best practices
    4. Validate: Functionality preservation + quality
    5. Document: Summary + future recommendations
  </flow>

  <mcp servers="seq:analysis|c7:patterns"/>
  <personas p="arch|perf|qual|sec"/>

  <tools>
    - Read/Grep/Glob: Code analysis + opportunity ID
    - Edit/MultiEdit: Safe modification + refactoring
    - TodoWrite: Multi-file progress tracking
    - Task: Large-scale improvement delegation
  </tools>

  <patterns>
    - Quality: Analysis → tech debt ID → refactoring
    - Performance: Profiling → bottleneck ID → optimization
    - Maintainability: Structure → complexity reduction → docs
    - Security: Vulnerability → pattern application → validation
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `src/ --type quality --safe` | Systematic quality + safe refactor |
| `api-endpoints --type performance --interactive` | Bottleneck analysis |
| `legacy-modules --type maintainability --preview` | Structure improvement |
| `auth-service --type security --validate` | Security hardening |

  </examples>

  <bounds will="systematic improvements|multi-persona|safe refactoring" wont="risky changes without confirm|arch changes without impact analysis|override standards"/>
</component>
