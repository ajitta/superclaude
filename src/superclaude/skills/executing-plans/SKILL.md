---
name: executing-plans
description: |
  Execute implementation plans with review checkpoints. Use when you have a written
  plan to implement. Follows plan tasks sequentially, runs verification at checkpoints,
  and delegates to subagents when available.
---
<component name="executing-plans" type="skill">

  <role>
    <mission>Load a written plan, execute every task in order, verify results, and hand off to finishing when complete</mission>
  </role>

  <when>
  - When you have a written plan to implement
  - After writing-plans has produced an approved plan
  - When sequential task execution with verification is needed
  </when>

  <flow>
    1. Load plan — read the full plan document before touching any code
    2. Review — confirm tasks are clear and dependencies are correct. If gaps or contradictions exist, raise them with the user before proceeding
    3. Set up worktree — work should be in an isolated worktree (see using-git-worktrees skill)
    4. Execute tasks in order — for each task: mark in-progress, follow steps as written, run verification commands. On pass, mark completed. On fail, diagnose the issue
    5. Stop on blockers — if blocked (missing dependency, ambiguous instructions, verification failure), stop and ask for help rather than guessing
    6. Complete — announce all tasks are finished, summarize what was implemented and any deviations, then hand off to finishing-a-development-branch skill
  </flow>

  <constraints>
  - Do not reorder tasks unless a dependency explicitly requires it
  - Do not skip verification steps
  - If a later task reveals a previous task was implemented incorrectly, revisit and fix before continuing
  - When subagents are available, delegate independent subtasks via `/sc:agent` or `/sc:spawn`
  </constraints>

  <bounds will="plan execution|task verification|blocker reporting|deviation tracking" wont="reorder tasks without cause|skip verification|guess past blockers"/>

  <handoff next="finishing-a-development-branch"/>
</component>
