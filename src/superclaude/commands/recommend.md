---
description: Ultra-intelligent command recommendation engine for optimal SuperClaude command selection
---
<component name="recommend" type="command">

  <role>
    /sc:recommend
    <mission>Ultra-intelligent command recommendation engine for optimal SuperClaude command selection</mission>
  </role>

  <syntax>/sc:recommend [request] [--estimate] [--alternatives] [--expertise beginner|intermediate|expert]</syntax>

  <flow>
    1. Analyze: User request + project context
    2. Classify: Category + expertise level
    3. Map: Keywords → commands + flags
    4. Recommend: Workflow + MCP flags + personas
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
    - plan (workflow|plan|phases): /sc:workflow --strategy systematic
    - deploy (deploy|ci|cd|pipeline): /sc:build --type prod --optimize
  </keyword_map>

  <project_detect>
    - react (package.json+react): --magic --c7 --play
    - node_api (express|routes/): --seq --c7
    - python (pyproject.toml|requirements.txt): --seq
  </project_detect>

  <expertise_adapt>
    - beginner: Simpler workflows, /sc:explain for concepts, --safe flags
    - intermediate: Standard recommendations with MCP flags
    - expert: Terse output, advanced flag combos, parallel workflows
  </expertise_adapt>

  <examples>
  | Input | Output |
  |-------|--------|
  | `'login page broken, blank screen'` | debug+web: /sc:troubleshoot --trace --seq → /sc:analyze --focus quality |
  | `'make dashboard load faster'` | perf: /sc:analyze --focus perf → /sc:improve --type performance |
  | `'improve the code'` | ambiguous: ask what aspect (perf/quality/security/arch) → /sc:analyze |
  </examples>

  <token_note>Low consumption — recommendation-only, no file modifications</token_note>

  <bounds will="intelligent mapping|project context|expertise adaptation" wont="execute commands|modify files" fallback="Ask user to clarify when request is too ambiguous to map"/>

  <handoff next="/sc:analyze /sc:implement /sc:design /sc:troubleshoot"/>
</component>
