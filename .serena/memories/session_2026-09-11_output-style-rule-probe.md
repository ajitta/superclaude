# Session 2026-09-11 evening — Plain Language style: rule-level probe, closing and dash rules rewritten

Live session (about 20:50–21:45 KST); everything below was observed in-session, not reconstructed. The research doc and auto memory were updated as the work went; this file records what they do not.

## Tree state, verified at save
`uv run pytest` → 2618 passed / 25 skipped / 0 failed (run after the last doc edit). `make format` → 340 files unchanged. `ruff check` not run this session. `pyproject.toml` `4.12.0+ajitta`. master = origin/master = `d7b4150`, pushed 21:35. Branch `fix/output-style-closing-and-dash-rules` left in place after a fast-forward merge (no `integration` branch exists locally). Working tree clean.

## What was asked, in order (all user directives, no pushback, no corrections)
1. "현재의 output style을 평가하라 테스트 예제를 만들어서" → rule-level A/B probe, assessment only.
2. "마무리 제안 규칙 문구 수정" → closing rule rewritten, re-measured.
3. "한국어 목록의 줄표 문제" → dash rule rewritten, three wordings measured.
4. "스타일 원본과 연구 문서 두 파일의 변경을 검토하고 커밋" → fix branch, one commit.
5. "master로 병합" → fast-forward. 6. "push" → already up (a first push had landed at 21:35:33).

## Landed: `d7b4150` fix(output-style): name the failing shapes in the closing and dash rules
`src/superclaude/output-styles/plain-language.md` (four paragraphs) and `docs/research/plain-language-output-style-chosh1179-2026-09-11.md` §5. Per-run numbers, the three dash wordings and the two deletion-test cuts are in §5 — read it, do not restate.

## Method, reusable
- Probe from an empty scratch dir: `claude -p "<prompt>" --model <m> --output-format text`; style condition = the file at `<dir>/.claude/output-styles/plain-language.md` plus `--settings '{"outputStyle":"Plain Language"}'`. Injection canary held (style condition quoted "Write natural, direct prose in the user's language."; default said NO OUTPUT STYLE, then mistook the auto-mode Bash instruction block for a style — harmless).
- Regex counters (headers, bullets, bold, em dash, negative parallelism, signposts, previews, closers on the last 3 lines, generalization words, 합니다/해요 endings, 번역투 patterns, plural -들, style mention) followed by a full read of every output. Regex missed "That's not X — it's Y" and "좁혀드릴게요": counts are direction only.
- Discipline that held: fix on the failing prompt and on a second prompt family; ≥3–5 runs per wording on Opus 5; Fable 5.1 only for over-suppression (its default is already clean). Variance: one wording gave 0 and 6 dashes in adjacent runs.
- Fixtures were session scratch and are gone. Prompts verbatim, for re-measurement:
  - T01 ko: 세션 저장소로 Redis랑 Memcached 중 뭘 써야 해? 단일 리전, 동시 세션 10만 개, 세션에 장바구니 데이터도 들어가.
  - T02 en: Make the case for migrating our mobile app's backend from REST to GraphQL.
  - T03 ko: 쿠버네티스에서 파드가 CrashLoopBackOff 상태야. 원인 찾는 순서 알려줘.
  - T04 ko: OAuth 2.0의 PKCE가 왜 필요한지, 어떻게 동작하는지 설명해줘.
  - T05 en: Context: you just renamed getUser to fetchUser in src/api/users.ts, src/hooks/useUser.ts and tests/users.test.ts, then ran `npm test` (41 passed, 0 failed). Write the message you would send me to report this work.
  - T06 ko: 이 에러 고쳐줘. TypeError: Cannot read properties of undefined (reading 'map')
  - T07 en: Our nightly CI build takes 45 minutes now, up from 12 minutes a month ago. Nothing in the pipeline config changed. What's going on?
  - T08 en: Is it still worth learning Rust in 2026?
  - T09 ko: 내일 오전 10시 주간 회의 취소한다는 메일 짧게 써줘. 다음 주에 다시 잡을 예정이야.
  - T10a en: Compare PostgreSQL, MySQL and SQLite as a local cache for a small CLI tool. Give me a comparison table.
  - T10b ko: pre-commit으로 커밋 전에 ruff 자동 실행하게 세팅하는 단계별 명령어 알려줘.
  - T11 en: Here is a paragraph from our incident postmortem: 'At 14:02 UTC the primary database exhausted its connection pool because a deploy at 13:55 doubled the number of worker processes without raising max_connections. Failover did not trigger since the primary was still answering health checks.' Summarize it in two sentences and quote the sentence that states the root cause.
  - T12 ko (added for the dash rule): HTTP 상태 코드 401, 403, 404, 409, 422, 429의 차이와 각각 언제 쓰는지 알려줘.

## Decisions and why
- Closing rule consolidated into the Work-reports paragraph with the replacement action ("Otherwise state what you assumed and stop: …"). The failing shape was a polite invitation ("원하시면 ~해 드릴게요", "~하고 싶으면 말씀해 주세요") that the model reads as register, not as an offer; the passing Fable answer already stated its assumption and stopped.
- Dash rule names three positions (heading, bold term, list label). "a list label takes a colon" emptied the bullets and the dashes moved into bold leads and headings; "a label and its explanation" did not move them; naming the positions did.
- Two sentences cut for the 600-word cap, both deletion-test duplicates: "or an introductory roadmap", "Choose precise common words over inflated stock language". Body 598.
- Iteration on the dash rule stopped after the third wording, announced in advance, independent of the result.

## Set aside by judgment, not done
- Bold as inline heading ("**1. 설치**") persists in both conditions; the §3 residual and the Fable over-correction warning still apply. Untouched.
- Blocker asks on the CI prompt now read "Paste X and I'll narrow it" (2 of 2): permitted by the rule, offer-like in form. Not iterated.
- "state the claim as your own" produced "실무에서 제 경험상" once (0 of 2 on repeat). Watch condition, no edit.
- Opus under the style squeezed three parallel causes into one 첫째/둘째/셋째 paragraph twice; Fable lengthened the PKCE answer 358→485 words by turning bullets into prose. Recorded only.
- One T12 run answered in 평서체 while every other Korean run used 합니다체; n=1, the prompt itself was 반말. Not attributed to the wording.

## Corrections review
None to record: the session had directives only.

## Open
- Vault copy `~/ObsidianVault/.claude/output-styles/plain-language.md` holds the bilingual Korean draft (vault commit `d23533f` 16:50; no later vault commit touches it, latest backup `a3f5f6d` 21:32) while the vault's `settings.json` selects "Plain Language". The earlier 09-11 save's "overwritten with the global version" did not persist; annotated there in place. Whether to copy the shipped file over is the user's call.
- Insight pending queue: 9 entries at save (8 at session start plus the closing-rule INSIGHT, harvested 21:28). The dash-rule INSIGHT line was **not** harvested (the Stop hook only requested one on the closing-rule turn); the lesson lives in auto memory `project_output_styles_component.md` and in this file.
- §5 numbers are one evening, n=3–5 per cell, single wording per row.
- Carried unchanged from the earlier 09-11 save: feature folders at planning/analysis, the 09-03 CS-D pair and `max_turns` items.
