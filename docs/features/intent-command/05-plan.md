---
status: draft
revised: 2026-10-07
---

# `/sc:intent` Implementation Plan

**Goal:** 요청을 분석 전에 요청자의 표현 그대로 다섯 항목으로 기록하는 `/sc:intent` 커맨드를 추가하고, brainstorm·review·reflect가 그 파일을 의도의 원본으로 읽게 한다.

**Architecture:** 커맨드는 `src/superclaude/commands/intent.md` 한 파일이다(XML 컴포넌트, 플래그 없음). 산출물은 `docs/features/<slug>/00-intent.md`이며 RULES_DOCS의 phase prefix 체계 맨 앞에 `00-intent`를 추가한다. 소비자는 세 커맨드의 flow 한 줄씩이다. 커맨드 이름은 디스크에서 읽히므로(`context_loader._known_command_names`) 레지스트리 등록은 없고, README의 커맨드 수와 컴포넌트 맵의 수만 갱신한다.

**Tech Stack:** Markdown + XML 컴포넌트, pytest 구조 테스트(`test_command_structure.py`, `test_cross_references.py`, `test_version_consistency.py`), `superclaude install --force --scope local`.

## Scope

In: 커맨드 파일, 문서 규약(phase prefix, phase enum, workflow gate), 소비자 3곳, 색인 4곳, 카운트 6곳, CHANGELOG, 로컬 재동기화.

Out (R18 미통과, 별도 결정 필요): `--from <ticket|file>` 플래그, standalone 경로(`docs/specs/*-intent-*`), Maintain 단계에서 사고를 00-intent로 되돌리는 경로, canary probe. 소비자 없이 산출물만 늘리는 변경은 넣지 않는다.

## Design decisions (locked)

- 이름 `/sc:intent`, 파일 `00-intent.md`. `00`은 기존 `01-discovery`보다 앞에 정렬되고 "분석 전"이라는 뜻을 번호가 그대로 보여 준다.
- 트리거 티어는 explicit-only. 커밋 산출물을 쓰므로 command-authoring 규칙의 "writes committed artifacts → explicit-only"에 해당한다.
- 플래그 없음. `<syntax>`는 `/sc:intent [request]`뿐이라 `<flags>` 섹션도 두지 않는다.
- Feature README `phase` enum에 `intent`를 추가한다(discovery 앞). 00-intent만 있는 폴더의 phase가 `discovery`로 표시되는 거짓말을 피하기 위해서다.
- 적용 티어: Large 체인 필수, Medium 선택, Trivial·Small 해당 없음. README 티어 표는 Large 행과 전체 체인 다이어그램만 바꾼다.

## Risks

- brainstorm-lite로 번질 위험: flow에 "해결책·대안·아키텍처·범위 추가 금지", 질문 최대 5개, 한 페이지 상한을 명시하고 `<never>`와 `<gotchas>`에 중복해 둔다.
- `test_every_readme_component_count_matches_source`가 커맨드 파일을 추가하는 순간 red가 된다. 의도된 순서다(Task 1 → Task 2).
- phase enum 사본: `.claude/superclaude/core/rules/RULES_DOCS.md`는 설치 사본이라 `src`만 고치고 재동기화로 맞춘다. 다른 사본은 grep으로 확인했고 `src`에 하나뿐이다.
- `<flow>` 단계 참조 규칙: 다른 커맨드에서 이 커맨드의 단계를 가리킬 때는 `the /sc:intent Save step` 형식만 허용된다(`test_command_structure.py`가 `step N`을 거부).
- description 1024자 상한.

## Alternatives not taken

- `/sc:brainstorm --capture-only`: 소크라테스 탐색 기계 전체가 같이 로드되고, "요청자의 말을 바꾸지 않는다"는 계약이 탐색 흐름과 충돌한다.
- 템플릿 파일만 제공(커맨드 없음): 빈 항목을 묻고 원문을 보존하는 동작이 없어 결국 사람이 brainstorm으로 간다.

---

### Task 1: 커맨드 파일
**Files:** Create: `src/superclaude/commands/intent.md` | Test: `tests/unit/test_command_structure.py`, `tests/unit/test_cross_references.py`
- [ ] Step 1: 아래 사양으로 파일 작성 (실패 테스트 = 구조 테스트가 새 파일을 자동 수집)
- [ ] Step 2: `uv run pytest tests/unit/test_command_structure.py tests/unit/test_cross_references.py -q` → green. `test_version_consistency.py`는 이 시점에 red여야 정상(Task 2에서 해소)
- [ ] Step 3: 커밋 없이 Task 2로

