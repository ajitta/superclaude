---
description: Create detailed implementation plans with TDD tasks, exact file paths, and verification commands
---
<component name="plan" type="command">

  <role>
    /sc:plan
    <mission>Create detailed implementation plans with TDD tasks, exact file paths, and verification commands</mission>
  </role>

  <syntax>/sc:plan [spec-or-topic] [--from docs/specs/...] [--output docs/plans/...]</syntax>

  <flow>
    1. Load: Read spec or requirements (from --from path or user description)
    2. Map: List files to create/modify and their responsibilities
    3. Decompose: Break into tasks — each is a single action (2-5 min), checkbox syntax, exact paths, complete code
    4. Template: Add plan header (goal, architecture, tech stack)
    5. Save: Write to docs/plans/<feature-name>-<username>-YYYY-MM-DD.md (with frontmatter: status: draft, revised: <today>)
    6. Handoff: Ready for /sc:implement --plan
  </flow>

  <outputs>
  | Artifact | Purpose |
  |----------|---------|
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
  |-------|--------|
  | `/sc:plan --from docs/specs/auth-design-ajitta-2026-03-17.md` | TDD plan from spec |
  | `/sc:plan 'add user profiles'` | Plan from description |
  | `/sc:plan --from REQUIREMENTS.md --output docs/plans/profiles.md` | Custom output path |
  </examples>

  <size_note>Plans should stay under 15KB (~4K tokens). For large implementations, split into phase files (e.g., plan-phase1-setup.md, plan-phase2-impl.md). Claude Code's Read tool fails at 25K tokens (~100KB) — oversized plans become unreadable mid-execution.</size_note>

  <token_note>Medium consumption — scales with spec complexity</token_note>

  <bounds will="plan creation|task decomposition|file mapping|TDD structure" wont="write implementation code|execute tasks|skip spec review" fallback="Ask user for spec clarification when requirements are ambiguous"/>

  <handoff next="/sc:implement /sc:brainstorm"/>
</component>
