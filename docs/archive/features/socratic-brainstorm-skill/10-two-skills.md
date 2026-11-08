---
status: complete
revised: 2026-10-02
---

# 10 — Two skills instead of one

After comparing v1 and v2 side by side, the user judged both useful and asked for two separate skills.

## 1. Split

| Skill | Content | Version | Lineage |
|---|---|---|---|
| `socratic-brainstorm` | the v1 approach: Paul's six question types → user-first diverge → converge → verdict + brief | 3.0.0 | body of 1.0.0 (`483163c`) restored; description and intro rewritten |
| `socratic-elenchus` | the v2 approach: Plato's elenchus, aporia, no advice | 1.0.0 | `socratic-brainstorm` 2.0.0 moved with `git mv` and renamed |

`socratic-brainstorm` jumps from 2.0.0 to 3.0.0 because its behavior changes again (back to the options-and-plan flow). The `metadata.lineage` field in each SKILL.md records the history.

## 2. Honest labels

v1's first mistake was calling modern questioning "the Socratic method". The restored `socratic-brainstorm` now says what it is: *modern Socratic questioning (Paul's six types) followed by brainstorming. It borrows the spirit, not the strict method of the dialogues.* It points to `socratic-elenchus` for the strict method.

## 3. Routing between the two

Both skills can be installed together, so the descriptions must route a request to the right one. Each description lists its own trigger words and names the other skill for the other case.

Routing probe: both skills in `.claude/skills/`, `claude -p --model sonnet`, first turn only, Skill tool call read from stream-json. n = 1 per prompt.

| Prompt | Loaded |
|---|---|
| 소크라테스식 브레인스토밍 해줘. 주말 무료 코딩 교실 | socratic-brainstorm ✓ |
| 이 계획 반박해줘, 질문으로 구멍 좀 찾아줘: 카페 창업 | socratic-brainstorm ✓ |
| 질문으로 아이디어 다듬어줘: 점심 메뉴 앱 | socratic-brainstorm ✓ |
| 소크라테스 대화법으로 따져줘: 점심 메뉴 앱 | socratic-elenchus ✓ |
| 엘렌코스로 내 생각 검증해줘: 회고 | socratic-elenchus ✓ |
| 내가 말하는 '좋은 리더'가 뭔지부터 정의로 따져줘 | socratic-elenchus ✓ |
| 파이썬 리스트 중복 제거하는 법 | none ✓ |

7 of 7 routed as intended. Ambiguous wording such as a bare "소크라테스식으로 해줘" was not tested, and either skill may load for it. Naming the skill (`/socratic-elenchus`) removes the ambiguity.

Codex (`gpt-6.1-sol`): both load by `$name`. `$socratic-brainstorm` opened with a steelman and "이렇게 이해한 게 맞나요?"; `$socratic-elenchus` opened with "좋은 추천이란 무엇인가요?". The multi-turn behavior of each was probed earlier (08 for brainstorm, 09 for elenchus) and is unchanged except for the description and intro text.

## 4. Packaging

Two zips in `portable-skills/releases/`. The old `socratic-brainstorm.zip` (2.0.0, elenchus content) is replaced by the 3.0.0 build. Tests are parametrized over every skill folder, so validation and zip freshness cover both.
