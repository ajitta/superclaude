---
description: Load session context from the project memory folder (.claude/memories/) and Claude auto memory. On request only — the user's /sc:load or a workflow step that names it. Not for resuming work or "let's continue" — keep working.
---
<component name="load" type="command">

  <role command="/sc:load">
    <mission>Session lifecycle mgmt with the project memory folder + Claude auto memory for proj context load</mission>
  </role>

  <syntax>/sc:load [target] [--type project|config|deps|checkpoint] [--refresh] [--analyze]</syntax>

  <flow>
  1. Load (memory folder): Glob .claude/memories/*.md → Read pm_context when present + the newest session_*_[branch-slug].md of the current branch (slug per /sc:save <storage>); none → the newest session_* of any branch, reported as that branch's record; folder absent → skip
  2. Load (auto memory): MEMORY.md (auto-load) + topic files linked from MEMORY.md
  3. Discover: Proj struct + reqs (Glob/Grep/Read)
  4. Activate: Proj context + workflow prep
  5. Validate: Context integrity + session ready
  6. Session Goal (optional): If user give goal, record as 1-line objective. Show as reminder when context > 60%.
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
  - Glob/Read: memory folder + auto memory + proj file analysis
  - Grep: proj file analysis
  - Write: Checkpoint create
  </tools>

  <examples>

| Input | Output |
|---|---|
| `/sc:load` | Current dir + memory folder + auto memory |
| `/path/to/project --type project --analyze` | Specific proj + analysis |
| `session_123 --type checkpoint` | Restore checkpoint |
| `--type deps --refresh` | Fresh dep analysis |

  <example name="load-wrong-project" type="error-path">
    - Input: /sc:load /path/to/wrong/project --type project
    - Why wrong: Load context for wrong proj pollute session with irrelevant info.
    - Correct: Verify proj path first (ls, git remote -v), then /sc:load with confirmed path.
  </example>

  </examples>


  <gotchas>
  - stale-memory: Verify loaded memory vs current file state before act on it
  - dual-persistence: Check both the memory folder and auto memory for full context
  </gotchas>

  <bounds>
    <does>memory folder + auto memory load, cross-session persist, context load.</does>
    <never>modify struct, load without validation, override without checkpoint.</never>
    <fallback>Memory folder absent: auto memory + Read CLAUDE.md/PLANNING.md/TASK.md, Glob for struct. Ask user for guidance when uncertain.</fallback>
  </bounds>

  <handoff next="/sc:analyze /sc:index-repo /sc:task"/>
</component>