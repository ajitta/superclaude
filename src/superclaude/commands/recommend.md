---
description: Ultra-intelligent command recommendation engine for optimal SuperClaude command selection
---
<component name="recommend" type="command">
  <config style="Telegraphic|Imperative|XML" eval="true"/>
  <runtime model="opus-4-5" effort="low"/>

  <role>
    /sc:recommend
    <mission>Ultra-intelligent command recommendation engine for optimal SuperClaude command selection</mission>
  </role>

  <syntax>/sc:recommend [request] [--estimate] [--alternatives] [--stream] [--expertise beginner|intermediate|expert]</syntax>

  <triggers>
    - Command recommendation requests
    - Help choosing approach
    - Project planning assistance
  </triggers>

  <flow>
    1. **Analyze**: User request + project context
    2. **Classify**: Category + expertise level
    3. **Map**: Keywords → commands + personas
    4. **Recommend**: Flow + MCP + flags
  </flow>

  <keyword_map>
    - **ml** (machine learning|ml|ai|model): /sc:analyze --seq --c7|/sc:design --seq --ultrathink
    - **web** (website|frontend|ui|react|vue): /sc:build --feature --magic|/sc:test --e2e --pup
    - **api** (api|backend|server|microservice): /sc:design --api --ddd --seq|/sc:build --feature --tdd
    - **debug** (error|bug|issue|not working): /sc:troubleshoot --investigate --seq|/sc:analyze --code
    - **perf** (slow|performance|optimization): /sc:analyze --performance --pup --profile|/sc:improve --performance
    - **sec** (security|auth|vulnerability|owasp): /sc:scan --security --owasp --deps|/sc:analyze --security
    - **test** (test|qa|coverage|e2e): /sc:test --coverage --e2e --pup|/sc:scan --validate
    - **learn** (how|learn|explain|tutorial): /sc:document --user --examples|/sc:brainstorm --interactive
  </keyword_map>

  <project_detect>
    - **react** (package.json+react|src/App.jsx): --magic --c7 --pup
    - **node_api** (express|server.js|routes/): --seq --c7
    - **python** (requirements.txt|setup.py|main.py): --seq
  </project_detect>

  <expertise_flags>
    - **beginner**: --tutorial --examples --step-by-step
    - **intermediate**: --guided --examples
    - **expert**: --advanced --no-explanations
  </expertise_flags>

  <examples>

| Input | Output |
|-------|--------|
| `'I want to do machine learning'` | ML-Beginner → analyze+design flow |
| `'my site is very slow'` | Perf-Urgent → analyze+troubleshoot+improve |
| `'building e-commerce' --estimate` | Multi-domain → design+build+scan + timeline |

  </examples>

  <bounds will="intelligent mapping|project context|expertise adaptation" wont="execute commands|make assumptions without context"/>
</component>
