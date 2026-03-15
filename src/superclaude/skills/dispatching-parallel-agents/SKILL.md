---
name: dispatching-parallel-agents
description: |
  Dispatch multiple subagents concurrently for independent tasks. Use when facing
  2+ tasks that can be worked on without shared state or sequential dependencies.
  Manages context isolation between agents.
disable-model-invocation: true
---

<component name="dispatching-parallel-agents" type="skill">

  <role>
    <mission>Delegate independent tasks to parallel agents with isolated context, then integrate their results</mission>
  </role>

  <flow>
    1. Identify independent tasks: Decompose work into non-overlapping units — two tasks are independent if one agent failing completely would not prevent the other from succeeding
    2. Craft focused agent prompts: Each prompt should be self-contained — include scope (specific files/modules), goal (concrete acceptance criteria), constraints (what not to touch), and all relevant context (code snippets, error messages copied verbatim) — do not reference session history
    3. Dispatch agents in parallel: Give each agent a distinct working area to avoid merge conflicts — prefer smaller, well-defined tasks over large ambiguous ones
    4. Review results: Confirm each agent met its stated goal — check for overlapping file edits or incompatible changes
    5. Integrate and verify: Apply changes in logical order, resolve any conflicts, then run the full test suite on the integrated result
  </flow>

  <constraints>
  - Do not dispatch parallel agents for related failures that likely share a root cause — investigate first
  - Do not dispatch when agents would need to edit the same files
  - Do not skip the integration test suite — individual agent tests passing does not guarantee the combined result works
  - If an agent fails, retry with an adjusted prompt or different model before escalating
  </constraints>

  <bounds will="integrate all agent results, pass full test suite, commit changes in logical grouping" wont="dispatch agents for related failures, skip integration testing"/>

  <handoff next="/sc:spawn using-git-worktrees"/>
</component>
