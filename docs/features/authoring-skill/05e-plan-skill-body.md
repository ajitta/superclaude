---
status: complete
revised: 2026-10-13
---

# Phase E: `SKILL.md`

Index: [05-plan.md](./05-plan.md). 계약: [04-design.md](./04-design.md) C2(frontmatter 표, description 초안, 본문 절차 1–7), §3.2(흐름, Check 상한 3), [04b-design-common-pass.md](./04b-design-common-pass.md) §1–3.

### Task E1: 실패하는 테스트

**Files:** Modify: `tests/unit/test_sc_author_skill.py`

- [x] Step 1: frontmatter (`yaml.safe_load`)
  - `name == "sc-author"`, `disable-model-invocation is True` (D4)
  - `allowed-tools`에 `Bash(superclaude author-check *)`와 `PowerShell(superclaude author-check *)` (05-plan §9 미결 해소)
  - `argument-hint` 있음, `description` ≤1,536자이고 1·2인칭으로 시작하지 않음
- [x] Step 2: 본문
  - 150줄 이하 (C1 목표)
  - 번호 단계가 이 라벨로 이 순서: `Resolve`, `Load-set`, `Load`, `Draft`, `Neighbors`, `Check`, `Hand-off` (`Draft | Audit`는 `Draft`로 시작)
  - D1의 `REFS` 전부와 `fields.yaml`이 `${CLAUDE_SKILL_DIR}/references/<file>` 형태로 링크됨 (C1 "참조 깊이 1단계")
  - `superclaude author-check` 명령 줄에 `--with`가 있음 (D15가 검사기에 닿는 유일한 길)
- [x] Step 3: 자기 검사 (C7 "스킬 구조"): `author_check.check(SKILL.md)` → 유형 추론 skill, error 0
- [x] Step 4: `uv run pytest tests/unit/test_sc_author_skill.py -v` → 새 테스트 FAIL

### Task E2: 본문 작성

**Files:** Create: `src/superclaude/skills/sc-author/SKILL.md`

- [x] Step 5: frontmatter: C2 표 그대로, description은 C2 초안 (영어). Step 1 조건을 맞춘다
- [x] Step 6: 본문 절차 (C2 1–7, 각 단계는 라벨로 시작하는 번호 목록. 판단 기준은 참고 파일로 넘기고 본문에는 절차만)
  1. Resolve: type(인자 → 문맥 → 모호하면 질문, 5종 밖이면 `generic`), path(`fields.yaml` `location` + scope, 기본 project), format(`--xml`|`--md`|미지정 → 기존 파일은 현재 형식, 새 파일은 md). `command` + 새 파일 → skill 권장 안내 후 선택받기. `--xml` + output-style → md로 진행하고 이유 한 줄
  2. Load-set: `quality.md` "Load set"으로 함께 로드되는 문서와 읽는 쪽을 정해 한 줄로 보여 줌. 이 목록이 N3·N4의 유일한 입력이라는 이유를 한 줄로 (04b §7)
  3. Load: `references/<type>.md`(generic이면 없음) + `quality.md` + (xml이면) `format-xml.md` + 프로젝트의 같은 유형 기존 문서 1–2개(있으면, D19). 맞출 관례(언어, 용어, 헤딩/태그 모양, 섹션 구성)를 한 줄로 보여 줌
  4. Draft | Audit → 공통 pass: 새 문서는 프로젝트 관례로 쓰고 템플릿은 같은 유형 문서가 없을 때만 (D19). 재형식화(아무것도 지우지 않음) → 후보 수집(검사기 N + `quality.md` Judgment questions) → 보고 순서 Harm → 기계 후보 → 판단 후보 → diff → 승인 후 쓰기. 코드 안 문구(hook 주입 문자열 등)는 판단 항목만 (04b §2)
  5. Neighbors: 컨텍스트에 이미 있는 스킬·에이전트 목록으로 이름·트리거 겹침 확인, 파일은 읽지 않음
  6. Check: `superclaude author-check <path> --type <t> --format <f> --with <load-set …>` → error 수정 → 재실행, 상한 3회. 넘으면 남은 error를 보고하고 멈춤. 명령이 없으면(`command not found`) 기계 검사를 하지 않았다고 Hand-off에 쓴다
  7. Hand-off: 새 세션 시험 프롬프트 2–3개 (발동해야 할 것 1–2 + 비슷하지만 발동하면 안 되는 것 1). 명시 호출 전용 문서면 호출 예시만. 기계 검사를 못 한 항목을 밝힘
- [x] Step 7: 참고 파일 목록 절: 파일마다 "언제 읽나" 한 줄 (C3 "읽는 시점" 열)

### Task E3: 검증과 커밋

- [x] Step 8: `uv run pytest tests/unit/test_sc_author_skill.py tests/integration/test_cross_directory_refs.py -v` → PASS (`TestSkillAgentRouting`이 이제 SKILL.md 하나를 순회함)
- [x] Step 9: `uv run superclaude author-check src/superclaude/skills/sc-author/SKILL.md` → exit 0. R2(참고 파일끼리 링크)·R3(목차) warning이 있으면 D의 파일을 고친다
- [x] Step 10: `make format && make lint && uv run pytest` → 모두 exit 0
- [x] Step 11: 커밋 `feat(sc-author): add the sc-author skill procedure`

## Deviations

- description은 C2 초안("Write or revise …")을 3인칭("Writes or revises …")으로 바꿈: skill best practices "Always write in third person". 본문 내용은 같음
- Step 9: 자기 검사 `0 errors, 0 warnings` — R2·R3 수정 불필요
