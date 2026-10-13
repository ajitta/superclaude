branch: feature/authoring-skill @bd2132c2

# Session 2026-10-13 → 10-14: sc-author planned, implemented, reviewed, merged

## Where it stands

- MERGED into local `master` (3 `--no-ff` merges: 007be180 feature, 76420a0e docs, 8319471d D22). `master` is 34 ahead of `origin/master` a2e626b0 — NOT pushed; feature branch has no upstream
- Feature README `phase: complete`; 03/04/04a/04b `status: complete`; 05-plan + 05a–05g complete, every box checked
- Suite 3261 passed, 3 skipped; ruff format/check clean; `author-check` on SKILL.md + all references: 0 errors, 0 warnings
- Branch commits after the first review: 66c4742a (review new drafts, paraphrased repeats, omitClaudeMd) → 5cdc8893 (Bash/MCP tool guidance) → 0b474394 (Proof 6 fix) → 552aee26 (stale D2 wording, design docs complete) → bd2132c2 (D22)

## Decisions (user, exact)

- D18–D20 at /sc:implement: "참조하는 rules파일들의 formatter와 내용을 그냥 가져오면 안된다. rules파일들은 이 프로젝트에 종속된 파일들이고 만들고자하는 것은 설치되는 각각의 프로젝트를 기준으로 맥락이 맞게 생성시키는 것이다"
  - D18 (picked "구조 규칙만"): XML checks = X1 one root, X2 balanced, X7 no XML for output styles
  - D19 (picked "프로젝트 관례 우선"), narrowed by D22
  - D20: references come only from external docs (`sources` URL + date); a test bans SC vocabulary in references and SKILL.md
- D21: "default는 해당 프로젝트의 형식을 따라간다." New file with no flag takes the same-type docs' format; md only when none. Replaces D2 (md default)
- D22 (picked A): "skill의 reference가 있고 이것을 참조하여 제작해야하는데 rules authoring을 이용해서 만들어지는 문제 때문이다." Existing same-type docs give format + language only; sections, tag names, terms, fields come from the type's reference; authoring rules already in context (`.claude/rules/*-authoring.md`) do not shape the document, a conflict goes in the hand-off. Recorded in 05-plan decision table
- Tool guidance: "tools 는 agent만 있는게 아니잖아?" → agent `tools` (allow-list) and skill/command `allowed-tools` (pre-approval only), `disallowed-tools` (removes), `context: fork` (uses `agent:` subagent's tools) each documented in their reference
- Merge condition: "머지는 확인되고" — merged only after Proof 6 passed

## Problems hit → resolution

- `--tavily` delegated to the marx agent, which had no Bash/Tavily MCP → it used WebSearch silently. Lesson saved as feedback memory `flag-tool-unavailable-to-delegate`
- Proof 6 failed on the marx run: Resolve/Load-set lines never shown. A "show before drafting" instruction also failed in 2 headless runs → the three lines (Resolve, Load set, Match) now open the approval message; passed in a real `/sc-author` run
- Headless `claude -p "/sc-author …"` from Git Bash: MSYS turns `/sc-author` into `C:/Program Files/Git/sc-author`, the model then reads SKILL.md by hand and looks fine → use `MSYS_NO_PATHCONV=1`
- A project under `~/.claude/tmp` for headless probes was confusing; probe from a dir outside `~/.claude` and keep run logs outside the project dir
- I misread D20 as "exclude SC-installed agents from conventions"; the user's intent was references-first (D22)

## Findings worth keeping

- Probe inside this repo after D22: XML body (project format) with `<role>/<task>/<return>` from the agent reference, no `<component>`/`<mission>`/`<bounds>`/R-code tags; model said agent-authoring.md was not used
- Effect claim still unproven: a plain request also passes author-check 0/0 (05g:52-57); the eval probes were not re-run after 66c4742a, 5cdc8893, 0b474394, bd2132c2
- Over-build signal (reflect): N1–N4 + `--with` drew most review findings; 14 design/plan docs (~1,330 lines) vs ~600 lines shipped

## Next actions

- [ ] `git push origin master` (user approval needed)
- [ ] Before release: `make canary-gates` (core change ba88edd3); CHANGELOG from 05-plan "Release note" in the version-bump commit — the note states an effect the probes did not prove
- [ ] Optional: re-run `uv run python evals/run_eval.py --canary --task sc-author-skill --task sc-author-plain` and record in 05g
- [ ] Optional: README "At a glance" hard-codes counts (37/24/8/3) — out of scope, untouched
