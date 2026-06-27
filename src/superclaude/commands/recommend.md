---
description: Ultra-intelligent command recommendation engine for optimal SuperClaude command selection. Use when the user types `/sc:recommend` or asks "which /sc:* command fits my situation?". Do NOT auto-trigger when the right command is already obvious from the user's request — invoke that command directly instead.
---
<component name="recommend" type="command">

  <role command="/sc:recommend">
    <mission>Ultra-smart cmd rec engine for best SuperClaude cmd pick</mission>
  </role>

  <syntax>/sc:recommend [request] [--estimate] [--alternatives] [--expertise beginner|intermediate|expert]</syntax>

  <flow>
  1. Analyze: user req + proj ctx
  2. Classify: category + skill lvl
  3. Map: keywords → cmds + flags
  4. Rec: workflow + MCP flags + agents
  </flow>

  <keyword_map>
    - debug (error|bug|not working): /sc:troubleshoot --type bug --trace --seq
    - perf (slow|performance|optimization): /sc:analyze --focus perf
    - sec (security|auth|vulnerability): /sc:analyze --focus security --seq
    - test (test|qa|coverage|e2e): /sc:test --type e2e --coverage --play
    - web (website|frontend|ui|react): /sc:implement --type component --with-tests
    - api (api|backend|server): /sc:design --type api --seq
    - ml (machine learning|ai|model): /sc:analyze --focus quality --c7 --seq
    - learn (how|explain|tutorial): /sc:explain --level basic --format examples
    - cleanup (refactor|dead code|tech debt): /sc:cleanup --type code --safe
    - plan (workflow|plan|phases): /sc:roadmap --strategy systematic
    - deploy (deploy|ci|cd|pipeline): /sc:build --type prod --optimize
  </keyword_map>

  <project_detect>
    - react (package.json+react): --c7 --play
    - node_api (express|routes/): --seq --c7
    - python (pyproject.toml|requirements.txt): --seq
  </project_detect>

  <expertise_adapt>
    - beginner: simpler workflows, /sc:explain for concepts, --safe flags
    - intermediate: standard recs w/ MCP flags
    - expert: terse output, advanced flag combos, parallel workflows
  </expertise_adapt>

  <examples>
  | Input | Output |
  |---|---|
  | `'login page broken, blank screen'` | debug+web: /sc:troubleshoot --trace --seq → /sc:analyze --focus quality |
  | `'make dashboard load faster'` | perf: /sc:analyze --focus perf → /sc:improve --type performance |
  | `'improve the code'` | ambiguous: ask what aspect (perf/quality/security/arch) → /sc:analyze |
  </examples>


  <gotchas>
  - simplicity-bias: rec simplest first. complex multi-agent flows only when justified
  - flag-match: match flags to task needs, not max capability
  </gotchas>

  <bounds>
    <does>smart mapping, proj ctx, skill adapt.</does>
    <never>exec cmds, modify files.</never>
    <fallback>ask user clarify when req too ambiguous to map.</fallback>
  </bounds>

  <handoff next="/sc:analyze /sc:implement /sc:design /sc:troubleshoot"/>
</component>