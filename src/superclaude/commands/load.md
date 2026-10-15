---
description: Load session context from the project memory folder (.claude/memories/) and Claude auto memory. On request only — the user's /sc:load or a workflow step that names it. Not for resuming work or "let's continue" — keep working.
---
<component name="load" type="command">

  <role command="/sc:load">
    <mission>Session lifecycle management with the project memory folder and Claude auto memory for loading project context</mission>
  </role>

  <syntax>/sc:load [target] [--type project|config|deps|checkpoint] [--refresh] [--analyze]</syntax>

  <flow>
  1. Load (memory folder): Glob .claude/memories/*.md → Read pm_context when present + the newest session_*_[branch-slug].md of the current branch (slug per /sc:save <storage>); none → the newest session_* of any branch, reported as that branch's record; folder absent → skip
  2. Load (auto memory): MEMORY.md (auto-load) + topic files linked from MEMORY.md
  3. Discover: project structure and requirements (Glob/Grep/Read)
  4. Activate: project context and workflow preparation
  5. Validate: context integrity and session readiness
  6. Session Goal (optional): if the user gives a goal, record it as a 1-line objective; restate it when the work changes direction and before /sc:save.
  </flow>

  <flags>
  - --type project|config|deps|checkpoint: what to load: project memory and structure, configuration files, dependency manifests, or the saved checkpoint the target names (e.g. session_123).
  - --refresh: re-read sources and replace loaded memory instead of reusing it.
  - --analyze: on top of the structure the Discover step always reports, assess the project's state: test status, open TODOs and recent changes.
  </flags>

  <storage>
    Storage locations (memory folder / auto memory / topic files / agent memory): SSOT in /sc:save <storage> — installed sibling commands/sc/save.md.
  </storage>


  <tools>
  - Glob/Read: memory folder, auto memory and project file analysis
  - Grep: project file analysis
  - Write: checkpoint creation
  </tools>

  <examples>

| Input | Output |
|---|---|
| `/sc:load` | Current dir + memory folder + auto memory |
| `/path/to/project --type project --analyze` | Specific project with analysis |
| `session_123 --type checkpoint` | Restore checkpoint |
| `--type deps --refresh` | Fresh dep analysis |

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
    <never>modifies project structure, loads without validation, or overrides without a checkpoint.</never>
    <fallback>Memory folder absent: auto memory + Read CLAUDE.md/PLANNING.md/TASK.md, Glob for the project structure. Ask the user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:analyze /sc:index-repo /sc:task"/>
</component>