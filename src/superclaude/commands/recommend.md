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

  <example name="keyword-detection" type="happy-path">
    <input>/sc:recommend 'my login page is broken and sometimes shows a blank screen'</input>
    <reasoning>Keywords: 'broken' → debug, 'login page' → web, 'blank screen' → debug+web overlap</reasoning>
    <output>
      Matched: debug + web domains
      Primary: /sc:troubleshoot --investigate --seq (diagnose blank screen root cause)
      Follow-up: /sc:analyze --focus quality --scope file (LoginPage component)
      Flags: --play (visual verification), --c7 (React hydration patterns)
      Project context: React detected → add --magic for component fix
    </output>
  </example>

  <example name="project-context" type="happy-path">
    <input>/sc:recommend 'make the dashboard load faster'</input>
    <reasoning>Keywords: 'faster' → perf. Project: package.json has react + next.js</reasoning>
    <output>
      Matched: perf domain + react project
      Primary: /sc:analyze --focus perf --play --devtools (Core Web Vitals audit)
      Follow-up: /sc:improve --performance (apply optimizations)
      Then: /sc:test --e2e --play (verify no regressions)
      Flags: --c7 (Next.js optimization patterns), --magic (lazy-loaded components)
    </output>
  </example>

  <example name="multi-domain" type="happy-path">
    <input>/sc:recommend 'build e-commerce with Stripe payments' --estimate</input>
    <reasoning>Multi-domain: web + api + sec. --estimate requested</reasoning>
    <output>
      Matched: web + api + sec domains
      Workflow:
        1. /sc:design --api --ddd --seq (payment architecture)
        2. /sc:implement --type feature --safe --with-tests (Stripe integration)
        3. /sc:analyze --focus security (PCI compliance check)
        4. /sc:test --e2e --play (checkout flow validation)
      Estimate: ~4-6 sessions, high complexity
    </output>
  </example>

  <example name="ambiguous-request" type="error-path">
    <input>/sc:recommend 'improve the code'</input>
    <reasoning>No specific keywords matched, no domain signal, too vague</reasoning>
    <output>
      Matched: none (ambiguous)
      Clarification: "What aspect would you like to improve?"
        - Performance → /sc:analyze --focus perf
        - Code quality → /sc:analyze --focus quality → /sc:improve
        - Security → /sc:analyze --focus security
        - Architecture → /sc:analyze --focus arch → /sc:design
      Suggestion: Run /sc:analyze first for a broad assessment
    </output>
  </example>

  </examples>

  <bounds will="intelligent mapping|project context|expertise adaptation" wont="execute commands|make assumptions without context" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="document-only">Provide recommendations only, then complete | Do not execute recommended commands automatically | Do not modify files or project state → Output: Prioritized command recommendations with justification</boundaries>


  <handoff next="/sc:implement /sc:help"/>
</component>
