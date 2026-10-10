---
status: implementing
revised: 2026-10-10
---

# Plain Language 문장 길이 Implementation Plan

**Goal:** Plain Language 스타일에서 문장이 기본 조건보다 길어지는 문제(L1)를 고친다. 구조(하위 단계)는 이 계획에서 다루지 않는다.

**Architecture:** [05-plan.md](./05-plan.md) Task 3의 문구 교체를 따로 떼어 실행한다. 05-plan의 Task 2가 세 번 모두 실패해 중단됐고(`b6e666a4`), 사용자가 문장 길이를 먼저 고치기로 정했다(2026-10-10). 측정 방법, 지표, 프롬프트, `measure` 함수, S4~S6과 L1의 정의는 05-plan을 그대로 쓴다. 모델은 `claude-sonnet-5-5`, 기본 조건과 수정 전 스타일은 `out-base`([06-measurement.md](./06-measurement.md))다.

**Branch:** `fix/plain-language-structure`

## 05-plan과 달라진 판정 기준

- **구조 기준:** 수정 전 스타일도 S1 하위 단계에서 실패한다. 그래서 S1 하위 단계는 판정에서 빼고, 나머지 S1~S3 셀(단계, 표, 원인 목록)은 05-plan 정의대로 통과해야 한다.
- **진입 조건:** 이미 충족됐다. 수정 전 스타일에서 r ≥ 1.15인 프롬프트는 5개(en-steps, ko-steps, en-causes, en-narrative, ko-narrative)다.
- **통과 조건:** L1 통과(r ≥ 1.15 프롬프트 3개 미만, 평균 r ≤ 1.05), 구조 기준 통과, S4~S6 통과(수정 전 스타일 대비)를 모두 만족해야 한다.
- **과교정:** 스타일 `words` 합계가 기본 조건 합계(2938.2)의 70%인 2056.7 아래면 과교정이다.

## Tasks

- [ ] Task 1: 시도 A. `:23` 첫 문장 끝 "do not turn concision into fragments"를 "split a sentence that joins two conditions"로 바꾼다(본문 598 → 599단어).
  - `uv run pytest tests/unit/test_output_style_structure.py -q`가 통과해야 한다.
  - `measure p3-a "$P/prompts.tsv" "style"`로 측정하고 위 통과 조건으로 판정한다.
  - 통과하면 Task 2를 건너뛴다(`- [x] ~~…~~`, Deviations에 이유).
- [ ] Task 2: 시도 B (A가 L1에서만 실패했을 때). `:7` 둘째 문장 "Keep enough detail to be useful; brevity must not make the response abrupt or incomplete."를 "Keep the detail the request needs and no more."로 바꾼다(599 → 593단어). `p3-b`로 측정한다. 과교정이면 B를 되돌린다.
- [ ] Task 3: 기록과 커밋.
  - 시도별 문구와 수치를 `06-measurement.md`에 적는다.
  - `uv run pytest`가 0으로 끝나고 `make lint`가 통과해야 한다.
  - Commit `fix(output-style): split long sentences in Plain Language`.
- [ ] Task 4: local scope 동기화.
  - `superclaude doctor --scope local`로 확인한 뒤 `superclaude install --force --scope local`을 실행한다.
  - `diff src/superclaude/output-styles/plain-language.md .claude/output-styles/plain-language.md`의 출력이 없어야 한다.
  - 이 문서를 `status: complete`로 바꾸고 커밋한다.

## 중단 경로

A와 B 모두 실패하면 05-plan과 같은 실패 절차를 따른다. src를 되돌리고, 수치와 실패 사실만 커밋한 뒤 멈춘다. 시도는 최대 3회다(A, A+B, 단어 한도 안의 재작성 1회).

## 범위 밖

- **구조:** 05-plan Phase 2는 열린 채로 둔다. 원인 분리 측정 결과(산문 지시의 누적 효과)는 `06-measurement.md`에 있다.
- **병합과 CHANGELOG:** `master` 병합, 푸시, CHANGELOG는 이 계획 밖이다. 사용자가 정한다.

## Deviations

(없음)
