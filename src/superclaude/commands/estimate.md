---
description: Provide development estimates for tasks, features, or projects with intelligent analysis
---
<component name="estimate" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

  <role>
    /sc:estimate
    <mission>Provide development estimates for tasks, features, or projects with intelligent analysis</mission>
  </role>

  <syntax>/sc:estimate [target] [--type time|effort|complexity] [--unit hours|days|weeks] [--breakdown]</syntax>

  <triggers>
    - Development time/effort estimates
    - Project scoping + resource allocation
    - Feature breakdown estimation
    - Risk assessment + confidence intervals
  </triggers>

  <flow>
    1. Analyze: Scope, complexity, deps, patterns
    2. Calculate: Methodology + benchmarks
    3. Validate: Cross-reference + domain expertise
    4. Present: Breakdown + confidence + risk
    5. Track: Accuracy for improvement
  </flow>

  <mcp servers="seq:analysis|c7:benchmarks"/>
  <personas p="arch|perf|pm"/>

  <tools>
    - Read/Grep/Glob: Codebase complexity analysis
    - TaskCreate/TaskUpdate: Estimation breakdown tracking
    - Task: Multi-domain estimation delegation
    - Bash: Project + dependency analysis
  </tools>

  <patterns>
    - Scope: Requirements → complexity → patterns → risk
    - Method: Time|Effort|Complexity|Cost approaches
    - Multi-Domain: Arch + Perf + Timeline assessment
    - Validation: Benchmarks → cross-check → confidence
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `'auth system' --type time --unit days --breakdown` | 8 days, 85% confidence |
| `'monolith to microservices' --type complexity --breakdown` | Risk + dependency map |
| `'optimize performance' --type effort --unit hours` | Effort by category |

  </examples>

  <bounds will="systematic estimates|confidence intervals|multi-persona analysis" wont="guarantee accuracy|estimate without analysis|override benchmarks"/>

  <boundaries type="document-only" critical="true">
    <rule>STOP after producing estimation report</rule>
    <rule>DO NOT begin implementation</rule>
    <rule>DO NOT create task tracking beyond estimation</rule>
    <output>Estimation report with breakdown and confidence intervals</output>
  </boundaries>

  <handoff>
    <next command="/sc:workflow">For implementation planning based on estimates</next>
    <next command="/sc:implement">For direct implementation of estimated work</next>
    <format>Provide estimates context for resource allocation</format>
  </handoff>
</component>
