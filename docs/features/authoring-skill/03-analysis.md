---
status: complete
revised: 2026-10-14
---

# `sc-author` 분석 — no-op 판정 기준

유형: analysis. 목적: 04-design.md §9 남은 미결 "no-op 판정 기준과 근거"의 입력. 2026-10-13 사용자: "지금 이 프로젝트의 rules, claude.md, agent.md, 메모리 내용만 봐도 NO-OP의 가능성이 있는 지시가 많아."

이 저장소 문서는 표본일 뿐 sc-author의 작업 대상이 아니다 (00-intent.md 범위 밖). 아무 파일도 고치지 않았다.

## 1. 방법

| 묶음 | 범위 | 후보 |
|---|---|---|
| A | `.claude/rules/*.md`, `schemas.yaml`, `gotchas/*.md` | 15 (+2 낮음) |
| B | `CLAUDE.md`, `AGENTS.md`, core `FLAGS`·`PRINCIPLES`·`RULES`, agent 5개 | 18 |
| C | auto memory `MEMORY.md` + 메모 파일 27개 | 16 |

- 정의: 지우면 Claude(Opus 5.5, Sonnet 5.5, Fable 5.1)의 행동이 바뀌지 않는 문장
- 세 에이전트가 읽기 전용으로 조사하고, 인용된 위치를 본 세션에서 다시 확인함
- 다시 확인에서 틀린 것 1건: C의 "MEMORY.md authoring-skill 줄이 `e6eccd37`" — 실제로는 이미 `1f55b9a5`. 조사 결과도 검증 없이 쓰면 안 된다는 사례

## 2. 먼저 정할 것: 로드 집합

같은 문장이라도 누가, 무엇과 함께 읽느냐에 따라 no-op 여부가 바뀐다.

| 로드 방식 | 함께 읽히는 것 | 예 |
|---|---|---|
| 항상 | CLAUDE.md → AGENTS.md, `@import` 체인, `paths:` 없는 rules | `AGENTS.md:40`과 `gotchas/general.md:6`(context-leak)은 둘 다 항상 로드 → 중복 |
| `paths:` 일치 시 | 같은 경로에 걸리는 rules 전부 | `xml-prose-format.md`의 `paths:`가 agents·commands·modes·mcp·core를 덮음 → 각 `*-authoring.md`의 "Inherited" 절과 동시 로드 → 중복 |
| 서브에이전트 | 그 agent 본문만 | 모든 agent의 같은 `<memory_guide>` 머리말은 중복 아님 |
| 읽는 쪽이 다름 | Claude는 자동 로드, Codex는 AGENTS.md만 | `AGENTS.md:35` "other agents read general.md"는 Claude에겐 no-op, Codex에겐 유일한 경로 |
| 비용 | 메모리 색인 줄은 매 턴, 본문은 열 때만 | 색인 기준: "파일을 열지 않는 세션에서 이 줄이 행동을 바꾸나?" |

## 3. 판정 기준

### 3.1 기계로 잡히는 것

문장이 가리키는 대상을 하나씩 확인한다 (경로, 테스트 이름, 커밋 ID, 도구·MCP 이름, 용어). A에서 15건 중 5건이 이 방법으로 나왔다.

| 분류 | 확인 방법 | 사례 |
|---|---|---|
| 없어진 대상 (sediment) | `ls`, `git cat-file`, grep | `mcp-authoring.md:80,91` Context7 (`src/superclaude/mcp/`에 없음) · `project-manager.md:46` "update checksums" (`src/` 전체에서 이 줄뿐) · 메모리 serena-followups "PR-A, PR-B still queued" (Serena 제거됨) · `feedback_pm-agent.md` "5 skills" |
| 가리키는 곳이 없음 | 인용한 파일·커밋 안에서 주장한 내용 grep | `mode-authoring.md:30` "per xml-prose-format.md" (해당 내용 0건) · `S390` 커밋 (유효한 객체 아님) · `mode-authoring.md:106` 검증한다는 테스트가 그 파일을 glob하지 않음 |
| 실행할 수 없음 | 지시가 쓰라는 도구 ↔ frontmatter `tools` | `simplicity-guide.md:55,58` Context7 호출 지시, `tools: Read, Grep, Glob, Agent` |
| 로드 집합 안 중복 | §2 집합 안에서 문장 비교 | `PRINCIPLES.md:13` ↔ `RULES.md:15` · agent의 `<tool_guidance>` Never ↔ `<bounds>` `<never>` (템플릿이 두 칸을 다 요구해서 생김) |
| 모순 | 같은 대상이 반대 칸에 | `business-panel-experts.md:51-52` 같은 행동이 Ask First와 Never에 동시 · `agent-authoring.md:57` "longer description … cost nothing" ↔ `content-quality.md:15,80` · `AGENTS.md:7` "never `python -m pytest`" ↔ `:14` 대체 경로 `.venv/Scripts/python.exe -m pytest` |
| 끝난 이력 (메모리) | 상태어(CLOSED, RELEASED, nothing open) + 행동 지침 없음 | `MEMORY.md` 약 6줄 |
| 다시 만들 수 있는 값 | 해시·개수·"latest vX" 정규식 | 메모리 본문의 커밋 범위, 버전 |