사양:

- frontmatter `description` (explicit-only + 부정 게이트, ≤1024자):
  `Capture a request as an intent record in the requester's own words — problem, proposed outcome, affected users and systems, constraints, open questions — before any analysis. Use ONLY when user explicitly types /sc:intent — writes docs/features/<slug>/00-intent.md, so a wrong fire creates a file unasked. Do NOT auto-trigger on "I want X" statements, feature ideas mentioned in passing, or requests to explore or design — those get a direct answer or /sc:brainstorm.`
- `<role command="/sc:intent"><mission>`: description과 단어 30% 이상 공유.
- `<syntax>/sc:intent [request]</syntax>`
- `<flow>`:
  1. Capture: 사용자 문장을 원문 그대로 seed로 둔다. 바꿔 쓰지 않는다.
  2. Fill: 다섯 항목 중 원문이 비운 항목에 대해서만 질문한다. 항목당 하나, 총 5개 이내. 사용자가 "충분하다"고 하면 멈춘다.
  3. Draft: 다섯 항목을 사용자의 표현을 인용해 채운다. 해결책, 대안, 아키텍처, 범위 추가 없음. 한 페이지 상한.
  4. Approve: 초안을 보이고 사용자가 문장을 고친다. 확인 없이는 쓰지 않는다.
  5. Save: `docs/features/<slug>/00-intent.md` (slug 해석은 core/rules/RULES_DOCS.md, zero-match 기본 `[f]`); frontmatter `status: draft`, `revised`; 폴더가 새로 생기면 README를 `phase: intent`로 만든다.
  6. Handoff: Large는 /sc:brainstorm, Medium은 /sc:plan에 00-intent를 입력으로 넘긴다.
- `<outputs>`: `docs/features/<slug>/00-intent.md` 한 줄과 본문 골격(`# Intent: <title>` / Author, Status / `## Problem` / `## Proposed outcome` / `## Affected users and systems` / `## Constraints` / `## Open questions`).
- `<tools>`: Read(기존 폴더·README 확인), Write(산출물), AskUserQuestion(Fill 단계).
- `<examples>`: 요청 한 줄 → 질문 2개 → 00-intent 저장; 이미 폴더가 있는 slug → 기존 README 갱신.
- `<gotchas>`: solution-creep(제안을 끼워 넣음 → 삭제하고 Open questions로), rephrase-drift(사용자 표현을 매끄럽게 고침 → 원문 인용 복원), question-flood(항목이 찼는데 계속 질문 → Draft로).
- `<bounds>`: `<does>` 원문 보존 캡처, 빈 항목 질문, 승인 후 저장. `<never>` 해결책·대안·아키텍처 제안, 범위 확장, 승인 전 저장, 탐색(brainstorm) 대행. `<fallback>` 요청이 Trivial·Small이면 파일을 만들지 말고 그렇게 말한다.
- `<handoff next="/sc:brainstorm /sc:plan /sc:design"/>`
- 본문 ≤100줄 목표(상한 200).

### Task 2: 카운트 갱신 (36 → 37)
**Files:** Modify: `README.md:28` (배지 표), `README.md:33`, `README.md:93`, `README.md:135`, `README.md:515` | `docs/codex/prompting_session_raw/02_component_and_delivery_map.md:24` | Test: `tests/unit/test_version_consistency.py`
- [ ] Step 1: Task 1 직후 `uv run pytest tests/unit/test_version_consistency.py -q` 가 red임을 확인
- [ ] Step 2: 여섯 곳의 수를 `ls src/superclaude/commands/*.md | grep -vc README` 결과로 바꾼다 (값을 외우지 않는다)
- [ ] Step 3: 같은 테스트 green

