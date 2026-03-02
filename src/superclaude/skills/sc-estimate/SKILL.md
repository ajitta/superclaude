---
name: sc-estimate
description: >-
  This skill should be used when the user asks to
  "estimate development time",
  "how long will this take",
  "complexity assessment",
  "effort estimation",
  "project timeline estimate",
  "task breakdown with estimates",
  "estimate the scope",
  "development cost estimate".
version: 1.0.0
metadata:
  context: inline
  agent: system-architect
  mcp: seq
  allowed-tools:
    - Read
    - Grep
    - Glob
    - Bash
---
<component name="sc-estimate" type="skill">

  <role>
    <mission>Provide development estimates for tasks, features, or projects with intelligent analysis</mission>
  </role>

  <syntax>/sc:estimate [target] [--type time|effort|complexity] [--unit hours|days|weeks] [--breakdown]</syntax>

  <flow>
    1. Scope: Read target description, scan relevant codebase areas to understand existing complexity
    2. Analyze: Measure codebase metrics (file count, LOC, dependency depth, test coverage)
    3. Calculate: Apply estimation methodology (analogous estimation, decomposition, expert judgment)
    4. Validate: Cross-reference with benchmarks, identify risks and unknowns
    5. Present: Output breakdown with confidence intervals, risk factors, and assumptions
  </flow>

  <estimation_methods>
| Method | When | Accuracy |
|--------|------|----------|
| Analogous | Similar past work exists | Medium (+-30%) |
| Decomposition | Task can be broken into subtasks | High (+-20%) |
| Expert Judgment | Novel or ambiguous scope | Low (+-50%) |
| Three-Point | Risk-sensitive estimates needed | Medium-High (optimistic/likely/pessimistic) |
  </estimation_methods>

  <complexity_scoring>
| Factor | Weight | Measures |
|--------|--------|----------|
| Code Volume | 20% | Files affected, LOC changes |
| Dependencies | 25% | Cross-module coupling, external deps |
| Test Coverage | 15% | Existing coverage, new tests needed |
| Risk | 25% | Unknown tech, integration complexity |
| Documentation | 15% | API docs, guides needed |
  </complexity_scoring>

  <patterns>
    - Scope: Requirements analysis -> identify affected files/modules -> boundary definition
    - Method: Select estimation approach based on available data and task type
    - MultiDomain: Combine architecture + performance + timeline assessments for comprehensive view
    - Validation: Compare against benchmarks, flag unrealistic assumptions, adjust for team context
  </patterns>

  <examples>
| Input | Output |
|-------|--------|
| `'auth system' --type time --unit days --breakdown` | 8 days estimate, 85% confidence, task breakdown |
| `'monolith to microservices' --type complexity --breakdown` | Risk map + dependency analysis + phased plan |
| `'optimize performance' --type effort --unit hours` | Effort by category with confidence intervals |
| (auto-trigger) "how long will this take" | Skill activates, analyzes scope, provides estimate |
| (auto-trigger) "estimate the effort" | Skill activates, runs effort analysis |

  <example name="estimate-no-scope" type="error-path">
    <input>/sc:estimate 'make it better' --type time</input>
    <why_wrong>No measurable scope. 'make it better' could mean anything from a typo fix to a full rewrite.</why_wrong>
    <correct>Define scope first: /sc:estimate 'refactor auth module to use JWT' --type time --breakdown</correct>
  </example>
  </examples>

  <bounds will="systematic estimates|confidence intervals|risk analysis|codebase metrics" wont="guarantee accuracy|estimate without analysis|modify any files" fallback="Ask user for scope clarification when target is ambiguous"/>

  <handoff next="/sc:workflow /sc:implement"/>
</component>
