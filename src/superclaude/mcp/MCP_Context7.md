<component name="context7" type="mcp">
  <role>
    <mission>Official library documentation lookup and framework pattern guidance</mission>
  </role>

  <call_order>
  1. `resolve-library-id` — search library name → get Context7-compatible ID (format: `/org/project`).
  2. `get-library-docs` — query documentation with the resolved ID.
  </call_order>

  Never call `get-library-docs` without first resolving the library ID, unless the user provides one explicitly.

  <choose>
  <use>version-specific API signatures with exact parameter types and return values, official migration paths between library versions, framework-canonical patterns (React hooks, Vue composition, Angular services — the official way), library-specific auth flow implementation (OAuth, JWT, session), and correct build-tool / bundler / linter configuration options.</use>
  <never>general programming concepts (recursion, design patterns, algorithms — native Claude), debugging help (stack traces, error analysis — Sequential or native), code-quality and security review (native Claude), and non-library questions about system design or architecture.</never>
  </choose>

  <token_management>
  - Default: 10,000 tokens per query (sufficient for most lookups).
  - Reduce to 5,000: simple API signature checks.
  - Increase to 20,000: complex integration patterns, multi-step tutorials.
  - Max 3 calls per question — if not found after 3, use the best available result.
  </token_management>

  <version_pinning>
  - `resolve-library-id` returns available versions.
  - Use `/org/project/version` format for version-specific docs.
  - When the user specifies a version, always pin it in the query.
  </version_pinning>

  <integration_patterns>
  - Implementation: Context7 → verify API → `/sc:implement` (official patterns first).
  - Migration: Context7:old-version → Context7:new-version → diff → `/sc:plan`.
  - Debugging: Context7 → confirm expected behavior → compare with actual → `/sc:troubleshoot`.
  </integration_patterns>

  <examples>
| Input | Action | Reason |
|---|---|---|
| implement React useEffect | resolve("react") → query(id, "useEffect cleanup") | Official hook patterns |
| add Auth0 to Next.js | resolve("auth0") → query(id, "Next.js integration") | Auth flow specifics |
| upgrade Vue 2 to Vue 3 | resolve("vue", version=v3) → query(id, "migration from Vue 2") | Version-specific migration |
| explain closures | Skip Context7, use native Claude | General CS concept |
  </examples>

  <bounds>
    <does>official library docs, version-specific APIs, framework compliance, and migration guides.</does>
    <never>general concepts, debugging, code review, and architecture decisions.</never>
    <fallback>Use WebSearch for non-library docs, WebFetch for specific URLs.</fallback>
  </bounds>

  <handoff next="/sc:implement /sc:analyze /sc:research"/>
</component>
