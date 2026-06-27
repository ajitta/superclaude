---
description: Make detailed impl plans w/ TDD tasks, exact file paths, verify commands. Use ONLY when user explicit type `/sc:plan` — make committed plan doc under docs/plans/. NOT auto-trigger on "what's the plan" / "how should we approach this" — those get 2-3 sentence inline answer, not plan file.
---
<component name="plan" type="command">

  <role command="/sc:plan">
    <mission>Make detailed impl plans w/ TDD tasks, exact file paths, verify commands</mission>
  </role>

  <syntax>/sc:plan [spec-or-topic] [--from docs/specs/...] [--output docs/plans/...] [--phases N] [--pr-bundle]</syntax>

  <flow>
  1. Load: Read spec/reqs (from --from path or user desc)
  2. Map: List files to create/modify + their jobs
  3. Decompose: Break to phases (default) — each phase = single-commit unit on feature branch, ordered by dep. Use "Phase N" term, NOT "PR N", since plans usually run as N commits on 1 branch (single review cycle). For real multi-PR work (separate review cycles per change-set), opt-in w/ --pr-bundle.
  4. Template: Add plan header (goal, arch, tech stack)
  5. Save (routing per RULES.md `<doc_output_convention>`): on feature path, write plan to `docs/features/<slug>/05-plan.md` (frontmatter: `status: draft, revised: <today>`) AND update `docs/features/<slug>/README.md` (`updated:` bump + append entry to `## Documents`, advance `phase:` if status enum moved). On standalone path, write to `docs/plans/<feature-name>-<username>-YYYY-MM-DD.md` — no README update needed.
  6. Handoff: Ready for /sc:implement --plan
  </flow>

  <outputs>
Routing: per RULES.md `<doc_output_convention>` — feature path `docs/features/<slug>/05-plan.md` (existing folder OR user picks `[f]`) | standalone path `docs/plans/<feature-name>-<username>-YYYY-MM-DD.md` (user picks `[s]` or no related work expected). Slug resolution: exact-match silent / multi partial-match prompt / zero match → `[f]/[s]` w/ default `[f]`.

  | Artifact | Purpose |
  |---|---|
  | Feature path: `docs/features/<slug>/05-plan.md` | Phase doc when slug resolves to existing/new feature folder |
  | Standalone path: `docs/plans/<feature-name>-<username>-YYYY-MM-DD.md` | One-off plan, no related work expected |
  </outputs>


  <tools>
  - Read: Spec + codebase analysis
  - Grep/Glob: File structure map
  - Write: Plan doc make
  </tools>

  <templates>
Plan header:
  # [Feature] Implementation Plan
  **Goal:** [One sentence]
  **Architecture:** [2-3 sentences]
  **Tech Stack:** [Key technologies]

Task format:
  ### Task N: [Component]
  **Files:** Create: path | Modify: path:lines | Test: path
  - [ ] Step 1: Write failing test
  - [ ] Step 2: Verify it fails
  - [ ] Step 3: Write minimal implementation
  - [ ] Step 4: Verify it passes
  - [ ] Step 5: Commit
  </templates>

  <examples>
  | Input | Output |
  |---|---|
  | `/sc:plan --from docs/specs/auth-design-ajitta-2026-03-17.md` | TDD plan w/ Phase 1..N (single-branch default) |
  | `/sc:plan 'add user profiles'` | Plan from desc, Phase framing |
  | `/sc:plan --from REQUIREMENTS.md --output docs/plans/profiles.md` | Custom output path |
  | `/sc:plan --from docs/specs/big-refactor.md --pr-bundle` | Multi-PR plan (separate review cycles per change-set; opt-in) |
  | `/sc:plan --from docs/specs/foo.md --phases 4` | Hint preferred phase count when natural |
  </examples>

  <size_note>Plans stay under 15KB (~4K tokens). Big impls — split to phase files (e.g., plan-phase1-setup.md, plan-phase2-impl.md). Claude Code Read tool fail at 25K tokens (~100KB) — oversized plans unreadable mid-exec.</size_note>


  <gotchas>
  - existing-plan: Check if plan already exist for this feature before make new one
  - scope-match: Plan scope must match user req. No expand to adjacent features
  - phase-vs-pr: Default to "Phase N" framing — single-branch, single-review-cycle exec. Reserve "PR N" for real multi-PR work (--pr-bundle), where each change-set get own review cycle. Naming match reality — past 4-PR plans actually ran as 4 phase commits on 1 branch.
  - workflow-fanout: Under ultracode Workflow fan-out, subagents RETURN plan markdown — subprocess FS writes are discarded, so the main loop performs the native Write per the outputs routing
  </gotchas>

  <bounds>
    <does>plan make, task decompose, file map, TDD structure.</does>
    <never>write impl code, exec tasks, skip spec review.</never>
    <fallback>Ask user for spec clarify when reqs ambiguous.</fallback>
  </bounds>

  <handoff next="/sc:implement /sc:brainstorm"/>
</component>