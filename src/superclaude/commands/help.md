---
description: List all /sc commands and what each one does. Use when asked which superclaude commands exist. Not for "help me" with a task — help with the task directly.
---

<component name="help" type="command">

  <role command="/sc:help">
    <mission>List all /sc commands and what each one does</mission>
  </role>
  <syntax>/sc:help [command-name] [--flags]</syntax>


  <flow>
  1. Display: no argument → the full command list and the scope map; a command-name → that command's syntax, its flags, and the "Not for" line of its description; --flags → the flag list per the flags section
  2. Complete: end after display
  </flow>

  <flags>
  - --flags: Render the flag list from core/FLAGS.md (always loaded in context) — one line per flag, grouped by modes / MCP / execution / output. Effort levels are Claude Code native, not managed by superclaude.
  </flags>

  <commands>
    - agent: session control + workflow orchestration
    - analyze: code analysis — quality, security, perf, architecture
    - brainstorm: requirements discovery via Socratic dialogue
    - build: build, compile, package + error handling
    - business-panel: multi-expert business analysis
    - cleanup: dead code removal + structure optimization
    - design: system architecture + API design
    - document: focused doc generation
    - estimate: dev effort/complexity estimates
    - explain: code + concept explanations
    - git: smart git ops + PR integration
    - help: this command ref
    - implement: feature impl + MCP integration
    - improve: code quality + perf improvements
    - index: project docs + knowledge base
    - index-repo: compact repo index (~3KB) for cheap navigation
    - load: session context load (memory folder + auto memory)
    - pm: multi-agent orchestration for 3+ independent streams (on request)
    - recommend: smart command recs
    - reflect: task reflection + validation
    - research: deep web research, parallel search
    - save: session context persistence
    - select-tool: smart MCP tool select
    - sc: command dispatcher (main entry)
    - spec-panel: multi-expert spec review
    - task: complex task workflow mgmt
    - test: test exec + coverage analysis
    - troubleshoot: issue diagnosis + fix
    - roadmap: PRD → impl task plan
    - init: interactive project env setup
    - insight: capture structured session insights
    - intent: capture a request in the requester's own words before analysis
    - plan: detailed impl plans with TDD tasks
    - review: code review with structured feedback
    - auto-improve: autonomous overnight code improvement loop (Karpathy AutoResearch)
    - promote-feature: promote standalone docs into a feature folder
  </commands>

  <scope_map>
  Analysis: analyze (static quality metrics) | review (PR/diff-level) | reflect (post-impl self-check)
  Project mgmt: task (single-session tracking) | pm (multi-session orchestration)
  Impl: implement (write/modify code) | build (compile, package)
  Docs: document (prose for humans) | index (structured knowledge base) | index-repo (repo catalog)
  Discovery: intent (request in the requester's words, before analysis) | brainstorm (Socratic requirements) | research (evidence-based investigation)
  Advisory: business-panel (market/strategy) | spec-panel (tech spec review)
  </scope_map>

  <examples>

  <example name="help-as-execution" type="error-path">
    - Input: /sc:help implement auth (expect run /sc:implement)
    - Why wrong: help reference-only. Shows info, no exec.
    - Correct: use /sc:implement 'auth system' to run. Use /sc:help to see options.
  </example>

  </examples>

  <gotchas>
  - stale-list: cmd list may go stale. Verify against actual files in commands/sc/ if unsure
  - flag-docs: point users to core/FLAGS.md for flag docs, not inline
  </gotchas>

  <bounds>
    <does>displays the full reference, a categorized flag list and usage examples.</does>
    <never>executes commands, creates files, activates modes, or modifies project state.</never>
  </bounds>

  <handoff next="/sc:recommend /sc:[command]"/>
</component>