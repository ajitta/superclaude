---
name: confidence-check
description: Pre-start check for any work (plan, design, spec, impl). Use when user say 'confidence check', 'validate first', 'before starting work', 'before implementing', or ask to validate assumptions before plan/design/spec/impl. NOT trigger on bare 'before starting' in non-dev contexts (meetings, talks).
---
<component name="confidence-check" type="skill">

  <role>
    <mission>Stop wrong-direction work by validate assumptions BEFORE start (plan, design, spec, or impl)</mission>
  </role>

  <syntax>/confidence-check [task description]</syntax>

  <flow>
  1. Run 3 checks below w/ evidence (Grep, Glob, Read)
  2. Each: cite hard evidence (file paths, search hits, docs)
  3. All Yes → go. Any No → dig that one before impl
  </flow>

  <checks>
  1. **Already exists?** — Grep/Glob for similar artifact (code for impl, prior spec for plan, pattern for design). Found → reuse/extend, no rebuild
  2. **Fits existing context?** — Check CLAUDE.md, prior specs/plans, set patterns. No new deps/patterns/conventions when old ones work
  3. **Root cause / intent clear?** — Bug: can repro? Feature: reqs clear? Plan/design: goal + constraints clear? Else clarify first
  </checks>

  <examples>
  | Input | Output |
  |---|---|
  | `/confidence-check add retry logic to API client` | 1. grep "retry" → found in utils/http.py:42. Reuse. 2. requests already in deps. Fits. 3. Error logs show timeout pattern. Clear. → Proceed |
  | `/confidence-check add caching layer` | 1. grep "cache" → none found. New. 2. No cache deps. New pattern. 3. "Why cache?" — no perf data. → Stop, measure first |
  | `/confidence-check write plan for auth feature` | 1. specs dir: no prior auth spec. New. 2. Framework has session middleware pattern. Fits. 3. Goal: multi-tenant auth. Clear. → Proceed |
  | `/confidence-check design notification system` | 1. No prior notification design. New. 2. Event bus exists (reuse). 3. Goal unclear — push? email? both? → Stop, clarify goal |
  </examples>

  <gotchas>
  - false-positive: No flag "already exists" when grep hit unrelated match (same word in comments or strings). Verify semantic match
  - skip-evidence: Never claim "fits stack" w/o actually read pyproject.toml or package.json. Cite file + line
  - scope-expansion: Confidence check = 3 questions only — no expand to full architecture review or impl plan
  </gotchas>

  <bounds>
    <does>pre-start check for any work (plan/design/spec/impl) + evidence-based checklist.</does>
    <never>score/percent compute, runtime check, modify artifact.</never>
  </bounds>

  <handoff next="/sc:implement /sc:plan /sc:design /sc:analyze"/>
</component>