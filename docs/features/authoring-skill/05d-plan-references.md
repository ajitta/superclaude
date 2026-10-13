---
status: draft
revised: 2026-10-13
---

# Phase D: 참고 파일

Index: [05-plan.md](./05-plan.md). 계약: [04-design.md](./04-design.md) C1(구성·규칙), C3(파일별 내용·유형 함정·description 기준), §6(형식 정책), [04b-design-common-pass.md](./04b-design-common-pass.md) §1–5, [03-analysis.md](./03-analysis.md) §2–3.4.

작성 규칙 (C1, 모두 테스트 또는 자기 검사로 확인):
- 독자는 SuperClaude를 설치한 사용자 프로젝트. 저장소 rules를 링크·import·인용하지 않는다 (D10, `install-tree-boundary`)
- 영어. 파일 맨 위 YAML frontmatter `sources:` 목록 (`url`, `retrieved: YYYY-MM-DD`)
- 참고 파일끼리 링크하지 않는다 (R2). 100줄 넘으면 맨 위 목차 (R3)
- 예시는 `<example>` 요소로 감싸고, 넣는 파일은 서로 다른 경우를 덮는 3–5개, 아니면 0개 (D11)
- 모델 버전 번호는 `quality.md` "Model differences" 표에만 (C1)
- 03의 이 저장소 사례(파일 경로·줄 번호)는 옮기지 않는다. 범주와 판정 질문만 일반화해 옮긴다 (00-intent: 이 저장소는 작업 대상이 아님)

### Task D1: 실패하는 테스트

**Files:** Create: `tests/unit/test_sc_author_skill.py`

- [ ] Step 1: 존재와 출처
  - `REFS = ["skill.md", "agent.md", "command.md", "output-style.md", "memory.md", "format-xml.md", "quality.md"]`가 `src/superclaude/skills/sc-author/references/`에 모두 있음
  - 각 파일 frontmatter `sources`: 비어 있지 않음, 항목마다 `url`이 `https://`, `retrieved`가 `YYYY-MM-DD`
- [ ] Step 2: 최신성 (D12, C7 "가이드 최신성")
  - `_prompt_model_ids()`: `src/superclaude/commands/prompt.md`에서 `→ '(claude-[a-z0-9-]+)'` 전부 → 지금 `{claude-opus-5-5, claude-sonnet-5-5, claude-opus-5, claude-fable-5-1}`
  - `_quality_model_ids()`: `quality.md`의 `## Model differences` 절 표 첫 칸에서 `claude-[a-z0-9-]+`
  - 두 집합이 같음. 실패 메시지: "/sc:prompt supports a model quality.md has no row for (or the reverse) — re-read that model's prompting guide and update the row and its sources date"
  - 날짜 경과로는 red가 되지 않는다 (C7)
- [ ] Step 3: 예시 개수 (D11): 코드 펜스를 가린 뒤 `<example` 여는 태그 수 ∈ {0, 3, 4, 5}, 파일마다
- [ ] Step 4: 판단 항목 (D17, C7 "누락 0"): `quality.md`에 헤딩 `Load set`, `Judgment questions`, `Keep`, `Harm`, `Model differences`, `Removal evidence`가 모두 있음
- [ ] Step 5: 자기 검사: 각 참고 `.md`에 `author_check.check(path, type_="generic")` → error 0
- [ ] Step 6: `uv run pytest tests/unit/test_sc_author_skill.py -v` → FAIL

### Task D2: 외부 가이드 재조회 (D12)

- [ ] Step 7: 아래를 다시 읽고 조회일을 기록한다. 읽은 내용과 04-design의 결정이 다르면 문서를 따르고 `## Deviations`에 기록
  - Skill authoring best practices: `platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`
  - Claude Code: `code.claude.com/docs/en/{skills,sub-agents,output-styles,memory}`
  - Prompting best practices: `platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices`
  - 모델별: `…/prompt-engineering/prompting-claude-opus-5-5`, `…/prompting-claude-sonnet-5-5`, `…/prompting-claude-fable-5-1`. Opus 5는 `claude-api` 스킬 model-migration reference의 `## Migrating to Claude Opus 5` 절 (`/sc:prompt`와 같은 출처)

### Task D3: 유형 참고 5개

**Files:** Create: `src/superclaude/skills/sc-author/references/{skill,agent,command,output-style,memory}.md`