### 3.2 판단이 필요한 것

| 분류 | 판정 질문 | 사례 |
|---|---|---|
| 기본 동작 재진술 | 하네스·모델이 시키지 않아도 하는가? 근거는 하네스 프롬프트·도구 설명 원문 또는 A/B 프로브 | `PRINCIPLES.md:10` Parallel-Thinking (시스템 프롬프트가 이미 지시) · `agent-authoring.md:131` cd 유지 안 됨 (서브에이전트 머리말에 있음) · 메모리 bash heredoc (Bash 도구 설명에 들어감) |
| 막연함 | 관찰 가능한 트리거, 구체적 대상, 임계값이 있는가? | `PRINCIPLES.md:12` "keep project understanding" · `gotchas/general.md:7` compaction-drift (스스로 감지 못함) · `FLAGS.md:33` "risk >0.7" (계산하는 곳 없음) |
| 다른 곳에서 강제 | 강제 장치가 작성자의 평소 루프에서, 실수 비용이 생기기 전에 돌고, 실패 메시지가 고칠 방법을 말하는가? 모두 예일 때만 no-op | `mode-authoring.md:14-26` frontmatter 금지 (테스트 2개) · 반례: `AGENTS.md:20` make lint (CI는 푸시 뒤에 돔) |
| 사실·이유 | 이 사실로 바뀌는 작성 결정이 있는가? | `agent-authoring.md:95` effort 우선순위 (결정 안 바뀜) · 반례: `agent-authoring.md:12` 서브에이전트는 본문만 받음 (본문에 무엇을 넣을지 바뀜) |

판정 단위는 규칙이 아니라 문장이다: `RULES.md:29` 첫 문장은 하네스가 이미 하는 말이지만 둘째 문장(gotcha 캡처)은 행동을 더한다.

### 3.3 no-op처럼 보이지만 남기는 것

| 유형 | 사례 |
|---|---|
| 예측 가능한 제안을 막는 "아니오" 기록 | 메모리 fork-detached "'this fork' 문구 유지" · plain-language-structure "브랜치를 따로 merge·삭제하지 않음" |
| 기본 습관을 뒤집음 | `gotchas/general.md:8` 개념이 아닌 정확한 태그로 grep |
| 모델이 알 수 없는 하네스 특이점 | `gotchas/general.md:14` Grep content 모드가 긴 줄을 숨김 |
| 남은 흔적을 오해하지 않게 함 | 메모리 beads-removed (`.beads/` 테스트 fixture) |
| 근거 위치만 낡음 | 메모리 verify-subagent-claims (줄 번호는 옛것, 규칙은 유효) — 위치를 고치고 문장은 남김 |

### 3.4 해로움 검사

낡은 문장은 no-op보다 나쁠 때가 많다. 따로 분류하고 먼저 처리한다.

- 잘못된 작업을 부름: serena-followups "PR-A, PR-B still queued"
- 실행하지 않은 확인을 했다고 말하게 함: simplicity-guide Context7
- 둘 중 하나가 늘 틀림: 모순 3건 (§3.1)
- 출처를 믿게 함: 가리키는 곳이 없는 인용 3건

## 4. 설계에 주는 것 (04-design.md §9 입력)

1. Resolve 다음에 "로드 집합" 단계: 이 문서가 어떻게 읽히는지(항상, `paths:`, `@import`, 서브에이전트 본문, 메모리 색인)와 함께 읽히는 문서를 먼저 정한다. 중복 판정은 그 집합 안에서만 한다
2. 검사기에 넣을 수 있는 것 (§3.1): 대상 확인(경로·커밋·테스트 이름·용어), 지시 도구 ↔ `tools`, 같은 대상의 반대 칸, 메모리 색인 상태어, 로드 집합 안 문장 중복
3. 판단에 맡길 것 (§3.2): `quality.md` 체크리스트의 판정 질문으로. 기본 동작 재진술은 모델에 따라 답이 달라지므로 D12 "모델별 차이"를 근거로 삼는다
4. 제거 근거: 기계 판정은 실패한 확인 결과를 그대로 보여 준다. 판단 판정은 후보로 내고 diff 승인(C2 3단계)에서 사용자가 고른다. 해로움(§3.4)은 맨 앞에
5. 남길 것(§3.3)을 지우지 않도록 `quality.md`에 반례 유형을 함께 둔다
