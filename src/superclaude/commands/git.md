---
description: Git operations with intelligent commit messages and workflow optimization
---
<component name="git" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>

  <role>
    /sc:git
    <mission>Git operations with intelligent commit messages and workflow optimization</mission>
  </role>

  <syntax>/sc:git [operation] [args] [--smart-commit] [--interactive]</syntax>

  <triggers>
    - Git ops: status, add, commit, push, pull, branch
    - Intelligent commit message generation
    - Repository workflow optimization
    - Branch management + merges
  </triggers>

  <flow>
    1. Analyze: Repo state + changes
    2. Validate: Operation appropriateness
    3. Execute: Git command + automation
    4. Optimize: Smart commits + patterns
    5. Report: Status + next steps
  </flow>

  <tools>
    - Bash: Git command execution
    - Read: Repo state analysis
    - Grep: Log parsing + status
    - Write: Commit message generation
  </tools>

  <patterns>
    - SmartCommit: Analyze changes → conventional message
    - Status: Repo state → actionable recs
    - Branch: Consistent naming + workflow
    - Recovery: Conflict resolution + restoration
  </patterns>

  <examples>

| Input | Output |
|-------|--------|
| `status` | State analysis + recommendations |
| `commit --smart-commit` | Conventional commit |
| `merge feature-branch --interactive` | Guided merge |

  </examples>

  <bounds will="intelligent git ops|conventional commits|workflow guidance" wont="modify config without auth|destructive without confirm|complex merges requiring manual"/>

  <boundaries type="execution" critical="true">
    <rule>EXECUTE git operations as requested</rule>
    <rule>DO NOT force push without explicit confirmation</rule>
    <rule>DO NOT modify git config without authorization</rule>
    <rule>Destructive operations require explicit user approval</rule>
  </boundaries>

  <safety_rules>
    <safe>status, log, diff, add, commit, pull, fetch, branch</safe>
    <approval_required>push --force, reset --hard, rebase, merge with conflicts</approval_required>
  </safety_rules>

  <completion_criteria>
    - [ ] Operation executed successfully
    - [ ] Repository state verified
    - [ ] Appropriate next steps suggested
  </completion_criteria>

  <handoff>
    <next command="/sc:test">Before pushing changes</next>
    <next command="/sc:build">Before deployment commits</next>
    <format>Include commit/push status for CI/CD awareness</format>
  </handoff>
</component>
