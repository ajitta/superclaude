branch: feature/authoring-skill @e850f657

# Session 2026-10-13 — feature/authoring-skill

## Where it stands
- Worktree `.claude/worktrees/authoring-skill`, branch has no upstream, NOT pushed. Use the worktree's own `.venv` (`unset VIRTUAL_ENV` first)
- master 32432c27 (v4.26.1) merged in @1f55b9a5; suite 3000 passed / 1 skipped, `tests/unit/scripts` 149, ruff clean
- Phase: design (`docs/features/authoring-skill/`), no implementation yet
- Untracked `.serena/memories/session_2026-10-10_authoring-skill-design.md` left on purpose (older decision log; `.serena/` is no longer read)

## Commits this session
- 1f55b9a5 merge master
- d0914981 / e8bcaf36 / 87704903 `00-intent.md` (rebuilt from 04-design §1 quotes, then answers + constraints)
- cf0e5780 04-design D11 (examples 3-5) + D12 (latest-model guides) + C4 split to `04a-design-checker.md`
- ba88edd3 `RULES_DOCS.md` size bands (25,000 B target / 30,000 B guard, never cut untouched content) + gotcha `size-target-no-collateral-cut`
- e850f657 D13 reframe + SC-own-docs excluded + `03-analysis.md` (no-op criteria)

## Decided (user, quoted in 00-intent.md)
- sc-author = SuperClaude-coupled; lean-author has "처리할 수 있는 하네스도 없다"
- Explicit `/sc-author` only, so it does not clash with skill-creator-style meta skills; their output still gets reformatted + validated
- Role: "skill-creator 종류가 충분히 잘 만들거라고 생각한다. 그것을 재형식화하고 no-op들을 제거하는 과정" — not "compatibility"
- Examples in references: only where needed, 3-5 (D11)
- Guidance must follow the latest Fable/Opus/Sonnet guides, never stale (D12): `sources:` per reference, model rules only in `quality.md` "모델별 차이", test ties its model IDs to `/sc:prompt` Resolve
- D13: target = any text Claude reads as instruction/context, NOT a growing type list ("mode, mcp, hook 에 대해 해당 대상을 명시적으로 규정해서 superclaude에 맞추려는 목적이 아니다")
- SuperClaude's own docs are out of scope ("sc 프로젝트를 위한 내용은 이 프로젝트에만 남아 있어") → repo `.claude/rules/*-authoring.md` stay

## Mistakes this session (don't repeat)
- Trimmed two unrelated existing lines of 04-design.md to fit 25KB → reverted; rule + gotcha now cover it
- Read the scope widening as a type list (mode/MCP/hook as new types) → user corrected (D13)

## No-op sample findings (03-analysis.md; reported, NOT fixed — user to decide)
- Harmful: auto memory `project_serena-mcp-followups.md` + its MEMORY.md line say PR-A/PR-B "still queued" (Serena removed)
- Contradictions: `AGENTS.md:7` vs `:14` (python -m pytest), `.claude/rules/agent-authoring.md:57` "cost nothing" vs `content-quality.md:15,80`, `src/superclaude/agents/business-panel-experts.md:51-52` Ask First vs Never
- Also: simplicity-guide instructs Context7 without the tool; `S390` evidence id is not a commit

## Next actions
- [ ] Finish 04-design §9 "남은 미결" (D13): move the design center to the common pass (reformat + no-op removal); add a load-set step after Resolve (C2); add checker rules for pointer resolution, instructed tools vs `tools`, opposite-slot contradiction (04a); judgment checks via `quality.md` + D12; update §6, C7, §10. Input: `03-analysis.md` §4. Keep 04-design under 25,000 B (now ~23.6 KB) → split further rather than cut
- [ ] Then `/sc:plan` on 04-design.md + 04a-design-checker.md (also check: PowerShell `allowed-tools` syntax, Fable 5.1 guide URL)
- [ ] Ask user whether to fix the harmful sample findings above (separate scope)
- [ ] Before any release containing ba88edd3: `make canary-gates` (core changed); local scope `make sync-local` pending
- [ ] Optional, offered: canary probe in `evals/tasks.yaml` for gotcha `size-target-no-collateral-cut`
