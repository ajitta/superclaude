---
name: confidence-check
description: Pre-start validation checklist for any work (plan, design, spec, implementation).
when-to-use: >
  When user says 'confidence check', 'validate first', 'before starting',
  'before implementing', or wants validation before starting any work
  (plan, design, spec, or implementation).
---
<component name="confidence-check" type="skill">

  <role>
    <mission>Prevent wrong-direction execution by validating assumptions BEFORE starting work (plan, design, spec, or implementation)</mission>
  </role>

  <syntax>/confidence-check [task description]</syntax>

  <flow>
    1. Run 3 checks below with evidence (Grep, Glob, Read)
    2. For each: cite concrete evidence (file paths, search results, docs)
    3. All Yes → proceed. Any No → investigate that item before implementing
  </flow>

  <checks>
  1. **Already exists?** — Grep/Glob for similar artifact (code for implementation, prior spec for plan, existing pattern for design). If found, reuse or extend instead of building new
  2. **Fits existing context?** — Check CLAUDE.md, prior specs/plans, established patterns. Don't introduce new deps/patterns/conventions when existing ones work
  3. **Root cause / intent understood?** — Bug: can you reproduce? Feature: clear requirements? Plan/design: clear goal + constraints? If not, clarify first
  </checks>

  <examples>
  | Input | Output |
  |-------|--------|
  | `/confidence-check add retry logic to API client` | 1. grep "retry" → found in utils/http.py:42. Reuse. 2. requests already in deps. Fits. 3. Error logs show timeout pattern. Clear. → Proceed |
  | `/confidence-check add caching layer` | 1. grep "cache" → none found. New. 2. No cache deps. New pattern. 3. "Why cache?" — no perf data. → Stop, measure first |
  | `/confidence-check write plan for auth feature` | 1. specs dir: no prior auth spec. New. 2. Framework has session middleware pattern. Fits. 3. Goal: multi-tenant auth. Clear. → Proceed |
  | `/confidence-check design notification system` | 1. No prior notification design. New. 2. Event bus exists (reuse). 3. Goal unclear — push? email? both? → Stop, clarify goal |
  </examples>

  <gotchas>
  - false-positive: Do not flag "already exists" when grep finds unrelated matches (same word in comments or strings). Verify semantic match
  - skip-evidence: Never claim "fits stack" without actually reading pyproject.toml or package.json. Cite file and line
  - scope-expansion: Confidence check is 3 questions only — do not expand into full architecture review or implementation planning
  </gotchas>

  <bounds should="pre-start validation for any work (plan/design/spec/implementation)|evidence-based checklist" avoid="score/percentage computation|runtime checks|modify artifact"/>

  <handoff next="/sc:implement /sc:plan /sc:design /sc:analyze"/>
</component>
