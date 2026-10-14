---
status: draft
revised: 2026-10-14
---

# 규칙 번호 인용 일관화 Implementation Plan

**Goal:** 배포 콘텐츠의 규칙 인용을 `[RNN Name]` 한 형식으로 맞추고 테스트가 다른 형식을 막게 한다. 커널과 RULES_QUALITY에 두 벌로 있는 규칙 5개는 RULES_QUALITY 쪽을 "커널 참조 + 커널에 없는 내용"으로 줄인다.

**Architecture:** 콘텐츠 마크다운 약 20곳을 손으로 고친다. `tests/unit/test_cross_references.py`의 규칙 인용 테스트는 번호만 쓴 인용을 예외 세 가지 밖에서 실패로 바꾸고, 괄호 이름 검사(Title Case 판별)는 지운다. RULES_QUALITY의 R06·R15·R18·R19·R20 정의 줄은 태그를 남긴 채 본문만 줄인다. hook 코드와 context_loader는 바꾸지 않는다.

**Tech Stack:** Markdown 콘텐츠, pytest, ruff.

줄 번호는 master `13ff23c0` + 브랜치 `test/rule-citation-scope`(커밋 전) 기준이다. 앞 task의 편집으로 밀릴 수 있으니 각 task는 grep으로 위치를 다시 잡는다.

## 근거 (2026-10-14 측정)

- 정의: `core/rules/RULES_QUALITY.md:8-21`에 14개(R01, R02, R03, R06, R12~R21). R04·R05·R07~R11은 정의도 인용도 없다.
- 인용 형식 7가지: `[R06 Scope]`(번호+이름), `R18`(문장 속), `(R01)`(괄호 안), `R06 (Scope)`(괄호 이름), `[R20]`(이름 없는 대괄호), `note="Enforcement: R15 — …"`(속성 안), `R01–R21`(범위).
- 인용이 차지하는 양: 37개 파일 합계 약 1.4KB, 파일당 0.9~3.1%. 형식을 바꿔도 컨텍스트는 거의 달라지지 않는다. 형식 통일의 목적은 읽는 쪽의 해석과 테스트 강도다.
- 정의가 없는 자리의 번호: 항상 읽히는 `core/PRINCIPLES.md`가 R01·R03·R12·R13을 번호로만 인용한다. 이 넷은 커널(`core/RULES.md`)에 없고 RULES_QUALITY에만 정의된다. RULES_QUALITY는 `scripts/context_loader.py:168-171` 패턴(/sc:implement 등)에서만 주입되므로, 그 밖의 세션에서 이 번호는 뜻이 없다.
- 중복: 커널의 `<scope_discipline>`·`<verification_before_completion>`·`<project_rules_priority>`가 R06·R18·R15·R20·R19를 1,559바이트로 서술하고, RULES_QUALITY가 같은 5개를 1,675바이트로 다시 서술한다. RULES_QUALITY가 주입되는 세션에는 둘 다 실린다. `.claude/rules/content-quality.md` 4절 Duplication("one answer location per rule")에 걸린다.
- 이 5줄 중 커널에 없는 내용(R15의 "verification not possible", R18의 요구 근거와 post-MVP 허용, R19의 형식·승인·예외, R20의 기준·예시·skip 목록)은 남겨야 한다. 줄 단위로 따지면 줄어드는 양은 약 0.5KB다(제안 당시 1KB로 말한 것을 바로잡음). 정확한 값은 Task 2.1이 측정한다.
- 이 문구를 고정하는 테스트·eval은 없다(`grep -rnE "YAGNI|unsolicited files|post-MVP|verification not possible|convergence detection|Is system broken" tests/ evals/` 0건).

## 결정

- 표준 형식: `[RNN Name]`. 번호만 쓰는 형식은 아래 예외에서만 허용한다.
  1. `core/rules/RULES_QUALITY.md` 안의 번호: 정의가 있는 파일이라 같은 화면에 이름이 있다(:13 "R12's ask-first branch", :21, :82, :91).
  2. 범위 `RNN–RNN`: 목록 전체를 가리키는 표기다(`ARCHITECTURE.md:32`, `commands/analyze.md:52`, `core/README.md:18`, `core/RULES.md:37`).
  3. `commands/insight.md:53`의 `rule (R13, R18...)`: insights.jsonl `rule` 필드에 실제로 저장되는 값 형식이다(`.claude/insights.jsonl`의 값이 `"R18"` 형태).
- 중복 정리는 방법 A(RULES_QUALITY 쪽을 줄임)로 한다. 항상 읽히는 커널은 키우지 않는다.

## 범위 밖

- insights.jsonl `rule` 필드(번호만)와 R14 `violated_rule`(`[RNN Name]`)의 기록 형식 차이. 저장 데이터 형식이라 별도 결정이 필요하다. 기존 데이터에 정의 없는 `R10`이 1건 있다.
- 비어 있는 번호(R04, R05, R07~R11)의 재번호. `violated_rule`·insights 기록이 번호에 묶여 있어 다시 매기면 과거 기록이 틀어진다.
- `.claude/rules/`(레포 전용 규칙)와 `docs/`의 인용. 배포 콘텐츠가 아니다.
- 30KB 경계 표기(`scripts/README.md:22`, `hooks/hooks.json:82`의 ">30KB" vs 코드 `>=`).

