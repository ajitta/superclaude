---
description: Pick the tool for an operation by operation type and the MCP servers connected in this session, with a native fallback. On request only — the user's /sc:select-tool or a workflow step that names it. Not for normal tool selection — choose from context.
---
<component name="select-tool" type="command">

  <role command="/sc:select-tool">
    <mission>Pick the tool for an operation by operation type and the MCP servers connected in this session, naming the native fallback when the preferred tool is absent.</mission>
  </role>

  <syntax>/sc:select-tool [operation] [--analyze] [--explain]</syntax>

  <flow>
  1. Parse: read the operation, its scope, and the file count from the request.
  2. Classify: operation type, matched to one row of the decision matrix.
  3. Check: the chosen tool is connected in this session (tool list, deferred tools, or skill list); a tool that is not connected is named, and the fallback in its row is used instead.
  4. Select: state the tool, the fallback when one is used, and the reason in one line.
  </flow>

  <flags>
  - --analyze: show the decision matrix row that matched and the facts behind it: operation type, scope, and whether the preferred tool is connected.
  - --explain: explain the choice in plain terms, including why the runner-up loses.
  </flags>

  <decision_matrix>
| Operation type | Preferred tool | Fallback when not connected |
|---|---|---|
| Symbol ops (rename, references, definitions) | symbol-aware tool (LSP or code index) | Grep every occurrence, review each, then Edit |
| Text-pattern edits | Grep to confirm the targets, then Edit | none needed (native) |
| Library or API docs | Context7 (--c7) | WebSearch/WebFetch on the official docs |
| Web search or page extraction | Tavily skills or Tavily MCP (--tavily) | WebSearch/WebFetch |
| Browser, E2E, or visual checks | Playwright (--play) | say it is not connected; ask the user to run the check |
| Performance metrics (LCP, CLS, traces) | Chrome DevTools (--perf) | say it is not connected; ask for a Lighthouse or profiler report |
| Session memory | /sc:save, /sc:load | none needed (native) |
| Preferred tool not connected | name the tool, use the fallback in its row, and say so | — |
  </decision_matrix>

  <examples>

| Input | Output |
|---|---|
| `'rename function across 10 files' --analyze` | Symbol op: LSP rename when connected; otherwise Grep every occurrence, then Edit |
| `'update console.log to logger.info' --explain` | Text-pattern edit: Grep the targets, then Edit |
| `'how does React useTransition work'` | Library docs: Context7 (--c7) when connected; otherwise WebFetch the React docs |
| `'check the checkout flow in a browser'` | Browser check: Playwright (--play); not connected → say so and ask the user to run it |

  <example name="wrong-tool-choice" type="error-path">
    - Input: /sc:select-tool 'rename a variable across the project' → suggests one bulk text replace
    - Why wrong: a rename is a symbol op; a bulk text replace also changes matches in strings and comments.
    - Correct: symbol-aware rename (LSP) when connected; otherwise Grep every occurrence and review each before Edit.
  </example>
  </examples>


  <gotchas>
  - native-first: recommend native tools (Grep, Glob, Read, Edit) when they cover the operation; recommend an MCP server only for a row that needs one, and state why.
  - not-connected: a server named in the matrix may be absent from this session; never recommend a tool the Check step did not find without saying it is not connected.
  </gotchas>

  <bounds>
    <does>maps an operation to one matrix row, checks that the tool is connected, and names the fallback.</does>
    <never>override the user's explicit tool preference, or recommend a tool that is not connected without saying so.</never>
  </bounds>

  <handoff next="/sc:implement /sc:analyze"/>
</component>