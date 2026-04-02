---
name: confidence-check
description: Pre-implementation validation checklist.
when-to-use: >
  When user says 'confidence check', 'validate first', 'before implementing',
  or wants validation before starting implementation work.
---
<component name="confidence-check" type="skill">

  <role>
    <mission>Prevent wrong-direction execution by validating assumptions BEFORE implementation</mission>
  </role>

  <syntax>/confidence-check [task description]</syntax>

  <flow>
    1. Run 3 checks below with evidence (Grep, Glob, Read)
    2. For each: cite concrete evidence (file paths, search results, docs)
    3. All Yes → proceed. Any No → investigate that item before implementing
  </flow>

  <checks>
  1. **Already exists?** — Grep/Glob for similar functionality in codebase. If found, reuse or extend instead of building new
  2. **Fits existing stack?** — Check CLAUDE.md, pyproject.toml, package.json for tech stack alignment. Don't introduce new deps/patterns when existing ones work
  3. **Root cause understood?** — Bug: can you reproduce it? Feature: do you have clear requirements? If neither, clarify first
  </checks>

  <examples>
  | Input | Output |
  |-------|--------|
  | `/confidence-check add retry logic to API client` | 1. grep "retry" → found in utils/http.py:42. Reuse. 2. requests already in deps. Fits. 3. Error logs show timeout pattern. Root cause clear. → Proceed |
  | `/confidence-check add caching layer` | 1. grep "cache" → none found. New. 2. No cache deps in pyproject.toml. New pattern. 3. "Why cache?" — no perf data yet. → Stop, measure first |
  </examples>

  <bounds will="pre-implementation validation|evidence-based checklist" wont="score/percentage computation|runtime checks|modify code"/>

  <handoff next="/sc:implement /sc:plan /sc:analyze"/>
</component>
