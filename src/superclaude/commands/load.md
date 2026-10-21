---
description: Load session context from the project memory folder (.claude/memories/) and Claude auto memory. On request only — the user's /sc:load or a workflow step that names it. Not for resuming work or "let's continue" — keep working.
---
<component name="load" type="command">

  <role command="/sc:load">
    <mission>Session lifecycle management with the project memory folder and Claude auto memory for loading project context</mission>
  </role>

  <syntax>/sc:load [target] [--type project|config|deps|checkpoint] [--refresh] [--analyze]</syntax>

  <flow>
  1. Sync: quote every upstream ref as below (PowerShell reads a bare one as a hashtable); the branch has an upstream (`git rev-parse --abbrev-ref '@{u}'`) → `git -c credential.interactive=never fetch --quiet` with credential prompts off (`GIT_TERMINAL_PROMPT=0`; PowerShell: `$env:GIT_TERMINAL_PROMPT=0`), then `git rev-list --count 'HEAD..@{u}'`; behind → tell the user the count and ask `[y/n]` before `git pull --ff-only`, and wait for the answer; the pull stops because the branch diverged → say so and name `git pull --rebase` without running it; no upstream, fetch fails or the pull stops → say so in one line and go on with the files on disk
  2. Load (memory folder): Glob .claude/memories/*.md → Read learnings_corrections when present (corrections /sc:save keeps there while auto memory is off) + the current branch's records: among session_*_[branch-slug].md keep those whose `branch:` line names the current branch (a branch slug may hold `_`, so the filename alone can misread machine and branch), then read every one of the newest date, one per machine — the part between the date and `_[branch-slug]` names the machine, and an empty part marks a record from before machine names — and say which machine wrote it (slugs per /sc:save <storage>); none → the newest session_* of any branch, reported as the branch its `branch:` line names; folder absent → skip
  3. Load (auto memory): MEMORY.md is already in context (Claude Code loads it); Read a memory file it points to only when that pointer bears on the session's work
  4. Discover: project structure and requirements (Glob/Grep/Read)
  5. Activate: project context and workflow preparation
  6. Validate: context integrity and session readiness
  7. Session Goal (optional): if the user gives a goal, record it as a 1-line objective; restate it when the work changes direction and before /sc:save.
  </flow>

  <flags>
  - --type project|config|deps|checkpoint: what to load: project memory and structure, configuration files, dependency manifests, or the saved checkpoint the target names (e.g. session_123).
  - --refresh: re-read sources and replace loaded memory instead of reusing it.
  - --analyze: on top of the structure the Discover step always reports, assess the project's state: test status, open TODOs and recent changes.
  </flags>

  <storage>
    Storage locations (memory folder / auto memory / agent memory): SSOT in /sc:save <storage> — installed sibling commands/sc/save.md.
  </storage>


  <tools>
  - Glob/Read: memory folder, auto memory and project file analysis
  - Grep: project file analysis
  - Write: checkpoint creation
  - Bash: git branch, rev-parse, fetch and rev-list for the branch slug and the Sync step; git pull only after the user's yes
  </tools>

  <examples>

| Input | Output |
|---|---|
| `/sc:load` | Current dir + memory folder + auto memory |
| `/path/to/project --type project --analyze` | Specific project with analysis |

  <example name="load-wrong-project" type="error-path">
    - Input: /sc:load /path/to/wrong/project --type project
    - Why wrong: loading context for the wrong project pollutes the session with irrelevant information.
    - Correct: verify the project path first (ls, git remote -v), then run /sc:load with the confirmed path.
  </example>

  </examples>


  <gotchas>
  - stale-memory: verify loaded memory against the current file state before acting on it
  - dual-persistence: Check both the memory folder and auto memory for full context
  </gotchas>

  <bounds>
    <does>loads the memory folder and auto memory, persists context across sessions.</does>
    <never>modifies project structure, loads without validation, overrides without a checkpoint, or pulls without the user's yes.</never>
    <fallback>Memory folder absent: auto memory + Read CLAUDE.md/PLANNING.md/TASK.md, Glob for the project structure. Ask the user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:analyze /sc:index-repo /sc:task"/>
</component>