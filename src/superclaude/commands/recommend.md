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

  <mcp servers="seq|c7"/>
  <personas p="pm|arch"/>

  <tools>
    - Read: Project file detection (package.json, pyproject.toml, etc.)
    - Glob: Project structure analysis
    - Grep: Dependency + framework detection
  </tools>

  <keyword_map>
    - ml (machine learning|ml|ai|model): /sc:analyze --focus quality --c7 --seq|/sc:design --type architecture
    - web (website|frontend|ui|react|vue): /sc:implement --type component --with-tests|/sc:test --type e2e --play
    - api (api|backend|server|microservice): /sc:design --type api --seq|/sc:implement --type api --with-tests
    - debug (error|bug|issue|not working): /sc:troubleshoot --type bug --trace --seq|/sc:analyze --focus quality
    - perf (slow|performance|optimization): /sc:analyze --focus perf --perf|/sc:improve --type performance
    - sec (security|auth|vulnerability|owasp): /sc:analyze --focus security --seq|/sc:improve --type quality --safe
    - test (test|qa|coverage|e2e): /sc:test --type e2e --coverage --play|/sc:analyze --focus quality
    - learn (how|learn|explain|tutorial): /sc:explain --level basic --format examples|/sc:brainstorm --depth deep
    - cleanup (refactor|dead code|unused|tech debt): /sc:cleanup --type code --safe|/sc:analyze --focus quality
    - plan (workflow|plan|prd|phases): /sc:workflow --strategy systematic|/sc:estimate --type effort --breakdown
    - deploy (deploy|ci|cd|pipeline|infra): /sc:build --type prod --optimize|/sc:troubleshoot --type deployment
    - git (commit|branch|pr|merge): /sc:git --smart-commit|/sc:git --pr-status
  </keyword_map>

  <project_detect>
    - react (package.json+react|src/App.jsx): --magic --c7 --play
    - node_api (express|server.js|routes/): --seq --c7
    - python (requirements.txt|pyproject.toml|main.py): --seq
  </project_detect>

  <expertise_adapt>
    - beginner: Recommend simpler workflows, suggest /sc:explain for concepts, prefer --safe flags
    - intermediate: Standard recommendations with relevant MCP flags
    - expert: Terse output, advanced flag combinations, parallel workflows
  </expertise_adapt>

  <patterns>
    - Keyword: Request text → domain classification → command mapping
    - Project: File detection → framework identification → MCP flag selection
    - Multi-Domain: Overlapping keywords → workflow sequencing
    - Expertise: User level → output verbosity + flag complexity
  </patterns>

  <examples>

  <example name="keyword-detection" type="happy-path">
    <input>/sc:recommend 'my login page is broken and sometimes shows a blank screen'</input>
    <reasoning>Keywords: 'broken' → debug, 'login page' → web, 'blank screen' → debug+web overlap</reasoning>
    <output>
      Matched: debug + web domains
      Primary: /sc:troubleshoot --type bug --trace --seq (diagnose blank screen root cause)
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
      Primary: /sc:analyze --focus perf --perf (Core Web Vitals audit)
      Follow-up: /sc:improve --type performance (apply optimizations)
      Then: /sc:test --type e2e --play (verify no regressions)
      Flags: --c7 (Next.js optimization patterns), --magic (lazy-loaded components)
    </output>
  </example>

  <example name="multi-domain" type="happy-path">
    <input>/sc:recommend 'build e-commerce with Stripe payments' --estimate</input>
    <reasoning>Multi-domain: web + api + sec. --estimate requested</reasoning>
    <output>
      Matched: web + api + sec domains
      Workflow:
        1. /sc:design --type api --seq (payment architecture)
        2. /sc:implement --type feature --safe --with-tests (Stripe integration)
        3. /sc:analyze --focus security (PCI compliance check)
        4. /sc:test --type e2e --play (checkout flow validation)
      Follow-up: /sc:estimate --type effort --breakdown
    </output>
  </example>

  <example name="ambiguous-request" type="error-path">
    <input>/sc:recommend 'improve the code'</input>
    <reasoning>No specific keywords matched, no domain signal, too vague</reasoning>
    <output>
      Matched: none (ambiguous)
      Clarification: "What aspect would you like to improve?"
        - Performance → /sc:analyze --focus perf → /sc:improve --type performance
        - Code quality → /sc:analyze --focus quality → /sc:improve --type quality
        - Security → /sc:analyze --focus security → /sc:improve --type quality --safe
        - Architecture → /sc:analyze --focus arch → /sc:design --type architecture
      Suggestion: Run /sc:analyze first for a broad assessment
    </output>
  </example>

  </examples>

  <token_note>Low consumption — recommendation-only, no file modifications</token_note>

  <bounds will="intelligent mapping|project context|expertise adaptation" wont="execute commands|make assumptions without context" fallback="Ask user for guidance when uncertain"/>

  <boundaries type="document-only">Provide recommendations only, then complete | Do not execute recommended commands automatically | Do not modify files or project state → Output: Prioritized command recommendations with justification</boundaries>


  <handoff next="/sc:analyze /sc:implement /sc:design /sc:troubleshoot /sc:help"/>
</component>
