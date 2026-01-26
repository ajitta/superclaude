---
description: Apply systematic improvements to code quality, performance, and maintainability
---
<component name="improve" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

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
    - TaskCreate/TaskUpdate: Multi-file progress tracking
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

  <boundaries type="execution" critical="true">
    <rule>IMPLEMENT improvements as requested</rule>
    <rule>Safe mode (--safe): Only non-breaking changes</rule>
    <rule>Interactive mode (--interactive): Confirm each change</rule>
  </boundaries>

  <auto_fix_threshold>
    <safe>Style fixes, minor refactoring, documentation updates</safe>
    <approval_required>API changes, dependency updates, architecture modifications</approval_required>
  </auto_fix_threshold>

  <completion_criteria>
    - [ ] All identified improvements applied
    - [ ] No breaking changes introduced
    - [ ] Tests pass (if available)
    - [ ] Code quality metrics improved
  </completion_criteria>

  <handoff>
    <next command="/sc:test">For verifying improvements</next>
    <next command="/sc:git">For committing changes</next>
    <format>Summarize improvements for test coverage</format>
  </handoff>
</component>
