---
description: Create detailed implementation plans with TDD tasks, exact file paths, and verification commands
---
<component name="plan" type="command">

  <role>
    /sc:plan
    <mission>Create detailed implementation plans with TDD tasks, exact file paths, and verification commands</mission>
  </role>

  <syntax>/sc:plan [spec-or-topic] [--from docs/specs/...] [--output docs/plans/...] [--phases N] [--pr-bundle]</syntax>

  <flow>
  1. Load: Read spec or requirements (from --from path or user description)
  2. Map: List files to create/modify and their responsibilities
  3. Decompose: Break into phases (default) — each phase is a single-commit unit on a feature branch, ordered by dependency. Use "Phase N" terminology, NOT "PR N", since plans typically execute as N commits on one branch (single review cycle). For genuine multi-PR work (separate review cycles per change-set), opt-in with --pr-bundle.
  4. Template: Add plan header (goal, architecture, tech stack)
  5. Save: Write to docs/plans/<feature-name>-<username>-YYYY-MM-DD.md (with frontmatter: status: draft, revised: <today>)
  6. Handoff: Ready for /sc:implement --plan
  </flow>

  <outputs>
  | Artifact | Purpose |
  |---|---|
  | `docs/plans/<name>-<username>-YYYY-MM-DD.md` | Implementation plan with TDD tasks |
  </outputs>


  <tools>
  - Read: Spec and codebase analysis
  - Grep/Glob: File structure mapping
  - Write: Plan document creation
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
  | `/sc:plan --from docs/specs/auth-design-ajitta-2026-03-17.md` | TDD plan with Phase 1..N (single-branch default) |
  | `/sc:plan 'add user profiles'` | Plan from description, Phase framing |
  | `/sc:plan --from REQUIREMENTS.md --output docs/plans/profiles.md` | Custom output path |
  | `/sc:plan --from docs/specs/big-refactor.md --pr-bundle` | Multi-PR plan (separate review cycles per change-set; opt-in) |
  | `/sc:plan --from docs/specs/foo.md --phases 4` | Hint preferred phase count when natural |
  </examples>

  <size_note>Plans should stay under 15KB (~4K tokens). For large implementations, split into phase files (e.g., plan-phase1-setup.md, plan-phase2-impl.md). Claude Code's Read tool fails at 25K tokens (~100KB) — oversized plans become unreadable mid-execution.</size_note>


  <gotchas>
  - existing-plan: Check if a plan already exists for this feature before creating a new one
  - scope-match: Plan scope must match user request. Do not expand into adjacent features
  - phase-vs-pr: Default to "Phase N" framing — single-branch, single-review-cycle execution. Reserve "PR N" for genuine multi-PR work (--pr-bundle), where each change-set gets its own review cycle. Source: 2026-04-25 retrospective §5.1 (4-PR plan was actually executed as 4 phase commits on 1 branch — naming should match reality).
  </gotchas>

  <bounds>
    <should>plan creation, task decomposition, file mapping, and TDD structure.</should>
    <avoid>write implementation code, execute tasks, and skip spec review.</avoid>
    <fallback>Ask user for spec clarification when requirements are ambiguous.</fallback>
  </bounds>

  <handoff next="/sc:implement /sc:brainstorm"/>
</component>
