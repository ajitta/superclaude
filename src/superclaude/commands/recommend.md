---
description: Ultra-intelligent command recommendation engine for optimal SuperClaude command selection
---
<component name="recommend" type="command">

  <role>
    /sc:recommend
    <mission>Ultra-intelligent command recommendation engine for optimal SuperClaude command selection</mission>
  </role>

  <syntax>/sc:recommend [request] [--estimate] [--alternatives] [--stream] [--expertise beginner|intermediate|expert]</syntax>

  <triggers>command recommendations|approach selection|project planning</triggers>

  <flow>
    1. Analyze: User request + project context
    2. Classify: Category + expertise level
    3. Map: Keywords → commands + personas
    4. Recommend: Flow + MCP + flags
  </flow>

  <keyword_map>
    - ml (machine learning|ml|ai|model): /sc:analyze --seq --c7|/sc:design --seq --effort max
    - web (website|frontend|ui|react|vue): /sc:build --feature --magic|/sc:test --e2e --play
    - api (api|backend|server|microservice): /sc:design --api --ddd --seq|/sc:build --feature --tdd
    - debug (error|bug|issue|not working): /sc:troubleshoot --investigate --seq|/sc:analyze --code
    - perf (slow|performance|optimization): /sc:analyze --performance --play --profile|/sc:improve --performance
    - sec (security|auth|vulnerability|owasp): /sc:analyze --focus security --seq|/sc:improve --focus security
    - test (test|qa|coverage|e2e): /sc:test --coverage --e2e --play|/sc:analyze --focus quality
    - learn (how|learn|explain|tutorial): /sc:document --user --examples|/sc:brainstorm --interactive
  </keyword_map>

  <project_detect>
    - react (package.json+react|src/App.jsx): --magic --c7 --play
    - node_api (express|server.js|routes/): --seq --c7
    - python (requirements.txt|setup.py|main.py): --seq
  </project_detect>


  <expertise_flags>
    - beginner: --tutorial --examples --step-by-step
    - intermediate: --guided --examples
    - expert: --advanced --no-explanations
  </expertise_flags>

  <examples>

| Input | Output |
|-------|--------|
| `'I want to do machine learning'` | ML-Beginner → analyze+design flow |
| `'my site is very slow'` | Perf-Urgent → analyze+troubleshoot+improve |
| `'building e-commerce' --estimate` | Multi-domain → design+build+scan + timeline |

  </examples>

  <bounds will="intelligent mapping|project context|expertise adaptation" wont="execute commands|make assumptions without context" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="document-only">Provide recommendations only, then complete | Do not execute recommended commands automatically | Do not modify files or project state → Output: Prioritized command recommendations with justification</boundaries>


  <handoff next="/sc:implement /sc:help"/>
</component>