## Phase 0: 선행 조건과 브랜치

- [ ] `test/rule-citation-scope`(규칙 인용 테스트를 `src/superclaude` 전체로 확장, 괄호 이름 검사 추가)를 커밋하고 master에 병합한다. 이 계획의 Task 1.1이 그 테스트를 고친다.
- [ ] master에서 `git switch -c refactor/rule-citations`.

## Phase 1: 인용 형식 통일 (커밋 1개)

### Task 1.1: 테스트를 먼저 엄격하게 (red)

**Files:** `tests/unit/test_cross_references.py` (`test_rule_citations_defined`, `_PAREN_NAME`)

- [ ] Step 1: 번호만 쓴 인용을 결정의 예외 세 가지 밖에서 실패로 바꾼다.
  - 예외 1은 파일 경로로(`core/rules/RULES_QUALITY.md`), 예외 2는 범위 정규식 `R\d{2}[–-]R\d{2}`를 먼저 지워서, 예외 3은 `{"commands/insight.md": ["rule (R13, R18...)"]}` 허용 목록으로 처리한다.
  - 번호+이름 검사(`[RNN Name]`이 정의와 일치)는 유지한다. 예외 1 파일 안의 번호도 정의된 번호여야 한다는 검사는 유지한다.
- [ ] Step 2: `_PAREN_NAME`과 `bad_names`를 지운다. 괄호 이름 5곳은 Task 1.2에서 `[RNN Name]`으로 바뀌므로 필요 없다.
- [ ] Step 3: `uv run pytest tests/unit/test_cross_references.py -q -k rule` → 실패 목록이 Task 1.2의 파일 목록과 같은지 확인한다.

### Task 1.2: 콘텐츠를 표준 형식으로 (green)

**Files:** 아래 표. 각 줄은 바뀌는 인용만 적는다.

| 파일:줄 | 지금 | 바꾼 뒤 |
|---|---|---|
| `core/PRINCIPLES.md:8` | `(R01)` | `([R01 Workflow])` |
| `core/PRINCIPLES.md:11` | `(R12/R13)` | `([R12 Clarification]/[R13 Intent Verification])` |
| `core/PRINCIPLES.md:32` | `(R03 — full chain: …)` | `([R03 Diagnosis] — full chain: …)` |
| `core/FLAGS.md:30` | `(R20)` | `([R20 Success Criteria])` |
| `commands/design.md:67` | `Apply R18 necessity test` | `Apply [R18 Necessity Test]` |
| `commands/implement.md:54` | `Run R02 status check` | `Run [R02 Status Check]` |
| `commands/improve.md:37` | `Apply R18 before` | `Apply [R18 Necessity Test] before` |
| `commands/spec-panel.md:68` | `apply R18 to` | `apply [R18 Necessity Test] to` |
| `core/rules/RULES_DELEGATION.md:45` | `[R20]` | `[R20 Success Criteria]` |
| `core/rules/RULES_DELEGATION.md:47` | `the same R15 risk` | `the same [R15 Verification] risk` |
| `core/rules/RULES_DELEGATION.md:54` | `(R15 gates resume)` | `([R15 Verification] gates resume)` |
| `core/rules/RULES_DELEGATION.md:55` | `an R15 'claimed done…'` | `a [R15 Verification] 'claimed done…'` |
| `core/rules/RULES_DOCS.md:42` | `[R19]` | `[R19 Project Gotcha Capture]` |
| `core/rules/RULES_QUALITY.md:42` | `R06 (Scope) + R18 (Necessity Test)` | `[R06 Scope] + [R18 Necessity Test]` |
| `core/rules/RULES_QUALITY.md:94` | `R12 (Clarification) + R13 (…) + R14 (…)` | `[R12 Clarification] + [R13 Intent Verification] + [R14 Correction Capture]` |
| `commands/analyze.md:53` | `` grep `violated_rule: "[RXX]"` `` | `` grep `violated_rule: "[RNN Name]"` `` (R14가 정한 기록 형식) |
| `commands/analyze.md:58` | `follow [R14 Correction Capture] Correction Capture format` | `follow the [R14 Correction Capture] format` |

- [ ] Step 1: 표대로 고친다. XML 속성 값(`note="…"`) 안의 대괄호는 그대로 둬도 파싱에 문제가 없는지 `uv run pytest tests/unit/test_content_structure.py -q`로 확인한다.
- [ ] Step 2: `uv run pytest tests/unit/test_cross_references.py -q -k rule` → 전부 통과.
- [ ] Step 3: 잡는지 확인. `commands/improve.md` 끝에 `Apply R18.`을 붙이면 실패하고, `[R06 Restraint]`도 실패하는지 본다. 확인 뒤 `git checkout -- src/superclaude/commands/improve.md`.
- [ ] Step 4: `uv run pytest` exit 0, `make format`, `make lint`. 커밋 `refactor(content): cite rules as [RNN Name] everywhere`.

