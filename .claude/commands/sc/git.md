---
description: Git operations with intelligent commit messages and workflow optimization
---
<component name="git" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5"/>

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
</component>
