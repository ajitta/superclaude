<component name="context7" type="mcp">
  <role>
    <mission>Official library documentation lookup and framework pattern guidance</mission>
  </role>

  ## 2-Step Workflow (required)
  1. `resolve-library-id` — search library name → get Context7-compatible ID (format: `/org/project`)
  2. `get-library-docs` — query documentation with the resolved ID

  Never call `get-library-docs` without first resolving the library ID, unless the user provides one explicitly.

  <tools note="2 tools, strict call order — @upstash/context7-mcp v2.1.6+">
  | Tool | Purpose | Required Input |
  |---|---|---|
  | `resolve-library-id` | Name → library ID | `libraryName` |
  | `get-library-docs` | ID → documentation | `context7CompatibleLibraryID`, `topic` |
  </tools>

  **Also available as:** Remote MCP server at `https://context7.com/mcp` (no local install needed)

  <choose>
  Use:
  - Version-specific APIs: exact method signatures, parameter types, return values
  - Migration guides: official upgrade paths between versions
  - Framework patterns: React hooks, Vue composition, Angular services — official way
  - Auth flows: OAuth, JWT, session — library-specific implementation
  - Configuration: build tools, bundlers, linters — correct options

  Avoid:
  - General concepts: recursion, design patterns, algorithms → native Claude
  - Debugging help: stack traces, error analysis → Sequential or native
  - Code review: quality, security assessment → native Claude
  - Non-library questions: system design, architecture → native Claude
  </choose>

  ## Token Management
  - Default: 10,000 tokens per query (sufficient for most lookups)
  - Reduce to 5,000: simple API signature checks
  - Increase to 20,000: complex integration patterns, multi-step tutorials
  - Max 3 calls per question — if not found after 3, use best available result

  ## Version Pinning
  - `resolve-library-id` returns available versions
  - Use `/org/project/version` format for version-specific docs
  - When user specifies a version, always pin it in the query

  ## Integration Patterns
  - **Implementation**: Context7 → verify API → /sc:implement (official patterns first)
  - **Migration**: Context7:old-version → Context7:new-version → diff → /sc:plan
  - **Debugging**: Context7 → confirm expected behavior → compare with actual → /sc:troubleshoot

  <examples>
| Input | Action | Reason |
|---|---|---|
| implement React useEffect | resolve("react") → query(id, "useEffect cleanup") | Official hook patterns |
| add Auth0 to Next.js | resolve("auth0") → query(id, "Next.js integration") | Auth flow specifics |
| upgrade Vue 2 to Vue 3 | resolve("vue", version=v3) → query(id, "migration from Vue 2") | Version-specific migration |
| explain closures | Skip Context7, use native Claude | General CS concept |
  </examples>

  <bounds>
    <should>official library docs, version-specific APIs, framework compliance, and migration guides.</should>
    <avoid>general concepts, debugging, code review, and architecture decisions.</avoid>
    <fallback>Use WebSearch for non-library docs, WebFetch for specific URLs.</fallback>
  </bounds>

  <handoff next="/sc:implement /sc:analyze /sc:research"/>
</component>
