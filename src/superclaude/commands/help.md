---
description: List all /sc commands + functionality. Use when user types `/sc:help` or asks what SuperClaude commands exist ("what /sc commands are there", "list superclaude commands"). NO auto-trigger on generic "help me" or task-specific how-to questions — those need direct help, not list.
---

<component name="help" type="command">

  <role command="/sc:help">
    <mission>List /sc commands + functionality</mission>
  </role>
  <syntax>/sc:help [command-name] [--flags]</syntax>


  <flow>
  1. Display: full command list
  2. Complete: end after display
  </flow>

  <commands>
    - agent: session control + workflow orchestration
    - analyze: code analysis — quality, security, perf, architecture
    - brainstorm: requirements discovery via Socratic dialogue
    - build: build, compile, package + error handling
    - business-panel: multi-expert business analysis
    - cleanup: dead code removal + structure optimization
    - design: system architecture + API design
    - document: focused doc generation
    - estimate: dev time/effort estimates
    - explain: code + concept explanations
    - git: smart git ops + PR integration
    - help: this command ref
    - implement: feature impl + MCP integration
    - improve: code quality + perf improvements
    - index: project docs + knowledge base
    - index-repo: repo indexing (94% token reduction)
    - load: session context load (Serena)
    - pm: Project Manager Agent (default orchestration)
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
    - plan: detailed impl plans w/ TDD tasks
    - review: code review w/ structured feedback
    - auto-improve: autonomous overnight code improvement loop (Karpathy AutoResearch)
    - promote-feature: promote standalone docs into a feature folder
  </commands>

  <scope_map>
  Analysis: analyze (static quality metrics) | review (PR/diff-level) | reflect (post-impl self-check)
  Project mgmt: task (single-session tracking) | pm (multi-session orchestration)
  Impl: implement (write/modify code) | build (compile, package, deploy)
  Docs: document (prose for humans) | index (structured knowledge base) | index-repo (repo catalog)
  Discovery: brainstorm (Socratic requirements) | research (evidence-based investigation)
  Advisory: business-panel (market/strategy) | spec-panel (tech spec review)
  </scope_map>

  <flags>
    <category name="Mode">
      - --brainstorm: collab discovery
      - --business-panel: multi-expert business analysis
      - --research: systematic investigation mode
      - --introspect: expose thinking
      - --task-manage: systematic org
      - --orchestrate: parallel tool optim
      - --token-efficient: 30-50% token cut
    </category>
    <category name="MCP">
      - --c7|--context7: curated docs
      - --seq|--sequential: multi-step reasoning
      - --serena: semantic + memory
      - --play|--playwright: browser automation
      - --all-mcp: all servers on
      - --no-mcp: native tools only
    </category>
    <category name="Effort">
      - Claude Code native (not managed by SuperClaude)
    </category>
    <category name="Control">
      - --delegate: sub-agent parallel proc
      - --concurrency [n]: max concurrent ops (1-15)
      - --loop: iterative improvement cycles
      - --validate: pre-exec risk assess
      - --safe-mode: max validation
    </category>
    <category name="Output">
      - --uc|--ultracompressed: symbol comms
      - --scope: file|module|project|system
      - --focus: perf|security|quality|arch|a11y|testing
    </category>
  </flags>

<priority_rules> - Safety: --safe-mode > --validate > optimization - Override: user flags > auto-detect - Effort: high > medium > low - MCP: --no-mcp beats all MCP flags - Scope: system > project > module > file
</priority_rules>

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
    <does>full ref display, categorized flag list, usage examples.</does>
    <never>exec commands, make files, activate modes, modify project state.</never>
    <fallback>ask user for guidance when unsure.</fallback>
  </bounds>

  <handoff next="/sc:recommend /sc:[command]"/>
</component>