- [ ] Step 8: 파일마다 세 절 (C3 `<type>.md` 행)
  - `When to use this type`: 다른 유형과 구분하는 한두 줄
  - `Template (md)`: 코드 펜스 안의 md 본문 템플릿. frontmatter는 `fields.yaml`의 `required` + 흔히 쓰는 `optional`만 (§6 표: skill = 헤딩 + 번호 목록 절차, agent = 헤딩 + 역할·경계 섹션, command = skill과 같음, output-style = 일반 산문, memory = 헤딩 + 불릿)
  - `Pitfalls`: C3 "유형 함정"의 해당 줄을 사용자 문서용 문장으로
- [ ] Step 9: `skill.md`에 description 작성 기준 (C3 마지막 문단: 능력은 몇 단어, 트리거는 구체적으로, 절차 요약 없음, 대문자 강조 없음)
- [ ] Step 10: `command.md` 첫 절: `.claude/commands/`는 legacy이고 새 작업은 skill 권장 (C2 Resolve의 안내 문구와 같은 뜻)
- [ ] Step 11: `memory.md`에 load 방식 요약 한 줄과 "AGENTS.md는 CLAUDE.md가 없을 때만 읽힘", "rules frontmatter는 `paths`만 읽힘", "강제가 필요하면 hook"

### Task D4: `format-xml.md`

**Files:** Create: `src/superclaude/skills/sc-author/references/format-xml.md`

- [ ] Step 12: XML 본문 규칙을 검사기 코드와 같은 순서로 산문화: 루트 하나(X1, memory의 `@path` 줄·HTML 주석 예외), 태그 짝(X2), `snake_case`(X3), 4단 이하(X4), `<example>` 밖 헤더 금지(X5), `<should>`·`<avoid>` 금지와 이유(X6), output-style 제외(X7). 산문 속 `<3` 같은 표기는 태그가 아님
- [ ] Step 13: skill·agent·command·memory 골격 4개를 코드 펜스로. memory 골격은 `@path` 줄 + 루트 하나, rules·import되는 파일은 루트만 (§6)
- [ ] Step 14: 형식 전환은 문장을 지우지 않는다는 불변식 한 줄 (§6, 04b §1)

### Task D5: `quality.md`

**Files:** Create: `src/superclaude/skills/sc-author/references/quality.md`

- [ ] Step 15: 절 구성 (C3 `quality.md` 행 순서). 100줄을 넘을 것이므로 맨 위 목차
  - Deletion test, Trigger and description, Procedure vs reference, Strong terms, Durability, Reasons over emphasis, Positive phrasing, Consistent terms, Examples (3–5, D11)
  - `Load set` (D15): 04b §3 판정 표를 사용자 프로젝트용으로 (항상 로드, `paths:` 일치, 서브에이전트, 호출 시 로드, 메모리 색인) + 읽는 쪽(Claude | 다른 하네스)
  - `Judgment questions` (D17): 04b §5 판정 질문 4개, 각 질문에 "답이 무엇이면 no-op 후보" 한 줄
  - `Keep`: 03 §3.3 반례 유형 5개 (구체 사례 없이 범주와 이유)
  - `Harm`: 03 §3.4 네 범주, 보고 맨 앞에 둔다는 규칙
  - `Removal evidence`: 기계 후보는 `path:line: CODE` 인용, 판단 후보는 질문 + 답 + 근거(하네스 원문, Model differences 행, A/B 프로브 중 하나). 승인 전에는 후보
  - `Model differences` (D12): 표, 행 = 모델 ID 4개 (`claude-opus-5-5`, `claude-sonnet-5-5`, `claude-opus-5`, `claude-fable-5-1`), 열 = "기본 동작 재진술" 판정에 쓰는 축(예: 자기 검증 문구, 범위 확장 경향, 진행 보고, 서식). 칸마다 D2에서 읽은 가이드의 내용만 쓰고 출처 URL은 frontmatter `sources`에
- [ ] Step 16: 감사 체크리스트 표 (C3 "감사 체크리스트"): 항목 → 질문 한 줄

### Task D6: 검증과 커밋

- [ ] Step 17: `uv run pytest tests/unit/test_sc_author_skill.py -v` → PASS
- [ ] Step 18: 파일마다 `uv run superclaude author-check src/superclaude/skills/sc-author/references/<file>.md --type generic` → exit 0
- [ ] Step 19: `make format && make lint && uv run pytest` → 모두 exit 0 (`test_shipped_content_server_neutral.py` 포함)
- [ ] Step 20: 커밋 `feat(sc-author): add the type, XML format and quality references`
