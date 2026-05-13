---
name: finishing-a-development-branch
description: Finish dev work w/ structured opts for merge, PR, or cleanup. Use when user done w/ feature branch + wants merge, PR, or branch cleanup.
disable-model-invocation: true
allowed-tools: Bash, Read, Grep, Glob
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'git branch -D([^a-zA-Z]|$)|git push (--force([^-]|$)|-f([^a-zA-Z]|$))' && echo 'BLOCKED: Destructive git operation. Confirm with user first (--force-with-lease is allowed).' >&2 && exit 2 || exit 0"
---

<component name="finishing-a-development-branch" type="skill">

  <role>
    <mission>Guide branch finish: verify tests, show opts, run chosen path, cleanup</mission>
  </role>

  <flow>
  1. Run test suite: tests must pass b4 opts — if fail, report + pause
  2. Detect base branch: check `main` vs `master`, confirm w/ user b4 proceed
  3. Show four opts:
  - Merge local into base
  - Push + make PR
  - Keep branch as-is
  - Discard branch (need typed "discard" confirm)
  4. Run chosen opt: merges → re-run tests after — PRs → use `gh pr create` + report URL — discard → wait explicit confirm b4 delete
  5. Cleanup worktree if applicable: remove for merge + discard — keep for PR + keep-as-is
  </flow>

  <constraints>
  - No pass step 1 w/ failing tests
  - No skip typed confirm on discard
  - No force-push w/o explicit user ask
  - No auto-merge PR — review separate
  </constraints>

  <gotchas>
  - stash-check: check git stash state b4 deleting worktree. Tell user if stash entries exist
  - base-branch: after auto-detect main vs master, always confirm w/ user. Stops merge into wrong base
  </gotchas>

  <bounds>
    <does>run chosen finish opt, handle worktree cleanup, tell user result.</does>
    <never>proceed w/ failing tests, force-push w/o ask, auto-merge PRs.</never>
  </bounds>

  <handoff next="/sc:git"/>
</component>