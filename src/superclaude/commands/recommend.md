---
description: Recommend the best SuperClaude command for a situation. Use when asked which /sc:* command fits. Not for a request whose command is already obvious — run that command.
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

  <flags>
  - --estimate: add an effort estimate for the recommended command sequence.
  - --alternatives: list other viable commands with a one-line trade-off each.
  - --expertise beginner|intermediate|expert: explanation depth per the expertise adaptation section.
  </flags>

  <keyword_map>
    - debug (error|bug|not working): /sc:troubleshoot --type bug --trace
    - perf (slow|performance|optimization): /sc:analyze --focus perf
    - sec (security|auth|vulnerability): /sc:analyze --focus security
    - test (test|qa|coverage|e2e): /sc:test --type e2e --coverage --play
    - web (website|frontend|ui|react): /sc:implement --type component --with-tests
    - api (api|backend|server): /sc:design --type api
    - ml (machine learning|ai|model): /sc:analyze --focus quality --c7
    - learn (how|explain|tutorial): /sc:explain --level basic --format examples
    - cleanup (refactor|dead code|tech debt): /sc:cleanup --type code --safe
    - plan (workflow|plan|phases): /sc:roadmap --strategy systematic
    - deploy (deploy|ci|cd|pipeline): /sc:build --type prod --optimize
  </keyword_map>

  <project_detect>
    - react (package.json+react): --c7 --play
    - node_api (express|routes/): --c7
  </project_detect>

  <expertise_adapt>
    - beginner: simpler workflows, /sc:explain for concepts, --safe flags
    - intermediate: standard recs with MCP flags
    - expert: terse output, advanced flag combos, parallel workflows
  </expertise_adapt>

  <examples>
  | Input | Output |
  |---|---|
  | `'login page broken, blank screen'` | debug+web: /sc:troubleshoot --trace → /sc:analyze --focus quality |
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