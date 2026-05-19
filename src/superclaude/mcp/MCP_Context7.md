<component name="context7" type="mcp">
  <role>
    <mission>Official lib docs lookup + framework pattern guide</mission>
  </role>

  <call_order>
  1. `resolve-library-id` — search lib name → get Context7-compat ID (format: `/org/project`).
  2. `query-docs` — query docs w/ resolved ID.
  </call_order>

  Never call `query-docs` w/o first resolve lib ID, unless user give one.

  <choose>
  <use>version-specific API sigs w/ exact param types + return vals, official migration paths between lib versions, framework-canonical patterns (React hooks, Vue composition, Angular services — official way), lib-specific auth flow impl (OAuth, JWT, session), correct build-tool / bundler / linter config opts.</use>
  <never>general prog concepts (recursion, design patterns, algos — native Claude), debug help (stack traces, error analysis — Sequential or native), code-quality + security review (native Claude), non-lib questions on sys design or arch.</never>
  </choose>

  <token_management>
  - Default: 10,000 tokens per query (enough most lookups).
  - Cut to 5,000: simple API sig checks.
  - Bump to 20,000: complex integration patterns, multi-step tutorials.
  - Max 3 calls per question — if no find after 3, use best result.
  </token_management>

  <version_pinning>
  - `resolve-library-id` returns avail versions.
  - Use `/org/project/version` format for version-specific docs.
  - When user give version, always pin in query.
  </version_pinning>

  <integration_patterns>
  - Implementation: Context7 → verify API → `/sc:implement` (official patterns first).
  - Migration: Context7:old-version → Context7:new-version → diff → `/sc:plan`.
  - Debugging: Context7 → confirm expected behavior → compare w/ actual → `/sc:troubleshoot`.
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
    <does>official lib docs, version-specific APIs, framework compliance, migration guides.</does>
    <never>general concepts, debugging, code review, arch decisions.</never>
    <fallback>Use WebSearch for non-lib docs, WebFetch for specific URLs.</fallback>
  </bounds>

  <handoff next="/sc:implement /sc:analyze /sc:research"/>
</component>