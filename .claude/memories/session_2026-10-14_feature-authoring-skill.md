branch: feature/authoring-skill @bd2c7b98

# Session 2026-10-13 → 10-14: sc-author planned, implemented, reviewed

## Where it stands

- Plan `docs/features/authoring-skill/05-plan.md` (index) + `05a`–`05g`: all phases `status: complete`, every box checked. README `phase: implementing` (manual check still open)
- Commits on the branch, NOT pushed (no upstream): 764bead8 plan → b4df54c6 D18–D20 → 87ea2a13 checker core → c33ade7f N rules → bd618076 skills component → c45b96d6 references → 59e1a446 SKILL.md → 1ab46459 repo docs → dc329aa4 eval probes → 62ccdca2 D21 → bd2c7b98 review fixes
- Suite 3261 passed, 3 skipped (1 pre-existing + 2 symlink tests skipped on win32, run on Linux CI); `make lint` clean; `author-check` on SKILL.md + 7 references: 0 errors, 0 warnings

## Decisions (user, exact)

- D18–D20 at /sc:implement: "참조하는 rules파일들의 formatter와 내용을 그냥 가져오면 안된다. rules파일들은 이 프로젝트에 종속된 파일들이고 만들고자하는 것은 설치되는 각각의 프로젝트를 기준으로 맥락이 맞게 생성시키는 것이다"
  - D18 (picked "구조 규칙만"): XML checks = X1 one root, X2 balanced, X7 no XML for output styles. X3–X6 dropped (this repo's xml-prose-format conventions)
  - D19 (picked "프로젝트 관례 우선"): Load reads 1–2 of the project's same-type docs; templates only as fallback
  - D20: references come only from external docs (`sources` URL + date); a test bans SC vocabulary in references and SKILL.md; no rules→references sync line
- D21: "default는 해당 프로젝트의 형식을 따라간다." New file with no flag takes the same-type docs' format; md only when none; ask when they disagree. Replaces D2 (md default)
- Review additions: skill must be self-contained; skip author-check when `superclaude` is absent; hand-off suggests `/doctor prompt-audit <path>` (+ `claude plugin validate <skills dir>` for an unchecked skill)
- §9 open items closed: allowed-tools `PowerShell(superclaude author-check *)` (permissions docs); Fable 5.1 guide `platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1`

## Problems hit → resolution

- TAG_RE swallowed `/` of `<x a="b"/>` → lazy attribute group (corpus: every agent's `<handoff …/>`)
- Prose placeholders `docs/<slug>/`, `/sc:save <storage>` → mid-line opening tag is markup only when closed on the same line
- Void-element handling broke `commands/sc.md` `<meta>…</meta>` → void only when the body never closes that name
- Docs check: subagents DO load CLAUDE.md + rules by default (`omitClaudeMd`), contrary to 04b §3 → references follow the docs (05d Deviations)
- Eval: `.claude/` is a protected path (headless writes only under bypassPermissions) → probe target moved to `agents/`; headless has no approval turn → same pre-approval sentence in both prompts
- Bash heredoc with mixed quotes failed → write edit scripts to the scratchpad and run them

## Findings worth keeping

- Probe (sonnet, sc-full): skill and plain request both 3/3 and both pass author-check → no checker-level effect; difference is format/fit (plain copied this repo's `<component>` skeleton incl. `[R06 Scope]`). After D21 the skill's output follows the project's XML. Results in 05g
- `/doctor prompt-audit [path]` exists (CC memory docs); `/skill-doctor` only lists unused skills
- 04-design.md is 25,030 B (over the 25,000 target, under 30,000): further design content goes to 05-plan decision rows or a new 04c

## Next actions

- [ ] User: restart Claude Code, run `/sc-author agent <description>` once in a real session (05-plan Proof 6)
- [ ] Decide merge: feature/authoring-skill → master (not pushed yet)
- [ ] Before release: `make canary-gates` (branch carries core change ba88edd3); CHANGELOG from 05-plan "Release note" in the version-bump commit
- [ ] Optional: README "At a glance" hard-codes counts (37/24/8/3) — out of scope, untouched
