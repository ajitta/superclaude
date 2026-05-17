---
status: complete
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
| Q1 | Where in command body does path-resolution logic live? | Cite-only — 1-line ref in existing `<outputs>` table header per Q4 SSOT (no new `<output_routing>` section, no per-command duplication, cuts R-2 drift risk + keeps command body ≤200-line target) | delegated |
| Q2 | How does command know which feature slug to use? | Conversation-aware w/ disambiguation: exact slug match → silent use; multiple partial-match → prompt candidate list; zero match → standalone-vs-feature prompt | delegated |
| Q3 | Standalone vs feature decision flow? | Heuristic + per-command default: feature-default for brainstorm/design/plan/workflow (multi-doc by nature); standalone-default for research/analyze (often one-off). Override via 1-line `[f]/[s]` prompt | delegated |
| Q4 | Phase-prefix mapping SSOT? | RULES.md `<doc_output_convention>` (already shipped Phase 1); commands cite "per RULES.md `<doc_output_convention>`" — no duplication | delegated |
| Q5 | Commit strategy? | Single PR, checkpoint-gated: commit brainstorm.md alone first → smoke test → only if green, add 5 replication commits in same PR. If smoke fails, abort PR. Markdown-only so revert-safe | delegated |
| Q6 | Smoke-test slug? | `test-feature-folder-temp` — kebab-compliant per 04-design.md feature-slug rule; `-temp` suffix flags ephemeral (leading `_` would violate kebab-case) | delegated |
| Q7 | brainstorm.md flow step 4 self-edit shape? | Path-conditional prose + R4 README update threaded inline. Step 4 carries write-path decision AND README index regen call | delegated |
| Q8 | Frontmatter delta for phase docs? | Phase doc gets `{status: draft, revised: <today>}`; standalone unchanged | delegated |

## Requirements

### R1. Output routing cite per command (cite-only, no new section)

Per Q4 SSOT principle: commands MUST NOT restate routing prose. Each of 6 commands gets a 1-line header note prepended to its existing `<outputs>` table body:

> Routing: per RULES.md `<doc_output_convention>` — feature path `docs/features/<slug>/NN-<phase>.md` (existing folder OR user picks `[f]`) | standalone path `docs/<type>/<slug>-<suffix>-<username>-YYYY-MM-DD.md` (user picks `[s]` or no related work expected).

Slug resolution rule (applies before routing): exact slug match against `docs/features/` dir names → silent use; multiple partial-match → prompt candidate list ("matched: foo-refactor, foo-rework; pick [1]/[2]/new"); zero match → 1-line `[f]/[s]` prompt with per-command default ([f] for brainstorm/design/plan/workflow; [s] for research/analyze). User skip = take default.

No separate `<output_routing>` section. Routing is a behavior rule already owned by RULES.md SSOT — duplicating to 6 command bodies would (a) violate Q4, (b) raise R-2 drift risk 6×, (c) push command bodies toward xml-prose-format ≤200-line ceiling.

### R2. `<flow>` step that mentions write path updates to conditional shape + threads R4 README update

Flow step MUST cover routing decision AND (on feature path) README index regen — both inline so R4 is not implicit aspiration.

Example (brainstorm.md step 4):

> Specify (routing per RULES.md `<doc_output_convention>`): on feature path, write spec to `docs/features/<slug>/01-discovery.md` (frontmatter: `status: draft, revised: <today>`) AND update `docs/features/<slug>/README.md` (`updated:` bump + append entry to `## Documents`, advance `phase:` if status enum moved). On standalone path, write to `docs/specs/<topic>-discovery-<username>-YYYY-MM-DD.md` — no README update needed.

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

- [ ] All 6 commands' `<outputs>` table prepended with 1-line routing cite to RULES.md `<doc_output_convention>` (cite-only, no new `<output_routing>` section)
- [ ] All 6 commands' `<flow>` write-step shows conditional path shape AND (feature-path branch) calls README index regen per R4
- [ ] All 6 commands' `<outputs>` table rows updated per R3 (both feature + standalone path columns)
- [ ] Slug-resolution rule honored: exact-match silent / multi partial-match prompt / zero match → per-command default
- [ ] Smoke test: `/sc:brainstorm 'foo' --feature test-feature-folder-temp` writes `docs/features/test-feature-folder-temp/01-discovery.md` + updates that README's `## Documents` index + bumps `updated:` frontmatter
- [ ] Smoke commit lands BEFORE 5 replication commits (Q5 checkpoint gate)
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

None — v2 resolved all 5 review findings (2 critical + 3 important). Re-review pass clean before `/sc:plan` handoff.

## Self-Review Iteration Log

- v1 (2026-05-18 01:55 GMT+9): initial draft. Pending `/sc:review`.
- v2 (2026-05-18 02:08 GMT+9): `/sc:review --audit-delegated` findings applied. Delta:
  - **C1** (Q1↔Q4 contradiction): adopted cite-only — dropped `<output_routing>` section requirement; rewrote R1 to 1-line cite in existing `<outputs>` table header. Cuts R-2 drift risk 6×.
  - **C2** (Q6 kebab-case violation): smoke slug `_test-feature-folder` → `test-feature-folder-temp`. Updated Q6, Success Criteria, + `05-plan.md` L87.
  - **I1** (Q2 disambiguation): added slug-resolution rule (exact / multi-partial / zero) to R1 + Q2.
  - **I2** (Q3 default): added per-command defaults — `[f]` for brainstorm/design/plan/workflow, `[s]` for research/analyze.
  - **I3** (R4 thread): R2 flow-step example now inlines README update call on feature path.
  - **S2** (Q5 checkpoint): commit brainstorm.md alone → smoke → only-if-green replicate 5. Abort-on-fail clause added.
  - S1 (drop `<output_routing>` section) folded into C1 fix.

## Handoff

→ `/sc:review` re-pass on v2 → `/sc:plan` if clean.

mandatory: 8 delegated decisions need independent audit (v2 incorporates v1 audit findings)
