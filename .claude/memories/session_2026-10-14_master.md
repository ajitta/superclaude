branch: master @7ac473cd

# Session 2026-10-14 — master (after the authoring-skill merge)

## Where it stands
- master @7ac473cd, 5 commits ahead of origin, NOT pushed (user approval pending)
  - ed9e182e fix(sc-author): scope output-style rules to the responses they are for
  - 128425de test(evals): measure sc-author per type with skeleton and reference checks
  - 92becf6d fix(sc-author): find commands and subagents kept in subfolders
  - merges 91dd2aa6, 7ac473cd (branches deleted)
- Suite before last commit: 3262 passed / 3 skipped, `make lint` clean (no `src/superclaude/scripts/` change, scripts suite not needed)
- Worktree `.claude/worktrees/authoring-skill` and branch `feature/authoring-skill` deleted (fully merged). `feature/portable-authoring-skill` (6 docs commits, local only) left alone: content moved to ajitta/lean-author
- Not released: latest tag v4.26.1. Core `RULES_DOCS.md` changed since → `make canary-gates` required before `make release`

## sc-author effect probes (detail: `docs/features/authoring-skill/05g-plan-probes.md` Results)
- `author-check` cannot separate skill from plain (both 0/0). Added a skeleton check: result must not contain `<component`, `<mission>`, `<bounds>`, `[Rnn` (copied SC skeleton = D22 failure)
- run4 agent: skill 4/4 (`<agent>/<role>/<task>/<return>`), plain 3/4 (copied SC skeleton) — first measured effect
- run5: 8 tasks (command, output-style, skill, rules file × skill/plain), each + one check from the type's reference, checks fixed before the run. Only agent separated by checks; plain runs of other types did not copy the skeleton
- Content audit (same model family, 1 run each — observation, not independent review): skill better for agent and memory, about equal for command and skill, worse for output-style before the fix
- Skill-type description check widened to `use (when|before|for|after)` after "Use before…" failed it (noted in `evals/tasks.yaml` comment)
- Runs dirs: `C:/tmp/sc-evals/sc-author-run4` … `run7` (outside ~/.claude); sonnet, local `claude -p`, ~$0.25 per task

## Fixed in sc-author
- Output style: "Open every reply with the findings" governed every response in the session → `references/output-style.md` Pitfall: name when a rule for one kind of response applies. run6: 5/5, style split into "When you review a migration" / "Everything else"
- Subfolders: `references/command.md`/`agent.md` read only `*.md` at top level; SC commands sit in `.claude/commands/sc/` → command came out md against D21. Now `**/*.md` (CC docs: command subfolder = namespace; `.claude/agents/` scanned recursively). `author-check` `infer_type` also typed `/agents/<sub>/x.md` as generic → now agent (test added, red before fix). run7: reads `.claude/commands/sc/explain.md`, XML body from reference skeleton, 5/5

## Problems hit
- Chained `diff -rq …; git worktree remove …; git branch -d …` in one call: removal ran despite 5 reported diffs. After-the-fact check: CRLF-only, nothing lost. Feedback memory `check-then-delete-separate-calls`
- YAML double-quoted `cmd` in `evals/tasks.yaml`: regex needs `\\[R\\d\\d`; sed/heredoc stripped backslashes → use the Edit tool. `[[]` avoids backslashes but raises Python's nested-set FutureWarning
- New inline-code example path in a reference (`.claude/commands/frontend/component.md`) drew `N1 warning: does not exist` → reworded without a path

## Next actions
- [ ] `git push origin master` (user approval)
- [ ] `make canary-gates` (inside a session: `EVAL_ARGS="--runs-dir <dir outside ~/.claude>"`), read the report
- [ ] Version-bump branch 4.27.0: CHANGELOG `### Added` from `docs/features/authoring-skill/05-plan.md` "Release note"; narrow its effect sentence to what the probes showed (agent, memory, output-style after fix; command and skill ≈ plain). Merge, `make release`, then `make sync-local`
- [ ] Optional: decide `feature/portable-authoring-skill` (delete or merge its 6 docs commits)
- [ ] Stale claude-mem work_state entry `authoring-skill` under scope `superclaude/authoring-skill` (old worktree project) cannot be closed from the main tree; ignore
