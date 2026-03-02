<component name="context7" type="mcp">
  <role>
    <mission>Official library documentation lookup and framework pattern guidance</mission>
  </role>

  <choose>
- Curated docs: Version-specific documentation over WebSearch
- Official patterns: Implementation must follow official patterns
- Frameworks: React hooks, Vue composition API, Angular services
- Libraries: Correct API usage, auth flows, configuration
- Compliance: Adherence to official standards
  </choose>

  <examples>
| Input | Output | Reason |
|-------|--------|--------|
| implement React useEffect | Context7 | official React patterns |
| add Auth0 authentication | Context7 | official Auth0 docs |
| migrate to Vue 3 | Context7 | official migration guide |
| just explain this function | Native Claude | no external docs needed |
  </examples>

  <workflows>
    <library_resolution>
1. resolve-library-id: search by name → get Context7-compatible ID
2. query-docs: use resolved ID + specific question → get curated docs
3. Apply: implement using returned patterns and code snippets
Note: always resolve ID first — direct queries without ID will fail
    </library_resolution>
    <version_specific>
- /org/project/version for pinned versions (e.g., /vercel/next.js/v14.3.0)
- Omit version suffix for latest stable; query both versions when migrating
    </version_specific>
  </workflows>

  <scenarios>
    <multi_library>
Scenario: OAuth with Next.js + Auth0
1. Resolve next.js → /vercel/next.js, auth0 → /auth0/docs
2. Query next.js: "middleware authentication pattern"
3. Query auth0: "Next.js SDK setup and callback configuration"
4. Cross-reference results for compatible integration
    </multi_library>
    <framework_migration>
Scenario: Vue 2 Options API → Vue 3 Composition API
1. Resolve vue → /vuejs/docs
2. Query: "composition API migration from options API"
3. Apply returned patterns file-by-file, validating each conversion
    </framework_migration>
  </scenarios>

  <tool_guide>
- resolve-library-id: max 3 calls per question; select by reputation + snippet count
- query-docs: max 3 calls per question; be specific in query phrasing
- Fallback: if Context7 lacks coverage, use WebSearch with site:docs.* filter
- Combine with --seq for complex integration patterns spanning multiple libraries
  </tool_guide>
</component>
