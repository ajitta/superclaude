---
status: draft
revised: 2026-05-18
---

# Phase 2 Discovery — Command Output Routing Updates

## Scope

Phase 2 of doc-convention-v2 rollout: update 6 file-producing command files so their `<flow>` write-step and `<outputs>` table route to feature-folder layout when context applies; standalone hybrid retained.

Files in scope:
- `src/superclaude/commands/brainstorm.md`
- `src/superclaude/commands/design.md`
- `src/superclaude/commands/plan.md`
- `src/superclaude/commands/workflow.md`
- `src/superclaude/commands/research.md`
- `src/superclaude/commands/analyze.md`

Out of scope: validator (Phase 3), bulk legacy migration (deferred), worktree-aware routing (deferred).

## Resolved Decisions

| # | Question | Decision | Mode |
|---|---|---|---|
| Q1 | Where in command body does path-resolution logic live? | New `<output_routing>` section before `<outputs>` — keeps `<flow>` clean | delegated |
| Q2 | How does command know which feature slug to use? | Conversation-aware: detect existing `docs/features/<slug>/` from context or topic; else prompt | delegated |
| Q3 | Standalone vs feature decision flow? | Heuristic — existing folder → feature; new topic → ask 1-line "[f]eature or [s]tandalone?" with rationale (≥2 docs expected → feature) | delegated |
| Q4 | Phase-prefix mapping SSOT? | RULES.md `<doc_output_convention>` (already shipped Phase 1); commands cite "per RULES.md doc_output_convention" — no duplication | delegated |
| Q5 | Commit strategy? | Single atomic PR — reviewer sees full pattern once; markdown-only so revert-safe | delegated |
| Q6 | Smoke-test slug? | `_test-feature-folder` per 05-plan.md — underscore prefix flags ephemeral | delegated |
| Q7 | brainstorm.md flow step 4 self-edit shape? | Path-conditional prose: feature-folder path OR standalone path inline, both shown | delegated |
| Q8 | Frontmatter delta for phase docs? | Phase doc gets `{status: draft, revised: <today>}`; standalone unchanged | delegated |

## Requirements

### R1. Output routing block per command

Each of 6 commands gets new `<output_routing>` section, placed immediately before `<outputs>`. Section body prose:

> If feature-folder context is in play (existing `docs/features/<slug>/` referenced in conversation, or user passes slug in topic arg), write to `docs/features/<slug>/NN-<phase>.md` using phase prefix per RULES.md `<doc_output_convention>`. Otherwise prompt: "feature folder or standalone? ([f]/[s])" — feature when ≥2 related docs expected; standalone for one-off. Standalone path: `docs/<type>/<slug>-<suffix>-<username>-YYYY-MM-DD.md`.

### R2. `<flow>` step that mentions write path updates to conditional shape

Example (brainstorm.md step 4):

> Specify: write spec to feature path `docs/features/<slug>/01-discovery.md` (frontmatter: `status: draft, revised: <today>`) OR standalone path `docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md` per `<output_routing>` decision.

### R3. `<outputs>` table updates

| Command | Feature path | Standalone path |
|---|---|---|
| brainstorm | `docs/features/<slug>/01-discovery.md` | `docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md` |
| design | `docs/features/<slug>/04-design.md` | `docs/specs/<topic>-design-<username>-YYYY-MM-DD.md` |
| plan | `docs/features/<slug>/05-plan.md` | `docs/plans/<topic>-<username>-YYYY-MM-DD.md` |
| workflow | `docs/features/<slug>/05-plan.md` (workflow = plan variant) | `docs/plans/<topic>-workflow-<username>-YYYY-MM-DD.md` |
| research | `docs/features/<slug>/02-research.md` | `docs/research/<topic>-<username>-YYYY-MM-DD.md` |
| analyze | `docs/features/<slug>/03-analysis.md` | `docs/analysis/<topic>-<username>-YYYY-MM-DD.md` |

### R4. README index maintenance

When writing to feature folder, command also updates `docs/features/<slug>/README.md`:
- Bump `updated:` frontmatter to today
- Append new doc to `## Documents` list (numbered, with date + status)
- If frontmatter `phase:` value advances per status enum, update it

### R5. Frontmatter prescription

- Feature-folder path: phase doc gets `{status: draft, revised: <today>}` (per RULES.md feature phase doc rule).
- Standalone path: existing prescription unchanged (commands that wrote frontmatter keep their existing shape; commands that didn't, still don't).

### R6. Multi-of-same-phase handling

When phase file already exists (e.g., `02-research.md` present, new research run triggered), append letter suffix: `02b-research-<distinguisher>.md`. Distinguisher = short slug from topic arg, kebab-case, ≤20 chars.

## Risks

- **R-1 Self-edit risk**: brainstorm.md is both the spec being edited AND the command invoked. Edit must preserve current flow contract (decision-mode tagging, self-review gate, handoff routing). Test: re-run `/sc:brainstorm` after edit on throwaway slug.
- **R-2 Drift between RULES.md SSOT and command bodies**: commands cite RULES.md but don't enforce — if RULES.md changes prefix mapping, commands silently use stale wording. Mitigation: Phase 3 validator catches; Phase 2 accept drift risk as documented in 05-plan.md.
- **R-3 6-file atomic commit blast radius**: single broken pattern propagates to all 6. Mitigation: write 1 file (brainstorm.md), smoke test, replicate to other 5 in same PR but separate commits.
- **R-4 README auto-update side effect**: command writes to README; if README malformed (missing `## Documents` section), command must fail loud not silent.

## Success Criteria

- [ ] All 6 commands have `<output_routing>` section citing RULES.md `<doc_output_convention>`
- [ ] All 6 commands' `<flow>` write-step shows conditional path shape
- [ ] All 6 commands' `<outputs>` table updated per R3
- [ ] Smoke test: `/sc:brainstorm 'foo' --feature _test-feature-folder` writes `docs/features/_test-feature-folder/01-discovery.md` + updates that README's `Documents` index
- [ ] `make test` passes (baseline ~1,904); markdown-only changes
- [ ] `make sync-user` deploys updated commands to `~/.claude/superclaude/commands/`
- [ ] No regression in existing `/sc:*` invocations that hit standalone path

## Verification Level

Level 1 per `<verification_ladder>` — single-file behavior change per command, no API/contract boundary. Required: typecheck + lint (`make lint`) + smoke test on throwaway feature folder. `make test` covers structural test suite for commands.

## Out of Scope (Phase 2)

- Phase 3 validator (`/sc:cleanup --type docs` extension, `/sc:promote-feature`)
- Bulk legacy migration of pre-existing `docs/{specs,plans,analysis,research}/*.md`
- Cross-feature dependency graph
- Worktree-aware doc routing
- Updating `/sc:document`, `/sc:explain`, `/sc:troubleshoot` (don't produce docs/specs|plans|analysis|research artifacts)

## Open Questions Blocking Phase 2 Execution

None — all 8 brainstorm questions delegated to ★ recommendations. Self-review may surface new ones.

## Self-Review Iteration Log

- v1 (2026-05-18 01:55 GMT+9): initial draft. Pending `/sc:review`.

## Handoff

→ `/sc:review` (mandatory before `/sc:plan`).

mandatory: 8 delegated decisions need independent audit
