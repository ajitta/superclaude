# Session 2026-03-23: Model-Agnostic Compatibility

## Goal
Make SuperClaude framework model-agnostic — remove all Opus 4.6 hardcoded assumptions so it works correctly on Sonnet, Haiku, or any future model.

## Status: DELIVERED

## Key Decisions
1. **Full inherit**: Removed `model:` field from all 22 agents — sub-agents inherit parent session's model
2. **No exceptions**: Even repo-index (previously pinned sonnet) now inherits — simpler, no cost surprises
3. **Anti-over-engineering**: Kept 7 proven rules, changed note to model-agnostic, added `<model_tendencies>` self-calibration (+30 tokens)
4. **No detection mechanism**: Models self-identify; framework uses hybrid notes, not conditional logic
5. **Source of truth**: Neither README nor frontmatter was correct — rebuilt from first-principles (task nature determines model need)

## Changes (30 files, commit 725589b)
- 22 agent .md files: removed `model:` frontmatter line
- RULES.md: `note="Scope discipline"` + model_tendencies section
- PRINCIPLES.md: thinking_strategy + multimodal notes generalized
- FLAGS.md: 5 Opus references removed, routing simplified
- MODE_Token_Efficiency.md: generalized token note
- simplicity-guide.md: `note="Common over-engineering tendencies"`
- agent-authoring.md: `model: required` → `optional`
- agents/README.md: Model column removed, new routing section
- Spec + Plan documents created

## Design Philosophy
"Remove model assumptions, don't add model-conditional logic."

## Verification
- Tests: 1,666 passed, 12 pre-existing failures, 0 new failures
- Grep audit: 0 "Opus" references in core/agents/modes
- Deployed: v4.3.0+ajitta

## Artifacts
- Spec: docs/specs/2026-03-23-model-agnostic-compatibility-design-chosh1179.md
- Plan: docs/plans/2026-03-23-model-agnostic-compatibility-chosh1179.md
