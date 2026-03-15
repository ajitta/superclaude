---
name: using-git-worktrees
description: |
  Create isolated git worktrees for feature work and plan execution. Use when
  starting work that needs isolation from current workspace. Sets up worktree
  with smart directory selection and safety verification.
disable-model-invocation: true
allowed-tools: Bash, Read, Grep, Glob
---

<component name="using-git-worktrees" type="skill">

  <role>
    <mission>Set up an isolated git worktree with verified directory selection, dependency installation, and a passing test baseline</mission>
  </role>

  <flow>
    1. Select a worktree directory: Check for existing directories (`.worktrees/`, `worktrees/`) in the repo root — if none exist, check `CLAUDE.md` for a configured preference — if still unresolved, ask the user to choose between a local hidden directory (`.worktrees/`) or a global shared location (`~/.config/superclaude/worktrees/`)
    2. Verify .gitignore coverage: Run `git check-ignore -q <dir>` to confirm the directory is ignored — if not, add it to `.gitignore` and commit the change before proceeding — an unignored worktree directory pollutes `git status` with thousands of untracked files
    3. Create the worktree: Use `git worktree add <dir>/<name> -b <branch>` (or without `-b` if the branch already exists)
    4. Install dependencies: Auto-detect the project type from lock files or build manifests and run the appropriate setup command inside the worktree
    5. Run baseline tests: Execute the project's test suite in the worktree — if tests fail, report failures and pause — do not proceed with feature work on a broken baseline
    6. Report the worktree location: Print the absolute path, branch name, and status so the caller knows where to work
  </flow>

  <constraints>
  - Do not create a worktree in a directory that is not gitignored
  - Do not proceed with feature work when baseline tests fail
  - Do not create a worktree on a branch that already has an active worktree
  </constraints>

  <bounds will="create worktree at known path with dependencies installed and baseline tests passing" wont="proceed on broken baselines, create worktrees in non-ignored directories"/>

  <handoff next="finishing-a-development-branch dispatching-parallel-agents"/>
</component>