## Phase 2: 커널과 RULES_QUALITY 중복 정리 (커밋 1개)

### Task 2.1: RULES_QUALITY의 5줄을 커널 참조 + 차이로

**Files:** `src/superclaude/core/rules/RULES_QUALITY.md:11,15,18,19,20`

- [ ] Step 1: 줄이기 전 크기를 기록한다. `wc -c src/superclaude/core/rules/RULES_QUALITY.md`.
- [ ] Step 2: 각 줄을 `[RNN Name] 🔴|🟡: kernel <섹션 이름> + <커널에 없는 내용>` 형식으로 줄인다. 태그(`[RNN Name]`)와 중요도 표시는 그대로 둔다. 테스트가 정의를 이 줄에서 읽고, R14 `violated_rule`과 `/sc:analyze --focus rules`가 이 태그를 쓴다.
  - R06 → `kernel <scope_discipline>`; 남길 것: `0 unsolicited files, 0 adjacent refactors`
  - R15 → `kernel <verification_before_completion>`; 남길 것: `<verification_ladder>` 참조, `If unable to verify at all, state "verification not possible: [reason]"`
  - R18 → `kernel <scope_discipline>`; 남길 것: `Require: specific failure scenario, quantitative evidence, or user-facing impact. "Deferred to post-MVP review" is valid design decision`
  - R19 → `kernel <project_rules_priority>`; 남길 것: 같은 발견이 두 번째일 때, 형식 `name: description`, 없으면 `paths:` frontmatter로 생성, 사용자 승인, 애매하면 project, framework `<gotchas>`에 있으면 skip
  - R20 → `kernel <verification_before_completion>`; 남길 것: `>3 steps or ambiguous outcome` 기준, 예시 3개, `--loop` 수렴 판정, skip 목록
- [ ] Step 3: 줄인 뒤 크기를 다시 재고 차이를 커밋 본문에 적는다.
- [ ] Step 4: 커널 `core/RULES.md`는 바꾸지 않는다. `git diff --stat`에 `core/RULES.md`가 없어야 한다.
- [ ] Step 5: `uv run pytest` exit 0(특히 `tests/unit/test_context_loader.py`의 core-lite 가드), `make lint`. 커밋 `refactor(rules): RULES_QUALITY points to the kernel for rules it already states`.

## Risks

- `core/`가 바뀐다. 다음 릴리스 전에 `make canary-gates`가 필요하다(이미 v4.27.0 이후 core 변경으로 필요한 상태). Phase 2는 규칙 문구를 줄이므로 canary 결과를 이전과 비교한다.
- Phase 2에서 커널에 없는 내용을 잘못 지우면 RULES_QUALITY가 주입되는 세션에서 규칙 세부가 사라진다. Step 2의 "남길 것" 목록을 지운 줄과 대조해 리뷰한다.
- 표준 형식은 인용마다 약 20바이트를 더한다. Phase 1 전체로 약 +400바이트, 항상 읽히는 `PRINCIPLES.md`·`FLAGS.md`는 합쳐 약 +130바이트다.

## 채택하지 않은 대안

- 번호만 쓰기로 통일: 전체 1KB 미만, 파일을 한 번 읽을 때 10~30바이트를 아낀다. 대신 정의가 없는 세션에서 뜻을 잃고, 테스트가 이름을 확인할 수 없다.
- 번호를 없애고 이름만 쓰기: R14 `violated_rule`, insights `rule`, `/sc:analyze --focus rules` 집계가 번호에 묶여 있어 함께 깨진다.
- 중복 정리 방법 B(5개 규칙의 정의를 커널로 옮기고 RULES_QUALITY에서 삭제): RULES_QUALITY 세션은 약 1.6KB를 아끼지만, 커널에 없던 세부(약 1KB)가 항상 읽히는 파일로 옮겨져 모든 세션이 그만큼 커진다. 커널 상한(`KERNEL_CHAR_BUDGET = 7600`, 지금 4,144자)에는 들어가지만 비용을 세션 전체로 넓힌다.
- 괄호 이름 검사 유지: Phase 1 뒤에는 괄호 이름이 남지 않아, 대문자 판별 휴리스틱만 남는다.

## 완료 증명

- `uv run pytest` exit 0, `make lint` 통과.
- `uv run pytest tests/unit/test_cross_references.py -q -k rule` 통과, Task 1.2 Step 3의 두 가지 위반이 각각 실패로 잡힘.
- 예외 세 곳 밖에서 번호만 쓴 인용 0건: Task 1.1 테스트가 그 검사다.
- Phase 2 전후 `RULES_QUALITY.md` 바이트 수와 `core/RULES.md` 무변경(`git diff --stat master -- src/superclaude/core/RULES.md` 빈 출력).
