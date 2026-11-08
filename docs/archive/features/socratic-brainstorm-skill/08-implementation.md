---
status: complete
revised: 2026-10-02
---

# 08 — Implementation and verification

> **Historical.** Records v1 (1.0.0), whose body is now `socratic-brainstorm` 3.0.0. Paths moved: `dist/portable-skills/` → `portable-skills/releases/`. Zips now carry a plugin manifest ([11](./11-plugin-upload.md)).

## 1. What shipped

| Path | Content |
|---|---|
| `portable-skills/socratic-brainstorm/SKILL.md` | 109 lines; frontmatter `name, description (674 chars), license, metadata` only |
| `portable-skills/socratic-brainstorm/references/question-bank.md` | six types, tactic templates, optional lenses (premortem, expert lenses from the panel commands, SCAMPER, edges), KO/EN |
| `portable-skills/socratic-brainstorm/references/brief-template.md` | verdict + brief sections, rules for refuted/risky/delegated |
| `portable-skills/socratic-brainstorm/agents/openai.yaml` | Codex display name, `allow_implicit_invocation: false` |
| `portable-skills/package.py` | stdlib validator (spec keys, name = folder, lengths, links, ≤200 body lines) + zip builder → `dist/portable-skills/<name>.zip` |
| `portable-skills/README.md` | install matrix per surface, incl. mobile |
| `tests/unit/test_portable_skills.py` | 6 tests: validator passes, YAML parses with spec keys only, Codex sidecar explicit-only, validator rejects a Claude Code-only key and a name/folder mismatch |

No change under `src/superclaude`, so no framework version bump; the skill carries its own `metadata.version: "1.0.0"`.

## 2. Verification

**Tests.** `uv run pytest -q`: full suite green (2677 passed, 25 skipped after adding the 6 new tests). Mutation check: adding `disable-model-invocation` to `ALLOWED_KEYS` makes `test_validator_rejects_claude_code_only_key` fail; reverted.

**CI.** `Tests` workflow on `feature/socratic-brainstorm-skill`: all 7 jobs green (run 37013601665). The first run failed `ruff format --check` on the new test (formatted with black locally); fixed by `ruff format`.

**Package.** `python3 portable-skills/package.py` → `ok socratic-brainstorm`; zip root is `socratic-brainstorm/` with 4 files. Frontmatter also parsed with PyYAML: keys `description, license, metadata, name`.

**Live probes**: Claude Code 2.1.284, `claude -p --model sonnet` (Sonnet 5.5), skill copied into a scratch repo's `.claude/skills/`. Multi-turn via `--resume`. n = 1 per cell unless stated. These record what happened, not rates.

| ID | Prompt | What happened |
|---|---|---|
| A | `/socratic-brainstorm 사내 점심 메뉴 추천 앱을 만들고 싶어` | Mode stated with reason, steelman with assumptions marked, "맞나요?". No probing before confirmation. |
| B | Natural language "소크라테스식으로 브레인스토밍 좀 해줘 …" (no slash) | Skill fired from wording; same opening. Five-turn continuation: one ask per turn; caught a non-answer and parked it; took a sample-size probe on "다들 코딩 배우고 싶어하잖아" ("몇 명쯤 알고 있나요?"); counterexample (a child without a laptop at the door); **contradiction surfaced by quoting both answers verbatim** ("무료니까 부담 없이 누구나…" vs "노트북 없는 애는 그냥 못 오는 거지 뭐"); on "됐어, 정리해줘" stopped at once and gave **open (aporia), not refuted**, because the stop came right after the collision. That is the rule in Step 5. |
| C | "파이썬에서 딕셔너리를 값 기준으로 정렬하는 방법 알려줘" | Skill did not fire; ordinary answer. |
| D | `/socratic-brainstorm 팀 회고를 더 재밌게…`, 7 turns | "너라면 어떻게 할 거야?" → one guiding question plus an offer to jump ahead (Rule 3). "아이디어 단계로 넘어가자" → asked for the user's 3 options first, built on each, pushed edges, then added 3 labeled "제 쪽 아이디어". "좋아" was read as moving on, not as a decision. Brief: verdict open, decisions none, options marked user's/mine, untested items listed. |
| F | stress + quick, "카페 창업 … 반박해줘" | `stress` picked with reason; falsification probe asked ("내가 틀렸구나 하게 만들 숫자나 장면"); after "그냥 잘 될 것 같아" the brief marked that belief **risky** and wrote the condition into the thesis. Verdict open. |
| Sym | Skill reached through a symlink `.claude/skills/x → ../../skills/x` | Loaded and ran. |

**Codex probes**: Codex CLI 0.158.0, `codex exec -s read-only` with model `gpt-6.1-sol`. Skill in the scratch repo's `.agents/skills/`; multi-turn via `codex exec resume <id>`.

| ID | Prompt | What happened |
|---|---|---|
| X1 | `$socratic-brainstorm 사내 점심 메뉴 추천 앱…` | Skill loaded; mode stated, steelman with the assumed purpose marked, "핵심인가요?" |
| M | `$socratic-brainstorm` + the B scenario, 5 turns | One ask per turn; evidence probe on "다들 코딩 배우고 싶어하잖아"; contradiction surfaced by quoting both answers; on "됐어, 정리해줘" the verdict was **open**, not refuted. Same outcome as Claude run B. The brief came out as a compact bullet list instead of the full template (sections merged); content stayed within the user's answers. |
| N1 | Same idea in plain words, no `$` | Skill **not** loaded (0 mentions in the transcript), as `allow_implicit_invocation: false` intends. The model still asked one question per turn on its own. |
| N2 | "딕셔너리를 값 기준으로 정렬…" | Skill not loaded. |

Consequence: on Codex, the `$socratic-brainstorm` mention is required. The README is corrected to say so.

**Defects found by probing and fixed:**

1. *Compound asks* ("어디서 사 마시고, 그걸 어떻게 알았어요?") in F and in 2/2 re-runs: one question mark, two asks. A "count question marks" rule didn't fix it (2/3 still compound). Rewriting Rule 1 as "one ask; two asks joined in one sentence count as two; offering possible answers to the same ask is fine" gave 3/3 single asks on the same prompt.
2. *Brief in a code block* (D): scrolls sideways on phones. The template now says to print plain Markdown and translate headers into the user's language. F, after the fix: plain Markdown, Korean prose.
3. *Next step as a list* (F gave two actions): template now says "one, not a list".

**Not verified here:**

- **claude.ai upload / mobile app.** Needs the account UI. The frontmatter uses only the six keys the upload accepts, and the validator enforces that. The upload itself has not been run.
- **Mobile Code tab slash registration** (anthropics/claude-code#48696) is not tested; the README tells users to invoke by wording there.