### Task 3: 문서 규약
**Files:** Modify: `src/superclaude/core/rules/RULES_DOCS.md:13` (phase prefix), `:45` (phase enum), `:65-74` (workflow_gates) | `src/superclaude/commands/promote-feature.md:17` (type→phase 매핑) | Test: `uv run pytest tests/unit -q -k "docs or rules or promote"`
- [ ] Step 1: phase prefix 목록 맨 앞에 `00-intent (intent)` 추가
- [ ] Step 2: Feature README phase enum을 `intent | discovery | design | planning | implementing | complete | abandoned`로
- [ ] Step 3: workflow_gates 첫 줄에 `/sc:intent -> /sc:brainstorm | /sc:plan: User approves the intent text in their own words; file committed before analysis starts` 추가
- [ ] Step 4: promote-feature 매핑에 `intent→00-intent.md` 추가
- [ ] Step 5: 관련 테스트 green

### Task 4: 소비자 세 곳
**Files:** Modify: `src/superclaude/commands/brainstorm.md:13` (Explore 단계), `src/superclaude/commands/review.md:15` (Gather 단계), `src/superclaude/commands/reflect.md` (Validate 단계) | Test: `tests/unit/test_command_structure.py`
- [ ] Step 1: brainstorm Explore 단계에 "같은 slug의 `00-intent.md`가 있으면 먼저 읽고, 각 항목을 어떻게 구체화했는지 01-discovery에 'Intent coverage' 표로 남긴다" 추가
- [ ] Step 2: review Gather 단계의 관련 문맥에 `00-intent.md`를 추가하고, Review-2D의 Dim 1(spec fidelity)이 spec뿐 아니라 00-intent와 대조하도록 한 구절 추가
- [ ] Step 3: reflect Validate 단계에 "00-intent.md가 있으면 Proposed outcome과 실제 결과를 대조해 차이를 적는다" 추가
- [ ] Step 4: 단계 참조는 `the /sc:intent Save step` 형식만 사용; `uv run pytest tests/unit/test_command_structure.py -q` green

### Task 5: 색인과 README 체인
**Files:** Modify: `src/superclaude/commands/README.md` (Planning 표), `src/superclaude/commands/help.md:25,66`, `src/superclaude/commands/sc.md:21`, `README.md:240` (Large 행), `README.md:245` (체인 다이어그램), `README.md:252` 앞 (하드 게이트 표 새 행), `README.md:606` (Planning & Design 목록)
- [ ] Step 1: 네 색인에 `/sc:intent` 한 줄씩 (설명: "Capture a request in the requester's own words before analysis")
- [ ] Step 2: README Large 체인을 `/sc:intent` → `/sc:brainstorm` → … 로, Medium 행에는 "(선택: `/sc:intent` 먼저)" 주석
- [ ] Step 3: 하드 게이트 표에 행 추가: `/sc:intent` | `docs/features/<slug>/00-intent.md` | User approves the wording; committed before analysis
- [ ] Step 4: `uv run pytest tests/unit/test_version_consistency.py tests/unit/test_cross_references.py -q` green

### Task 6: CHANGELOG
**Files:** Modify: `CHANGELOG.md`
- [ ] Step 1: 다음 버전 섹션(버전 범프 브랜치에서 생성)의 `### Added`에 `/sc:intent` 항목과 `00-intent` phase, `intent` phase enum 추가. `## [Unreleased]` 헤딩은 쓰지 않는다 — `test_version_consistency.py`가 날짜 있는 릴리스 헤딩만 인식한다
- [ ] Step 2: `uv run pytest tests/unit/test_version_consistency.py -q` green

### Task 7: 동기화와 전체 검증
**Files:** none (설치 사본 갱신)
- [ ] Step 1: `superclaude doctor --scope local` 로 local scope 설치 확인 후 `superclaude install --force --scope local`
- [ ] Step 2: `echo '{"prompt":"/sc:intent test"}' | superclaude hook context_loader` 출력에 "is not a command"가 없어야 함
- [ ] Step 3: `uv run pytest` exit 0, `make lint` clean
- [ ] Step 4: `/sc:intent`를 실제로 한 번 실행해 Trivial 요청에는 파일을 만들지 않고, Large 요청에는 질문 5개 이내로 00-intent.md를 만드는지 확인. 결과를 이 문서의 "Proof"에 적는다
- [ ] Step 5: `feat: add /sc:intent command` 로 커밋, 이 plan의 체크박스 갱신과 README `phase: implementing → complete` 를 같은 커밋에

## Proof

- 구조·교차참조·카운트 테스트 green (명령과 출력을 여기 붙인다)
- Task 7 Step 2 훅 출력
- Task 7 Step 4 실행 기록: 요청 원문, 질문 수, 생성된 파일 경로, 사용자가 고친 문장 수
